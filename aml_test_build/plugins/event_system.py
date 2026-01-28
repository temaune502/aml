import threading
from .callback_manager import CallbackManager

class EventSystem:
    """
    Система подій, що дозволяє реєструвати слухачів на певні події
    та викликати їх з Python або AML.
    """
    def __init__(self):
        self._events = {} # {event_name: CallbackManager}
        self._lock = threading.Lock()

    def subscribe(self, event_name, callback):
        """Підписатися на подію."""
        with self._lock:
            # print(f"[Python EventSystem] Subscribing to '{event_name}' with {callback}")
            if event_name not in self._events:
                self._events[event_name] = CallbackManager()
            return self._events[event_name].register(callback)

    def unsubscribe(self, event_name, handler_id):
        """Відписатися від події."""
        with self._lock:
            if event_name in self._events:
                return self._events[event_name].unregister(handler_id)
            return False

    def emit(self, event_name, data=None):
        """Викликати подію з даними."""
        manager = None
        with self._lock:
            manager = self._events.get(event_name)
        
        if manager:
            # Викликаємо всі колбеки для цієї події
            # Аргументи передаються як список [data]
            # print(f"[Python EventSystem] Emitting event '{event_name}' to {len(manager._callbacks)} subscribers")
            return manager.execute_all([data] if data is not None else [])
        # print(f"[Python EventSystem] No subscribers for event '{event_name}'")
        return []

# Глобальний екземпляр
_instance = EventSystem()

def subscribe(event_name, callback):
    return _instance.subscribe(event_name, callback)

def unsubscribe(event_name, handler_id):
    return _instance.unsubscribe(event_name, handler_id)

def emit(event_name, data=None):
    return _instance.emit(event_name, data)
