"""
AMLRuntime — простий інтерфейс для інтеграції AML у Python-проекти.

Функції:
- запуск AML-коду з рядка або файлу;
- зупинка (кооперативне скасування) поточного виконання;
- додавання/отримання змінних у рантаймі;
- дефолтні імпорти модулів (Python та AML);
- налаштування шляхів імпорту для AML та Python модулів;
- виклик AML-функцій з Python.
"""

from typing import Any, List, Optional, Callable, Dict
import os
import threading
import types

from .lexer import Lexer
from .parser import Parser, ImportPy, ImportAml
from .interpreter import Interpreter, Function, Namespace, TaskHandle


class AMLRuntime:
    def __init__(
        self,
        default_py_modules: Optional[List[str]] = None,
        default_aml_modules: Optional[List[str]] = None,
        aml_search_paths: Optional[List[str]] = None,
        python_search_paths: Optional[List[str]] = None,
        use_cache: bool = True,
    ):
        """
        Ініціалізує рантайм AML із конфігурацією за замовчанням.

        - default_py_modules: список Python модулів для автозавантаження;
        - default_aml_modules: список AML модулів для автозавантаження;
        - aml_search_paths: додаткові шляхи пошуку AML файлів;
        - python_search_paths: додаткові шляхи для імпорту Python модулів;
        - use_cache: чи використовувати кешування AST (за замовчуванням True).
        """
        self.interpreter = Interpreter()
        self.default_py_modules = default_py_modules or []
        self.default_aml_modules = default_aml_modules or []
        self.use_cache = use_cache

        # Налаштування шляхів імпорту
        for p in (aml_search_paths or []):
            self.interpreter.add_aml_search_path(p)
        for p in (python_search_paths or []):
            self.interpreter.add_python_search_path(p)

        self._started = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        # Конфігурація мікро‑yield для операцій рантайму (доступи/присвоєння/снімки)
        self._yield_every_ops = 64
        self._yield_sleep_seconds = 0.0  # 0 => чистий yield через sleep(0)
        self._ops_counter = 0
        # Кеш метаданих для швидкого доступу через рантайм
        self._meta_cache: Dict[str, Any] = {}

    def configure_micro_yield(self, every: Optional[int] = None, sleep_seconds: Optional[float] = None) -> None:
        """Налаштовує мікро‑yield у рантаймі та синхронізує з інтерпретатором."""
        if every is not None and every > 0:
            self._yield_every_ops = int(every)
        if sleep_seconds is not None and sleep_seconds >= 0.0:
            self._yield_sleep_seconds = float(sleep_seconds)
        # Синхронізуємо з інтерпретатором для послідовної поведінки
        try:
            self.interpreter.configure_micro_yield(every=every, sleep_seconds=sleep_seconds)
        except Exception:
            pass

    def disable_micro_yield(self) -> None:
        """Вимикає мікро‑yield у рантаймі та інтерпретаторі."""
        self._yield_every_ops = 1 << 30
        self._yield_sleep_seconds = 0.0
        try:
            self.interpreter.disable_micro_yield()
        except Exception:
            pass

    def _maybe_yield(self) -> None:
        """Легкий мікро‑yield: викликається у гарячих циклах для зниження CPU."""
        self._ops_counter += 1
        thr = self._yield_every_ops
        if thr <= 0:
            return
        # Якщо thr — степінь 2, користуємось дешевою побітовою перевіркою
        is_pow2 = (thr & (thr - 1)) == 0
        should_yield = ((self._ops_counter & (thr - 1)) == 0) if is_pow2 else (self._ops_counter % thr == 0)
        if should_yield:
            import time
            if self._yield_sleep_seconds > 0.0:
                time.sleep(self._yield_sleep_seconds)
            else:
                time.sleep(0)

    # --------- Керування життєвим циклом ---------
    def start(self) -> None:
        """Запускає рантайм та виконує дефолтні імпорти модулів."""
        with self._lock:
            # Імпорт Python модулів за замовчанням
            if self.default_py_modules:
                stmt = ImportPy(self.default_py_modules)
                self.interpreter.execute_ImportPy(stmt)

            # Імпорт AML модулів за замовчанням
            if self.default_aml_modules:
                stmt = ImportAml(self.default_aml_modules)
                self.interpreter.execute_ImportAml(stmt)

            self._started = True
            self.interpreter.reset_cancel()

    def stop(self) -> None:
        """Кооперативно зупиняє поточне виконання AML."""
        with self._lock:
            self.interpreter.cancel()
            self._started = False

    def is_running(self) -> bool:
        """Повертає стан запуску (логічний)."""
        t_alive = self._thread is not None and self._thread.is_alive()
        return (self._started and not self.interpreter.cancelled) or t_alive

    # --------- Виконання AML ---------
    def run_source(self, source: str) -> None:
        """Виконує AML-код із рядка у поточному середовищі."""
        with self._lock:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            program = parser.parse()

            self.interpreter.reset_cancel()
        # Інтерпретуємо поза замком, щоб stop() міг працювати
        try:
            try:
                self.interpreter.push_file_context('<string>', source)
                self.interpreter.interpret(program, source_text=source, file_path='<string>')
            finally:
                self.interpreter.pop_file_context()
            # Оновлюємо кеш метаданих після виконання верхнього рівня
            try:
                self._meta_cache = dict(self.interpreter.metadata)
            except Exception:
                pass
        except KeyboardInterrupt:
            # Кооперативне скасування та дружній лог
            with self._lock:
                self.interpreter.cancel()
            print("\nВиконання AML перервано користувачем (KeyboardInterrupt)")

    def run_file(self, file_path: str) -> None:
        """Зчитує та виконує AML-файл або зкомпільований .caml."""
        with self._lock:
            abs_path = os.path.abspath(file_path)
            
            # Перевірка чи це .caml файл
            if file_path.endswith('.caml'):
                entry_path = self.interpreter.load_caml(abs_path)
                program = self.interpreter.dict_to_ast(self.interpreter._caml_bundle[entry_path])
                source = "" # Source text might not be available for .caml
                abs_path = entry_path # Set abs_path to the original entry point path from bundle
            else:
                base_dir = os.path.dirname(abs_path)
                self.interpreter.add_aml_search_path(base_dir)

                program = None
                if self.use_cache:
                    # Спробувати завантажити через кеш інтерпретатора
                    try:
                        program = self.interpreter._load_ast(abs_path)
                    except Exception:
                        program = None
                
                # Якщо кеш вимкнено або виникла помилка при завантаженні кешу
                if program is None:
                    try:
                        with open(abs_path, 'r', encoding='utf-8') as f:
                            source = f.read()
                        
                        lexer = Lexer(source)
                        tokens = lexer.tokenize()
                        parser = Parser(tokens)
                        program = parser.parse()
                    except Exception as e:
                        raise RuntimeError(f"Не вдалося завантажити або розпарсити файл: {abs_path}\nПомилка: {e}")
                
                # Отримуємо вихідний код для контексту виконання
                try:
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                except Exception:
                    source = ""
        
        # Виконуємо без блокування замка, щоб дозволити stop() під час інтерпретації
        try:
            self.interpreter.reset_cancel()
            try:
                self.interpreter.push_file_context(abs_path, source)
                self.interpreter.interpret(program, source_text=source, file_path=abs_path)
            finally:
                self.interpreter.pop_file_context()
        except KeyboardInterrupt:
            with self._lock:
                self.interpreter.cancel()
            print("\nВиконання AML-файла перервано користувачем (KeyboardInterrupt)")

    # --------- Метадані ---------
    def get_metadata(self) -> Dict[str, Any]:
        """Повертає метадані сценарію AML (об'єднання з кешем)."""
        with self._lock:
            # Поєднуємо кеш та актуальні метадані з інтерпретатора
            out = {}
            try:
                out.update(self._meta_cache)
                out.update(self.interpreter.metadata)
            except Exception:
                out.update(self._meta_cache)
            return out

    def set_metadata(self, meta: Dict[str, Any]) -> None:
        """Встановлює метадані в рантайм та оточення AML (meta змінна).
        Якщо містить 'entry' або 'entrypoint' — конфігурує точку входу.
        """
        if not isinstance(meta, dict):
            raise RuntimeError("Очікується dict для метаданих")
        with self._lock:
            self._meta_cache.update(meta)
            try:
                # Оновити інтерпретатор та середовище
                self.interpreter.metadata.update(meta)
                self.interpreter.environment.define('meta', self.interpreter.metadata)
                entry = meta.get('entry') or meta.get('entrypoint')
                if isinstance(entry, str) and entry:
                    self.interpreter._entrypoint_name = entry
            except Exception:
                pass

    def set_entrypoint(self, entry: str) -> None:
        """Встановлює ім'я точки входу для автоматичного виклику."""
        if not isinstance(entry, str) or not entry:
            raise RuntimeError("Очікується непорожній рядок для імені точки входу")
        with self._lock:
            self.interpreter._entrypoint_name = entry

    def invoke_entrypoint(self) -> None:
        """Явно викликає точку входу, якщо вона задана."""
        with self._lock:
            if not getattr(self.interpreter, '_entrypoint_name', None):
                raise RuntimeError("Точка входу не налаштована")
        # Викликаємо поза замком, щоб уникати блокувань під час виконання
        self.interpreter._invoke_entrypoint()

    # --------- Паралельні виклики ---------
    def parallel_call(self, name: str, *args: Any, daemon: bool = True) -> TaskHandle:
        """Запускає функцію/метод AML або Python у окремому потоці.
        Повертає TaskHandle для очікування результату/помилки.
        """
        result_container: Dict[str, Any] = {'result': None, 'error': None}

        def _runner():
            try:
                res = self.call_function(name, *args)
                result_container['result'] = res
            except Exception as e:
                result_container['error'] = e

        t = threading.Thread(target=_runner, name=f"AMLRuntimeParallel:{name}", daemon=daemon)
        t.start()
        return TaskHandle(name, t, result_container)

        
    def parallel_calls(self, calls: List[tuple]) -> List[TaskHandle]:
        """Запускає список викликів у паралельних потоках.
        calls: [(name, *args), ...] або [(name, args_list), ...]
        """
        handles: List[TaskHandle] = []
        for item in calls:
            self._maybe_yield()
            if not isinstance(item, (list, tuple)) or len(item) == 0:
                continue
            name = item[0]
            args = []
            if len(item) == 2 and isinstance(item[1], (list, tuple)):
                args = list(item[1])
            elif len(item) > 1:
                args = list(item[1:])
            h = self.parallel_call(name, *args)
            handles.append(h)
        return handles

    def wait_all(self, handles: List[TaskHandle], timeout: Optional[float] = None) -> List[Any]:
        """Очікує завершення усіх паралельних задач і повертає результати."""
        results: List[Any] = []
        for h in handles:
            self._maybe_yield()
            try:
                results.append(h.join(timeout=timeout))
            except Exception:
                results.append(None)
        return results

    # --------- Асинхронне виконання в окремому потоці ---------
    def run_source_async(self, source: str, on_done: Optional[Callable[[], None]] = None, on_error: Optional[Callable[[Exception], None]] = None) -> threading.Thread:
        """Запускає виконання AML-коду з рядка у окремому потоці."""
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Виконання вже триває у потоці")

        def _worker():
            try:
                self.run_source(source)
                if on_done:
                    on_done()
            except KeyboardInterrupt:
                with self._lock:
                    self.interpreter.cancel()
                print("\nВиконання AML у потоці перервано користувачем (KeyboardInterrupt)")
                if on_error:
                    on_error(KeyboardInterrupt())
            except Exception as e:
                if on_error:
                    on_error(e)

        t = threading.Thread(target=_worker, name="AMLRuntimeThread", daemon=True)
        self._thread = t
        t.start()
        return t

    def run_file_async(self, file_path: str, on_done: Optional[Callable[[], None]] = None, on_error: Optional[Callable[[Exception], None]] = None) -> threading.Thread:
        """Запускає виконання AML-файла у окремому потоці."""
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Виконання вже триває у потоці")

        def _worker():
            try:
                self.run_file(file_path)
                if on_done:
                    on_done()
            except KeyboardInterrupt:
                with self._lock:
                    self.interpreter.cancel()
                print("\nВиконання AML-файла у потоці перервано користувачем (KeyboardInterrupt)")
                if on_error:
                    on_error(KeyboardInterrupt())
            except Exception as e:
                if on_error:
                    on_error(e)

        t = threading.Thread(target=_worker, name="AMLRuntimeThread", daemon=True)
        self._thread = t
        t.start()
        return t

    def join(self, timeout: Optional[float] = None) -> bool:
        """Очікує завершення поточного потоку виконання. Повертає True, якщо завершився."""
        if not self._thread:
            return True
        self._thread.join(timeout=timeout)
        return not self._thread.is_alive()

    # --------- Змінні рантайму ---------
    def set_variable(self, name: str, value: Any) -> None:
        """Встановлює змінну у поточному середовищі AML.
        Підтримує крапкові імена (namespace.attr) для встановлення атрибутів.
        """
        with self._lock:
            if '.' in name:
                self._assign_symbol(name, value, create_if_missing=True)
            else:
                self.interpreter.environment.define(name, value)

    def get_variable(self, name: str) -> Any:
        """Отримує змінну з поточного середовища AML.
        Підтримує крапкові імена (namespace.attr) для доступу до атрибутів.
        """
        with self._lock:
            if '.' in name:
                return self._resolve_symbol(name)
            return self.interpreter.environment.get(name)

    def override_variable(self, name: str, value: Any) -> None:
        """Перевизначає змінну: якщо існує — присвоює, якщо ні — створює."""
        with self._lock:
            if '.' in name:
                # Для крапкових шляхів працюємо з атрибутами/ключами напряму
                self._assign_symbol(name, value, create_if_missing=True)
            else:
                try:
                    # Перевіряємо існування
                    _ = self.interpreter.environment.get(name)
                    self.interpreter.environment.assign(name, value)
                except Exception:
                    self.interpreter.environment.define(name, value)

    def get_env_snapshot(self) -> dict:
        """Повертає копію поточного оточення змінних з розкритими namespace.
        Namespace відображаються як вкладені dict з їх атрибутами (рекурсивно).
        Приватні службові атрибути не включаються.
        """
        snap: Dict[str, Any] = {}
        env = self.interpreter.environment.values
        for k, v in env.items():
            self._maybe_yield()
            if isinstance(v, Namespace):
                snap[k] = self._namespace_to_dict(v)
            else:
                snap[k] = v
        return snap

    def print_env_snapshot(self, snapshot: Optional[Dict[str, Any]] = None, indent: int = 0) -> None:
        """Виводить відформатований знімок оточення у консоль.
        
        Якщо snapshot не передано, бере актуальний стан через get_env_snapshot().
        """
        if snapshot is None:
            snapshot = self.get_env_snapshot()
            print("\n=== AML Environment Snapshot ===")

        prefix = "  " * indent
        
        # Сортуємо ключі для стабільності виводу: спочатку звичайні змінні, потім функції, потім модулі/namespace
        keys = sorted(snapshot.keys())
        
        for key in keys:
            self._maybe_yield()
            val = snapshot[key]
            
            # Визначаємо тип та текстове представлення
            val_type = type(val).__name__
            val_str = ""
            
            if isinstance(val, dict):
                # Це вкладений Namespace (вже перетворений у dict через _namespace_to_dict)
                print(f"{prefix} {key} (Namespace):")
                self.print_env_snapshot(val, indent + 1)
                continue
            elif callable(val) or "Function" in val_type:
                # AML або Python функція
                val_str = f"func {key}(...)"
                print(f"{prefix} {val_str}")
            elif "module" in val_type:
                # Python модуль
                print(f"{prefix} {key} (Module)")
            else:
                # Звичайна змінна (str, int, float, list, etc.)
                repr_val = repr(val)
                if len(repr_val) > 100:
                    repr_val = repr_val[:97] + "..."
                print(f"{prefix}v {key} = {repr_val} ({val_type})")

        if indent == 0:
            print("================================\n")

    def _namespace_to_dict(self, ns: Namespace) -> Dict[str, Any]:
        """Повертає словник атрибутів Namespace (рекурсивно)."""
        out: Dict[str, Any] = {}
        # Використовуємо __dict__ для користувацьких атрибутів; пропускаємо приватні
        for attr, val in getattr(ns, "__dict__", {}).items():
            # Пропустити службове ім'я
            if attr.startswith("_Namespace__"):
                continue
            self._maybe_yield()
            if isinstance(val, Namespace):
                out[attr] = self._namespace_to_dict(val)
            else:
                out[attr] = val
        return out

    # --------- Імпорт модулів ---------
    def add_aml_search_path(self, path: str) -> None:
        with self._lock:
            self.interpreter.add_aml_search_path(path)

    def add_python_search_path(self, path: str) -> None:
        with self._lock:
            self.interpreter.add_python_search_path(path)

    def import_py(self, modules: List[str]) -> None:
        """Імпортує Python модулі у рантайм AML."""
        if not modules:
            return
        with self._lock:
            stmt = ImportPy(modules)
            self.interpreter.execute_ImportPy(stmt)

    def import_aml(self, modules: List[str]) -> None:
        """Імпортує AML-модулі у рантайм AML."""
        if not modules:
            return
        with self._lock:
            stmt = ImportAml(modules)
            self.interpreter.execute_ImportAml(stmt)

    # --------- Виклик функцій ---------
    def call_function(self, name: str, *args: Any) -> Any:
        """Викликає AML/Python функцію. Підтримує крапкові імена (namespace.attr)."""
        with self._lock:
            callee = self._resolve_symbol(name)
            if isinstance(callee, Function):
                return callee.call(self.interpreter, list(args))
            if callable(callee):
                return callee(*args)
            raise RuntimeError(f"'{name}' не є функцією")

    def _resolve_symbol(self, name: str) -> Any:
        """
        Розв'язує ім'я з крапками у поточному середовищі.
        Напр.: 'a.main' -> environment.get('a') -> getattr(ns, 'main').
        Підтримує Namespace, будь-які Python-об'єкти та dict ключі.
        """
        parts = name.split('.')
        if not parts:
            raise RuntimeError("Порожнє ім'я функції")
        # Перша частина завжди з середовища
        current = self.interpreter.environment.get(parts[0])
        for part in parts[1:]:
            self._maybe_yield()
            # Спроба доступу як атрибуту (Namespace/модуль/об'єкт)
            if hasattr(current, part):
                current = getattr(current, part)
                continue
            # Доступ як до словника
            if isinstance(current, dict) and part in current:
                current = current[part]
                continue
            raise RuntimeError(f"Не знайдено атрибут '{part}' у '{name}'")
        return current

    def _assign_symbol(self, dotted_name: str, value: Any, create_if_missing: bool = True) -> None:
        """Присвоює значення для крапкового імені.
        'a.first' -> setattr(environment.get('a'), 'first', value).
        Підтримує атрибути об'єктів та ключі словників.
        """
        parts = dotted_name.split('.')
        if len(parts) < 2:
            # fallback до верхнього рівня
            try:
                self.interpreter.environment.assign(dotted_name, value)
            except Exception:
                if create_if_missing:
                    self.interpreter.environment.define(dotted_name, value)
                else:
                    raise
            return
        # Розв'язуємо батьківський об'єкт
        parent = self.interpreter.environment.get(parts[0])
        for part in parts[1:-1]:
            self._maybe_yield()
            if hasattr(parent, part):
                parent = getattr(parent, part)
            elif isinstance(parent, dict) and part in parent:
                parent = parent[part]
            else:
                # Створюємо проміжний dict, якщо потрібно
                if create_if_missing and isinstance(parent, dict):
                    parent[part] = {}
                    parent = parent[part]
                else:
                    raise RuntimeError(f"Не знайдено проміжний атрибут '{part}' у '{dotted_name}'")
        last = parts[-1]
        if isinstance(parent, dict):
            parent[last] = value
        else:
            setattr(parent, last, value)

    # --------- Namespace API ---------
    def create_namespace(self, name: str) -> Namespace:
        """Створює або повертає існуючий namespace у кореневому середовищі."""
        with self._lock:
            try:
                existing = self.interpreter.environment.get(name)
                if isinstance(existing, Namespace):
                    return existing
            except Exception:
                pass
            ns = Namespace(name)
            self.interpreter.environment.define(name, ns)
            return ns

    def get_namespace(self, name: str) -> Namespace:
        """Повертає namespace за ім'ям або кидає помилку."""
        with self._lock:
            obj = self.interpreter.environment.get(name)
            if not isinstance(obj, Namespace):
                raise RuntimeError(f"'{name}' не є Namespace")
            return obj

    def set_namespace_var(self, ns_name: str, var_name: str, value: Any) -> None:
        """Встановлює/оновлює змінну усередині namespace."""
        with self._lock:
            ns = self.get_namespace(ns_name)
            setattr(ns, var_name, value)

    def get_namespace_var(self, ns_name: str, var_name: str) -> Any:
        """Отримує значення змінної усередині namespace."""
        with self._lock:
            ns = self.get_namespace(ns_name)
            if not hasattr(ns, var_name):
                raise RuntimeError(f"Namespace '{ns_name}' не має змінної '{var_name}'")
            return getattr(ns, var_name)

    def add_namespace_function(self, ns_name: str, func_name: str, func: Any) -> None:
        """Додає Python/AML функцію як метод у namespace."""
        with self._lock:
            ns = self.get_namespace(ns_name)
            # Дозволяємо як AML Function, так і Python callable
            if isinstance(func, Function) or callable(func):
                setattr(ns, func_name, func)
            else:
                raise RuntimeError("Очікується AML Function або Python callable")

    def add_namespace_functions(self, ns_name: str, mapping: Dict[str, Any]) -> None:
        """Пакетне додавання функцій у namespace."""
        if not mapping:
            return
        with self._lock:
            ns = self.get_namespace(ns_name)
            for k, v in mapping.items():
                if isinstance(v, Function) or callable(v):
                    setattr(ns, k, v)
                else:
                    raise RuntimeError(f"'{k}': очікується Function або callable")

    # --------- Вбудовані Python функції та класи ---------
    def add_builtin(self, name: str, obj: Any) -> None:
        """Додає Python-функцію або клас у кореневе середовище AML під ім'ям."""
        if not isinstance(obj, (types.FunctionType, types.BuiltinFunctionType)) and not callable(obj):
            # Дозволяємо також будь-які значення, але попереджаємо розробника
            pass
        with self._lock:
            self.interpreter.environment.define(name, obj)

    def add_builtins(self, mapping: Dict[str, Any]) -> None:
        """Додає кілька вбудованих об'єктів одним викликом."""
        if not mapping:
            return
        with self._lock:
            for k, v in mapping.items():
                self.interpreter.environment.define(k, v)

    def expose_builtins_from_module(self, module_name: str, names: List[str]) -> None:
        """Імпортує Python-модуль та експортує задані атрибути у корінь AML."""
        if not names:
            return
        # Імпортуємо модуль через існуючу логіку
        self.import_py([module_name])
        module = self.interpreter.python_modules.get(module_name)
        if module is None:
            raise RuntimeError(f"Не вдалося імпортувати модуль '{module_name}'")
        with self._lock:
            for attr in names:
                if not hasattr(module, attr):
                    raise RuntimeError(f"Модуль '{module_name}' не має атрибуту '{attr}'")
                self.interpreter.environment.define(attr, getattr(module, attr))


class AMLRuntimeManager:
    """Керування багатьма AMLRuntime: створення, доступ, запуск та зупинка."""
    def __init__(self):
        self._runtimes: Dict[str, AMLRuntime] = {}
        self._lock = threading.RLock()

    def create_runtime(self, name: str, **kwargs) -> AMLRuntime:
        with self._lock:
            if name in self._runtimes:
                raise RuntimeError(f"Рантайм з ім'ям '{name}' вже існує")
            rt = AMLRuntime(
                default_py_modules=kwargs.get("default_py_modules"),
                default_aml_modules=kwargs.get("default_aml_modules"),
                aml_search_paths=kwargs.get("aml_search_paths"),
                python_search_paths=kwargs.get("python_search_paths"),
            )
            self._runtimes[name] = rt
            return rt

    def get_runtime(self, name: str) -> AMLRuntime:
        with self._lock:
            if name not in self._runtimes:
                raise RuntimeError(f"Рантайм '{name}' не знайдено")
            return self._runtimes[name]

    def remove_runtime(self, name: str, stop: bool = True) -> None:
        with self._lock:
            rt = self._runtimes.pop(name, None)
            if rt is None:
                return
            if stop:
                try:
                    rt.stop()
                    rt.join(timeout=1.0)
                except Exception:
                    pass

    def list_runtimes(self) -> List[str]:
        with self._lock:
            return list(self._runtimes.keys())

    def start_runtime(self, name: str) -> None:
        rt = self.get_runtime(name)
        rt.start()

    def stop_runtime(self, name: str) -> None:
        rt = self.get_runtime(name)
        rt.stop()
        rt.join(timeout=1.0)

    def stop_all(self) -> None:
        with self._lock:
            for rt in self._runtimes.values():
                try:
                    rt.stop()
                except Exception:
                    pass
        # Після виставлення cancel — очікуємо завершення
        with self._lock:
            for rt in self._runtimes.values():
                try:
                    rt.join(timeout=1.0)
                except Exception:
                    pass
