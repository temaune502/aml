"""
Документація QoL модулів: helpers.py та dsl_integration.py
Українська версія
"""

# ============================================================================
# HELPERS.PY - ОСНОВНІ УТИЛІТИ
# ============================================================================

HELPERS_MODULE = """
================================================================================
HELPERS.PY - ОСНОВНІ УТИЛІТИ ДЛЯ КОНВЕРТУВАННЯ І ВАЛІДАЦІЇ
================================================================================

ОПИСАННЯ:
Модуль helpers.py надає 50+ практичних функцій для:
- Конвертування типів даних
- Валідації даних
- Форматування текстів і дат
- Роботи з файлами
- Кешування з TTL
- Обробки стрічок, списків і словників
- Хешування

ЗАЛЕЖНОСТІ: тільки стандартна бібліотека Python (pathlib, json, re, datetime, hashlib, time, pickle)

================================================================================
1. КОНВЕРТУВАННЯ ТИПІВ
================================================================================

to_int(value, default=0) -> int
    Конвертує значення в int
    Приклади:
        to_int("42") → 42
        to_int("invalid", default=0) → 0
        to_int("42.5") → 42

to_float(value, default=0.0) -> float
    Конвертує значення в float
    Приклади:
        to_float("3.14") → 3.14
        to_float("invalid", default=0.0) → 0.0

to_bool(value) -> bool
    Розумно конвертує в bool
    Істинні значення: true, 1, yes, on, y, enabled (case-insensitive)
    Приклади:
        to_bool("true") → True
        to_bool("yes") → True
        to_bool("1") → True
        to_bool("0") → False

to_list(value) -> list
    Конвертує значення в список
    Приклади:
        to_list("один") → ["один"]
        to_list((1, 2, 3)) → [1, 2, 3]

to_dict(value) -> dict
    Конвертує JSON стрічку в словник
    Приклади:
        to_dict('{"a": 1}') → {"a": 1}

to_string(value) -> str
    Конвертує значення в стрічку
    Приклади:
        to_string([1, 2, 3]) → '[1, 2, 3]'
        to_string({"key": "value"}) → '{"key": "value"}'

================================================================================
2. ВАЛІДАЦІЯ ДАНИХ
================================================================================

is_email(value: str) -> bool
    Перевіряє коректність email адреси
    Приклад: is_email("user@example.com") → True

is_url(value: str) -> bool
    Перевіряє коректність URL
    Приклад: is_url("https://example.com") → True

is_phone(value: str) -> bool
    Перевіряє коректність номера телефону
    Форматиці: +380961234567, 380961234567, 0961234567
    Приклад: is_phone("+380961234567") → True

is_ipv4(value: str) -> bool
    Перевіряє коректність IPv4 адреси
    Приклад: is_ipv4("192.168.1.1") → True

is_valid_json(value: str) -> bool
    Перевіряє коректність JSON
    Приклад: is_valid_json('{"key": "value"}') → True

matches_pattern(value: str, pattern: str) -> bool
    Перевіряє збіг з regex патерном
    Приклад: matches_pattern("test123", r"\\w+\\d+") → True

has_length(value, min_len=0, max_len=None) -> bool
    Перевіряє довжину значення
    Приклад: has_length("password", min_len=8) → True/False

================================================================================
3. ФОРМАТУВАННЯ ТЕКСТІВ
================================================================================

to_camel_case(text: str) -> str
    Конвертує в camelCase
    Приклад: to_camel_case("hello_world") → "helloWorld"

to_snake_case(text: str) -> str
    Конвертує в snake_case
    Приклад: to_snake_case("HelloWorld") → "hello_world"

to_kebab_case(text: str) -> str
    Конвертує в kebab-case
    Приклад: to_kebab_case("helloWorld") → "hello-world"

to_title_case(text: str) -> str
    Конвертує в Title Case
    Приклад: to_title_case("hello world") → "Hello World"

truncate(text: str, max_length: int, suffix: str = "...") -> str
    Обрізає текст до максимальної довжини
    Приклад: truncate("Hello World", 8) → "Hello..."

remove_special_chars(text: str, keep_spaces: bool = True) -> str
    Видаляє спеціальні символи
    Приклад: remove_special_chars("Hello@World!") → "HelloWorld"

slugify(text: str) -> str
    Створює URL-friendly slug
    Приклад: slugify("My Awesome Blog!") → "my-awesome-blog"

reverse_string(text: str) -> str
    Розвертає стрічку
    Приклад: reverse_string("hello") → "olleh"

repeat_string(text: str, count: int) -> str
    Повторює стрічку
    Приклад: repeat_string("ab", 3) → "ababab"

================================================================================
4. ФОРМАТУВАННЯ ДАТИ И ЧАСУ
================================================================================

format_date(date, fmt: str = "%d.%m.%Y") -> str
    Форматує дату
    Приклад: format_date(datetime.now()) → "16.11.2025"

format_datetime(date_time, fmt: str = "%d.%m.%Y %H:%M:%S") -> str
    Форматує дату и час
    Приклад: format_datetime(datetime.now()) → "16.11.2025 14:30:45"

format_time(seconds: float) -> str
    Форматує час в легкочитаючий формат
    Приклад: format_time(3665) → "1h 1m 5s"

format_bytes(bytes_val: int) -> str
    Форматує байти в легкочитаючий формат
    Приклад: format_bytes(1536) → "1.50 KB"

format_number(num, decimals: int = 0, separator: str = ",") -> str
    Форматує число з розділювачем
    Приклад: format_number(1234567.89) → "1,234,568"

human_readable_time_delta(past_datetime) -> str
    Показує час в людяному форматі
    Приклад: human_readable_time_delta(datetime.now() - timedelta(days=2))
            → "2 дні тому"

================================================================================
5. ФАЙЛОВІ ОПЕРАЦІЇ
================================================================================

ensure_dir(path: str) -> str
    創建директорію якщо не існує
    Приклад: ensure_dir("data/output") → "data/output"

read_file(path: str, encoding: str = "utf-8") -> str
    Читає вміст файлу
    Приклад: read_file("config.json")

write_file(path: str, content: str, encoding: str = "utf-8") -> bool
    Пише контент в файл
    Приклад: write_file("output.txt", "Hello World")

read_lines(path: str, encoding: str = "utf-8") -> List[str]
    Читає файл в список рядків
    Приклад: read_lines("data.txt")

append_file(path: str, content: str, encoding: str = "utf-8") -> bool
    Додає контент до файлу
    Приклад: append_file("log.txt", "New log entry")

delete_file(path: str) -> bool
    Видаляє файл
    Приклад: delete_file("temp.txt")

file_exists(path: str) -> bool
    Перевіряє чи існує файл
    Приклад: file_exists("config.json")

file_size(path: str) -> int
    Повертає розмір файлу в байтах
    Приклад: file_size("data.bin")

================================================================================
6. КЕШУВАННЯ
================================================================================

class SimpleCache:
    Простий кеш з підтримкою TTL (Time-To-Live)
    
    __init__(ttl: float = 3600.0)
        Ініціалізує кеш з TTL в секундах
    
    set(key: str, value: Any) -> None
        Додає значення в кеш
        Приклад: cache.set("user_1", {"name": "Іван"})
    
    get(key: str) -> Any
        Отримує значення з кешу (None якщо експайрив)
        Приклад: user = cache.get("user_1")
    
    delete(key: str) -> bool
        Видаляє значення з кешу
        Приклад: cache.delete("user_1")
    
    clear() -> None
        Очищає весь кеш
        Приклад: cache.clear()
    
    __contains__(key: str) -> bool
        Перевіряє наявність в кеші
        Приклад: if "user_1" in cache: ...
    
    __len__() -> int
        Повертає кількість елементів
        Приклад: size = len(cache)

================================================================================
7. УТИЛІТИ ДЛЯ СТРІЧОК
================================================================================

count_words(text: str) -> int
    Рахує кількість слів
    Приклад: count_words("Hello World Example") → 3

count_lines(text: str) -> int
    Рахує кількість рядків
    Приклад: count_lines("line1\\nline2\\nline3") → 3

count_chars(text: str, exclude_spaces: bool = False) -> int
    Рахує символи
    Приклад: count_chars("Hello World") → 11

find_all_matches(text: str, pattern: str) -> List[str]
    Знаходить всі збіги з regex
    Приклад: find_all_matches("abc123def456", r"\\d+") → ["123", "456"]

replace_all(text: str, replacements: dict) -> str
    Замінює всі збіги
    Приклад: replace_all("Hello World", {"Hello": "Hi", "World": "Earth"})
            → "Hi Earth"

remove_duplicates(items: list) -> list
    Видаляє дублікати зберігаючи порядок
    Приклад: remove_duplicates([1, 2, 2, 3]) → [1, 2, 3]

dedent(text: str) -> str
    Видаляє спільний відступ
    Приклад: dedent("    line1\\n    line2") → "line1\\nline2"

================================================================================
8. УТИЛІТИ ДЛЯ СПИСКІВ
================================================================================

flatten(lst: list) -> list
    Розгортає вкладені списки
    Приклад: flatten([[1, 2], [3, [4, 5]]]) → [1, 2, 3, 4, 5]

chunk_list(lst: list, chunk_size: int) -> List[list]
    Розділяє список на частини
    Приклад: chunk_list([1, 2, 3, 4, 5], 2) → [[1, 2], [3, 4], [5]]

unique(lst: list) -> list
    Повертає унікальні елементи
    Приклад: unique([1, 2, 2, 3]) → [1, 2, 3]

find_index(lst: list, value) -> int
    Знаходить індекс значення (-1 якщо не знайдено)
    Приклад: find_index([1, 2, 3], 2) → 1

intersect(list1: list, list2: list) -> list
    Повертає елементи які є в обох списках
    Приклад: intersect([1, 2, 3], [2, 3, 4]) → [2, 3]

difference(list1: list, list2: list) -> list
    Повертає елементи з list1 що не в list2
    Приклад: difference([1, 2, 3], [2, 3, 4]) → [1]

group_by(items: list, key: str) -> dict
    Групує елементи за ключем
    Приклад: group_by([{"cat": "A", "val": 1}, {"cat": "A", "val": 2}], "cat")
            → {"A": [{"cat": "A", "val": 1}, {"cat": "A", "val": 2}]}

================================================================================
9. УТИЛІТИ ДЛЯ СЛОВНИКІВ
================================================================================

merge_dicts(*dicts) -> dict
    Об'єднує множину словників
    Приклад: merge_dicts({"a": 1}, {"b": 2}) → {"a": 1, "b": 2}

filter_dict(d: dict, keys: list) -> dict
    Залишає тільки вказані ключі
    Приклад: filter_dict({"a": 1, "b": 2}, ["a"]) → {"a": 1}

exclude_dict(d: dict, keys: list) -> dict
    Видаляє вказані ключі
    Приклад: exclude_dict({"a": 1, "b": 2}, ["b"]) → {"a": 1}

flatten_dict(d: dict, parent_key: str = "") -> dict
    Розгортає вкладені словники в плоску структуру
    Приклад: flatten_dict({"user": {"name": "John"}})
            → {"user.name": "John"}

deep_get(d: dict, path: str, default=None)
    Отримує значення через точку
    Приклад: deep_get({"user": {"profile": {"name": "John"}}}, "user.profile.name")
            → "John"

================================================================================
10. ХЕШУВАННЯ
================================================================================

hash_md5(text: str) -> str
    Повертає MD5 хеш
    Приклад: hash_md5("password") → "5f4dcc3b5aa765d61d8327deb882cf99"

hash_sha256(text: str) -> str
    Повертає SHA256 хеш
    Приклад: hash_sha256("password") → "5e884898da28047151d0e56f8dc629..."

hash_file(file_path: str, algorithm: str = "sha256") -> str
    Хешує вміст файлу
    Приклад: hash_file("document.pdf") → "abc123..."

================================================================================
11. СИСТЕМНІ УТИЛІТИ
================================================================================

get_current_timestamp() -> float
    Повертає поточний timestamp
    Приклад: get_current_timestamp() → 1731500000.123

sleep_ms(milliseconds: int) -> None
    Спить на кількість мілісекунд
    Приклад: sleep_ms(500)  # Спить 0.5 секунди

get_env(name: str, default: str = "") -> str
    Отримує змінну середовища
    Приклад: get_env("HOME", "/root")

set_env(name: str, value: str) -> None
    Встановлює змінну середовища
    Приклад: set_env("DEBUG", "1")

================================================================================
"""

# ============================================================================
# DSL_INTEGRATION.PY - СИСТЕМА DSL
# ============================================================================

DSL_INTEGRATION_MODULE = """
================================================================================
DSL_INTEGRATION.PY - СИСТЕМА ДОМЕННО-СПЕЦІАЛЬНОЇ МОВИ (DSL)
================================================================================

ОПИСАННЯ:
Модуль dsl_integration.py надає повну систему для:
- Парсування та виконання DSL скриптів
- Управління змінними та макросами
- Будування DSL скриптів через fluent API
- Інтеграції всіх модулів в єдиний інтерфейс

ЗАЛЕЖНОСТІ: локальні модулі (з fallback-ами)

================================================================================
АРХІТЕКТУРА DSL СИСТЕМИ
================================================================================

1. DSLCommand - Структура парсованої команди
   Поля: name, args, kwargs, raw

2. DSLContext - Контекст виконання
   Управління змінними, функціями, макросами, логами

3. DSLParser - Парсер DSL синтаксису
   Regex-based парсування команд, змінних, строк

4. DSLExecutor - Виконавець команд
   10+ вбудованих команд + користувацькі функції

5. DSLBuilder - Fluid builder для конструювання скриптів
   Method chaining для зручного построения скриптів

6. DSLModuleIntegration - Інтеграція всіх модулів
   Автоматична реєстрація функцій як DSL команд

================================================================================
DSL СИНТАКСИС
================================================================================

КОМАНДИ:
    command_name(arg1, arg2, key=value)
    
    Приклади:
        print("Hello", $name)
        click(100, 200)
        set(user_id, 123)

ЗМІННІ:
    $variable_name
    
    Приклади:
        $name
        $count
        $user_email

СТРІЧКИ:
    "double quotes" або 'single quotes'
    
    Приклади:
        "Hello World"
        'Single quoted string'

ЦИФРИ:
    123, 3.14, true, false
    
    Приклади:
        set(count, 42)
        set(ratio, 3.14)
        set(enabled, true)

================================================================================
ВБУДОВАНІ DSL КОМАНДИ
================================================================================

print(*args)
    Виводить повідомлення
    Приклад: print("Hello", $name, "Age:", $age)

set(name, value)
    Встановлює змінну
    Приклад: set(user_name, "Іван")
             set(count, 42)

get(name) -> value
    Отримує значення змінної
    Приклад: get(user_name)

if(condition, true_block, false_block)
    Умовне виконання
    Приклад: if($age > 18, print("Дорослий"), print("Не дорослий"))

for(var, iterable, block)
    Цикл по ітерабельному
    Приклад: for(i, [1, 2, 3], print("Item:", $i))

sleep(seconds)
    Спить на кількість секунд
    Приклад: sleep(1.5)

macro(name, template)
    Визначає макрос
    Приклад: macro(greet, "Hello, ${name}!")

expand(macro_name, **params)
    Розширює макрос з параметрами
    Приклад: expand(greet, name="Марія")

assert(condition, message)
    Перевіряє умову, кидає помилку якщо неправда
    Приклад: assert(has_length($password, min_len=8), "Коротко")

import(module_name)
    Імпортує додатковий модуль (заплановано)
    Приклад: import(automation)

================================================================================
ФУНКЦІЇ HELPERS ЧЕРЕЗ DSL
================================================================================

Конвертування:
    to_int(value) - конвертує в int
    to_float(value) - конвертує в float
    to_bool(value) - конвертує в bool
    to_list(value) - конвертує в список
    to_str(value) - конвертує в стрічку

Валідація:
    is_email(value) - перевіряє email
    is_url(value) - перевіряє URL
    is_phone(value) - перевіряє телефон
    is_ipv4(value) - перевіряє IPv4
    matches_pattern(value, pattern) - regex match

Форматування:
    to_camel_case(text) - convertuje в camelCase
    to_snake_case(text) - convertuje в snake_case
    to_kebab_case(text) - convertuje в kebab-case
    to_title_case(text) - convertuje в Title Case
    slugify(text) - URL-friendly slug
    truncate(text, max_length) - обрізає текст

Дата/Час:
    format_date(date) - форматує дату
    format_time(seconds) - форматує час
    format_bytes(bytes) - форматує байти
    format_number(num, decimals) - форматує число

Стрічки:
    count_words(text) - рахує слова
    count_chars(text) - рахує символи
    reverse_string(text) - розвертає стрічку
    find_all_matches(text, pattern) - знаходить збіги

Списки:
    flatten(list) - розгортає список
    chunk_list(list, size) - розділяє на частини
    unique(list) - унікальні елементи
    intersect(list1, list2) - перетин
    difference(list1, list2) - різниця

Словники:
    merge_dicts(dict1, dict2) - об'єднує
    filter_dict(dict, keys) - фільтрує ключі
    flatten_dict(dict) - розгортає

Файли:
    read_file(path) - читає файл
    write_file(path, content) - пише файл
    file_exists(path) - перевіряє існування

================================================================================
DSLContext - Контекст виконання
================================================================================

Властивості:
    variables: Dict[str, Any]
        Користувацькі змінні
    
    functions: Dict[str, Callable]
        Зареєстровані функції
    
    macros: Dict[str, str]
        Визначені макроси
    
    output: List[str]
        Логи вивіду
    
    error_log: List[str]
        Логи помилок

Методи:
    set_var(name: str, value: Any) -> None
        Встановлює змінну
        Приклад: context.set_var("user", "Марія")
    
    get_var(name: str, default=None) -> Any
        Отримує змінну
        Приклад: age = context.get_var("age", 0)
    
    register_function(name: str, func: Callable) -> None
        Реєструє функцію
        Приклад: context.register_function("my_func", my_function)
    
    register_macro(name: str, template: str) -> None
        Реєструє макрос
        Приклад: context.register_macro("greet", "Hello, ${name}!")
    
    expand_macro(name: str, **params) -> str
        Розширює макрос
        Приклад: context.expand_macro("greet", name="Іван")
    
    log_output(message: str) -> None
        Додає повідомлення у вивід
    
    log_error(message: str) -> None
        Додає помилку у логи

================================================================================
DSLBuilder - Fluid Builder для конструювання скриптів
================================================================================

Методи (повертають self для chaining):
    
    set_var(name: str, value: Any) -> DSLBuilder
        Встановлює змінну
    
    print_msg(*args) -> DSLBuilder
        Виводить повідомлення
    
    sleep(seconds: float) -> DSLBuilder
        Спить на кількість секунд
    
    add_comment(text: str) -> DSLBuilder
        Додає коментар
    
    add_raw(dsl_code: str) -> DSLBuilder
        Додає сирий DSL код
    
    build() -> str
        Повертає побудований DSL скрипт
    
    execute() -> bool
        Виконує скрипт і повертає успіх

Приклад:
    script = DSLBuilder() \\
        .add_comment("Мій скрипт") \\
        .set_var("name", "Іван") \\
        .print_msg("Привіт", "$name") \\
        .sleep(1) \\
        .build()

================================================================================
DSLParser - Парсер DSL синтаксису
================================================================================

Регулярні вирази:
    Команди: r'(\\w+)\\s*\\((.*?)\\)(?:\\s*\\{(.*?)\\})?'
    Змінні: r'\\$([\\w_]+)'
    Стрічки: "..." або '...'
    Значення: числа, bool, JSON, стрічки

Методи:
    parse_command(line: str) -> DSLCommand
        Парсує команду з рядка
    
    parse_arguments(args_str: str) -> Tuple[list, dict]
        Парсує аргументи і kwargs
    
    parse_value(value_str: str) -> Any
        Конвертує текстове значення в тип

Приклад:
    parser = DSLParser()
    cmd = parser.parse_command('click(100, 200)')
    # cmd.name = 'click'
    # cmd.args = [100, 200]

================================================================================
DSLExecutor - Виконавець команд
================================================================================

Методи:
    execute_script(script: str) -> bool
        Виконує мультирядковий скрипт
        Повертає True якщо успішно
    
    execute_line(line: str) -> bool
        Виконує один рядок
    
    execute_command(cmd: DSLCommand) -> Any
        Виконує парсовану команду

Приклад:
    executor = DSLExecutor(context)
    success = executor.execute_script("""
        set(x, 10)
        print("x =", $x)
    """)

================================================================================
ПРИКЛАДИ ВИКОРИСТАННЯ
================================================================================

Простий DSL скрипт:
    context, executor = create_dsl_system()
    
    script = '''
    set(name, "Іван")
    print("Привіт", $name)
    '''
    
    executor.execute_script(script)

Використання Builder:
    script = DSLBuilder() \\
        .set_var("count", 5) \\
        .print_msg("Лічу до", "$count") \\
        .sleep(1) \\
        .build()
    
    print(script)

Макроси:
    context, executor = create_dsl_system()
    
    script = '''
    macro(greeting, "Привіт, ${name}! Ти маєш ${age} років.")
    expand(greeting, name="Марія", age=25)
    '''
    
    executor.execute_script(script)

Функції helpers:
    context, executor = create_dsl_system()
    
    script = '''
    set(email, "user@example.com")
    assert(is_email($email), "Email невалідний")
    print("✓ Email валідний")
    '''
    
    executor.execute_script(script)

================================================================================
ІНТЕГРАЦІЯ З МОДУЛЯМИ
================================================================================

DSLModuleIntegration автоматично реєструє функції з модулів:

OCR модуль:
    ocr_read_text(image_path)
    ocr_find_text(text)

Screen модуль:
    screen_save(filename)
    screen_find_image(template)

Recorder модуль:
    recorder_start()
    recorder_stop()

Automation модуль:
    click(x, y)
    move_mouse(x, y)
    type_text(text)
    press_key(key)
    scroll(x, y, direction)

Performance модуль:
    log_info(message)
    log_error(message)

Helpers модуль:
    to_int(), to_float(), to_bool(), to_list(), to_str()
    is_email(), is_url(), is_phone(), is_ipv4()
    format_date(), format_time(), format_bytes()
    ... і 40+ інших функцій

================================================================================
ОБРОБКА ПОМИЛОК
================================================================================

Помилки логуються в context.error_log
Виконання продовжується на наступній команді

Приклад:
    context, executor = create_dsl_system()
    
    script = '''
    assert(false, "Це помилка")
    print("Цей рядок не виконується")
    '''
    
    success = executor.execute_script(script)
    print(f"Помилки: {context.error_log}")

================================================================================
ФУНКЦІЯ create_dsl_system()
================================================================================

create_dsl_system() -> Tuple[DSLContext, DSLExecutor]
    
    Створює готову до використання DSL систему
    
    Повертає кортеж (context, executor)
    
    Приклад:
        context, executor = create_dsl_system()
        
        # Використовуємо контекст
        context.set_var("x", 10)
        
        # Виконуємо скрипти
        executor.execute_script("print($x)")

================================================================================
РОЗШИРЕННЯ DSL СИСТЕМИ
================================================================================

Реєстрування користувацької функції:
    def my_function(x, y):
        return x + y
    
    context.register_function("add", my_function)
    
    # Тепер можна використовувати:
    script = "print(add(3, 5))"

Реєстрування макросу:
    context.register_macro("greet", "Hello, ${name}!")
    
    # Використання:
    context.expand_macro("greet", name="World")

================================================================================
"""

if __name__ == "__main__":
    print(HELPERS_MODULE)
    print("\n" + "=" * 80 + "\n")
    print(DSL_INTEGRATION_MODULE)
