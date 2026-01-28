import threading
import aml_runtime_access

class CallbackManager:
    """
    Утиліта для керування колбеками з AML в Python плагінах.
    Дозволяє безпечно викликати AML функції з різних потоків.
    """
    def __init__(self):
        self._callbacks = {}
        self._next_id = 1
        self._lock = threading.Lock()

    def register(self, callback):
        """Реєструє AML функцію як колбек і повертає її ID."""
        with self._lock:
            cb_id = self._next_id
            self._next_id += 1
            self._callbacks[cb_id] = callback
            return cb_id

    def unregister(self, cb_id):
        """Видаляє колбек за його ID."""
        with self._lock:
            if cb_id in self._callbacks:
                del self._callbacks[cb_id]
                return True
            return False

    def execute(self, cb_id, args=None):
        """Виконує AML функцію за її ID з переданими аргументами."""
        if args is None:
            args = []
            
        with self._lock:
            callback = self._callbacks.get(cb_id)
            
        if not callback:
            return None

        interpreter = aml_runtime_access.get_interpreter()
        if not interpreter:
            return None

        try:
            if hasattr(callback, 'call'):
                # Це об'єкт функції AML
                return callback.call(interpreter, args)
            elif callable(callback):
                # Це звичайна функція Python
                return callback(*args)
        except Exception as e:
            print(f"Error executing callback {cb_id}: {e}")
            return None

    def execute_all(self, args=None):
        """Виконує всі зареєстровані колбеки."""
        ids = []
        with self._lock:
            ids = list(self._callbacks.keys())
            
        results = []
        for cb_id in ids:
            results.append(self.execute(cb_id, args))
        return results

# Глобальний екземпляр для загального використання
_manager = CallbackManager()

def register(callback):
    return _manager.register(callback)

def unregister(cb_id):
    return _manager.unregister(cb_id)

def execute(cb_id, args=None):
    return _manager.execute(cb_id, args)
