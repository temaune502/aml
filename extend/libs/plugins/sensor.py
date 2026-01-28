"""
Sensor модуль для моніторингу екрану

Модуль забезпечує моніторинг екрану в реальному часі, виявлення змін,
отримання данних координат та оброблення подій.

Функції:
    - Моніторинг змін на екрані
    - Callback функції для подій
    - Моніторинг миші та клавіатури
    - Журналування подій
"""

import threading
import time
from typing import Callable, Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict


class EventType(Enum):
    """Типи подій для моніторингу"""
    SCREEN_CHANGE = "screen_change"
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    KEYBOARD_EVENT = "keyboard_event"
    CUSTOM = "custom"


@dataclass
class Event:
    """Клас для подій"""
    event_type: EventType
    timestamp: float
    data: Dict = None
    
    def to_dict(self) -> Dict:
        """Конвертувати подію в словник"""
        return {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp,
            'data': self.data or {}
        }


class EventListener:
    """Слухач подій"""
    
    def __init__(self, event_type: EventType,
                 callback: Callable,
                 filter_func: Optional[Callable] = None):
        """
        Ініціалізація EventListener
        
        Args:
            event_type: Тип подій для сліджання
            callback: Функція-обробник
            filter_func: Функція для фільтрації подій
        """
        self.event_type = event_type
        self.callback = callback
        self.filter_func = filter_func
        self.is_active = True
    
    def handle(self, event: Event) -> None:
        """
        Обробити подію
        
        Args:
            event: Подія для обробки
        """
        if not self.is_active:
            return
        
        if self.filter_func and not self.filter_func(event):
            return
        
        try:
            self.callback(event)
        except Exception as e:
            print(f"Помилка в callback функції: {e}")
    
    def disable(self) -> None:
        """Вимкнути слухача"""
        self.is_active = False
    
    def enable(self) -> None:
        """Включити слухача"""
        self.is_active = True


class Sensor:
    """Основний клас для моніторингу"""
    
    def __init__(self, name: str = "sensor"):
        """
        Ініціалізація Sensor
        
        Args:
            name: Назва сенсора
        """
        self.name = name
        self.listeners: Dict[EventType, List[EventListener]] = defaultdict(list)
        self.events_history: List[Event] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.log_file: Optional[str] = None
        self.max_history = 10000
    
    def add_listener(self,
                    event_type: EventType,
                    callback: Callable,
                    filter_func: Optional[Callable] = None) -> EventListener:
        """
        Додати слухача подій
        
        Args:
            event_type: Тип подій
            callback: Функція-обробник
            filter_func: Функція фільтру
        
        Returns:
            EventListener: Об'єкт слухача
        """
        listener = EventListener(event_type, callback, filter_func)
        self.listeners[event_type].append(listener)
        return listener
    
    def remove_listener(self, listener: EventListener) -> bool:
        """
        Видалити слухача
        
        Args:
            listener: Об'єкт слухача
        
        Returns:
            bool: True якщо видалено
        """
        for event_type, listeners in self.listeners.items():
            if listener in listeners:
                listeners.remove(listener)
                return True
        return False
    
    def emit_event(self, event_type: EventType,
                   data: Optional[Dict] = None) -> None:
        """
        Спустити подію
        
        Args:
            event_type: Тип подій
            data: Данні подій
        """
        event = Event(event_type, time.time(), data)
        
        # Додати до історії
        self.events_history.append(event)
        if len(self.events_history) > self.max_history:
            self.events_history.pop(0)
        
        # Логувати якщо встановлено
        if self.log_file:
            self._log_event(event)
        
        # Сповістити слухачів
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                listener.handle(event)
        
        # Сповістити слухачів для всіх подій
        if EventType.CUSTOM in self.listeners:
            for listener in self.listeners[EventType.CUSTOM]:
                listener.handle(event)
    
    def start_monitoring(self,
                        check_interval: float = 0.5,
                        log_file: Optional[str] = None) -> None:
        """
        Почати моніторинг
        
        Args:
            check_interval: Інтервал перевірки в секундах
            log_file: Шлях до файлу для логування подій
        """
        if self.is_monitoring:
            print(f"[{self.name}] Моніторинг вже активний")
            return
        
        self.is_monitoring = True
        self.log_file = log_file
        
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(check_interval,),
            daemon=True
        )
        self.monitor_thread.start()
        print(f"[{self.name}] Моніторинг розпочатий")
    
    def stop_monitoring(self) -> None:
        """Зупинити моніторинг"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        print(f"[{self.name}] Моніторинг зупинений")
    
    def _monitor_loop(self, check_interval: float) -> None:
        """
        Основний цикл моніторингу
        
        Args:
            check_interval: Інтервал перевірки
        """
        while self.is_monitoring:
            try:
                # Перевірити екран на зміни
                self._check_screen_changes()
                time.sleep(check_interval)
            except Exception as e:
                print(f"Помилка в циклі моніторингу: {e}")
                time.sleep(check_interval)
    
    def _check_screen_changes(self) -> None:
        """Перевірити зміни на екрані"""
        try:
            from . import screen
            
            # Отримати поточний скріншот
            current_screenshot = screen.screenshot_region(0, 0, 100, 100)
            
            # Порівняти з попереднім (якщо є)
            if hasattr(self, '_last_screenshot'):
                has_changes, change_pct, _ = screen.detect_changes(
                    self._last_screenshot, current_screenshot
                )
                
                if has_changes:
                    self.emit_event(
                        EventType.SCREEN_CHANGE,
                        {'change_percentage': change_pct}
                    )
            
            self._last_screenshot = current_screenshot
        except Exception as e:
            pass  # screen модуль може бути недоступний
    
    def _log_event(self, event: Event) -> None:
        """
        Логувати подію у файл
        
        Args:
            event: Подія для логування
        """
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                log_entry = json.dumps(event.to_dict(), ensure_ascii=False)
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"Помилка логування: {e}")
    
    def get_event_statistics(self) -> Dict:
        """
        Отримати статистику подій
        
        Returns:
            Dict: Статистика по типам подій
        """
        stats = {}
        for event in self.events_history:
            event_type = event.event_type.value
            stats[event_type] = stats.get(event_type, 0) + 1
        return stats
    
    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """
        Отримати всі подій певного типу
        
        Args:
            event_type: Тип подій
        
        Returns:
            List[Event]: Список подій
        """
        return [e for e in self.events_history if e.event_type == event_type]
    
    def get_recent_events(self, count: int = 100) -> List[Event]:
        """
        Отримати останні подій
        
        Args:
            count: Кількість подій
        
        Returns:
            List[Event]: Список останніх подій
        """
        return self.events_history[-count:]
    
    def clear_history(self) -> None:
        """Очистити історію подій"""
        self.events_history = []
        print(f"[{self.name}] Історія подій очищена")
    
    def wait_for_event(self,
                       event_type: EventType,
                       timeout: int = 30,
                       filter_func: Optional[Callable] = None) -> Optional[Event]:
        """
        Чекати поки буде спущена подія
        
        Args:
            event_type: Тип подій для очікування
            timeout: Максимум секунд
            filter_func: Функція для фільтрації
        
        Returns:
            Event: Спущена подія або None
        """
        result = None
        
        def on_event(event: Event):
            nonlocal result
            if filter_func is None or filter_func(event):
                result = event
        
        listener = self.add_listener(event_type, on_event)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if result is not None:
                self.remove_listener(listener)
                return result
            time.sleep(0.1)
        
        self.remove_listener(listener)
        return None
    
    def export_events(self, filepath: str) -> bool:
        """
        Експортувати подій у JSON файл
        
        Args:
            filepath: Шлях до файлу
        
        Returns:
            bool: True якщо успішно
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'sensor_name': self.name,
                'export_time': datetime.now().isoformat(),
                'event_count': len(self.events_history),
                'events': [e.to_dict() for e in self.events_history]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Помилка експорту подій: {e}")
            return False
    
    def __str__(self) -> str:
        """Строкове представлення сенсора"""
        stats = self.get_event_statistics()
        return f"Сенсор '{self.name}': {len(self.events_history)} подій, стан {'активний' if self.is_monitoring else 'неактивний'}"


class ScreenSensor(Sensor):
    """Спеціалізований сенсор для моніторингу екрану"""
    
    def __init__(self, name: str = "screen_sensor"):
        super().__init__(name)
        self._last_hash = None
    
    def _check_screen_changes(self) -> None:
        """Перевірити зміни екрану за хешем"""
        try:
            from . import screen
            from PIL import ImageGrab
            
            current = ImageGrab.grab()
            current_hash = screen.get_image_hash(current)
            
            if self._last_hash and current_hash != self._last_hash:
                self.emit_event(
                    EventType.SCREEN_CHANGE,
                    {'hash_changed': True}
                )
            
            self._last_hash = current_hash
        except Exception:
            pass
