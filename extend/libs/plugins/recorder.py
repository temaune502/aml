"""
Recorder модуль для запису та відтворення дій

Модуль дозволяє записувати послідовність дій користувача (клацання миші,
рух миші, натиски клавіш) та відтворювати їх у вигляді макросів.

Функції:
    - Запис дій користувача
    - Відтворення записаних дій
    - Редагування макросів
    - Експорт/імпорт макросів
    - Планування виконання
"""

import json
import time
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
from datetime import datetime
import threading


class ActionType(Enum):
    """Типи дій для запису"""
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    MOUSE_DOUBLE_CLICK = "mouse_double_click"
    MOUSE_RIGHT_CLICK = "mouse_right_click"
    MOUSE_SCROLL = "mouse_scroll"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    WAIT = "wait"
    TEXT_TYPE = "text_type"


@dataclass
class RecordedAction:
    """Клас для однієї записаної дії"""
    action_type: str
    timestamp: float
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[str] = None
    key: Optional[str] = None
    text: Optional[str] = None
    dx: Optional[int] = None
    dy: Optional[int] = None
    duration: Optional[float] = None
    count: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Конвертувати дію в словник"""
        return {k: v for k, v in asdict(self).items() if v is not None}


class Recorder:
    """Клас для запису та управління макросами"""
    
    def __init__(self, name: str = "macro"):
        """
        Ініціалізація Recorder
        
        Args:
            name: Назва макросу
        """
        self.name = name
        self.actions: List[RecordedAction] = []
        self.is_recording = False
        self.start_time = 0
        self.base_time = 0
        self._listeners = []
    
    def start_recording(self) -> None:
        """Почати запис дій"""
        self.actions = []
        self.is_recording = True
        self.start_time = time.time()
        self.base_time = self.start_time
        print(f"[Запис] Макрос '{self.name}' розпочатий")
    
    def stop_recording(self) -> None:
        """Зупинити запис дій"""
        self.is_recording = False
        print(f"[Запис] Макрос '{self.name}' зупинений. Записано {len(self.actions)} дій")
    
    def record_mouse_move(self, x: int, y: int) -> None:
        """
        Записати рух миші
        
        Args:
            x: X координата
            y: Y координата
        """
        if self.is_recording:
            action = RecordedAction(
                action_type=ActionType.MOUSE_MOVE.value,
                timestamp=time.time() - self.base_time,
                x=x,
                y=y
            )
            self.actions.append(action)
    
    def record_mouse_click(self, x: int, y: int,
                          button: str = "left",
                          count: int = 1) -> None:
        """
        Записати клацання миші
        
        Args:
            x: X координата
            y: Y координата
            button: Кнопка ('left', 'right', 'middle')
            count: Кількість клацань
        """
        if self.is_recording:
            action = RecordedAction(
                action_type=ActionType.MOUSE_CLICK.value,
                timestamp=time.time() - self.base_time,
                x=x,
                y=y,
                button=button,
                count=count
            )
            self.actions.append(action)
    
    def record_mouse_scroll(self, x: int, y: int,
                           dx: int = 0,
                           dy: int = 1) -> None:
        """
        Записати гортання миші
        
        Args:
            x: X координата
            y: Y координата
            dx: Гортання горизонтально
            dy: Гортання вертикально
        """
        if self.is_recording:
            action = RecordedAction(
                action_type=ActionType.MOUSE_SCROLL.value,
                timestamp=time.time() - self.base_time,
                x=x,
                y=y,
                dx=dx,
                dy=dy
            )
            self.actions.append(action)
    
    def record_key_press(self, key: str) -> None:
        """
        Записати натиск клавіші
        
        Args:
            key: Назва клавіші
        """
        if self.is_recording:
            action = RecordedAction(
                action_type=ActionType.KEY_PRESS.value,
                timestamp=time.time() - self.base_time,
                key=key
            )
            self.actions.append(action)
    
    def record_text(self, text: str) -> None:
        """
        Записати введення тексту
        
        Args:
            text: Текст для запису
        """
        if self.is_recording:
            action = RecordedAction(
                action_type=ActionType.TEXT_TYPE.value,
                timestamp=time.time() - self.base_time,
                text=text
            )
            self.actions.append(action)
    
    def record_wait(self, duration: float = 1.0) -> None:
        """
        Записати паузу
        
        Args:
            duration: Тривалість паузи в секундах
        """
        if self.is_recording:
            action = RecordedAction(
                action_type=ActionType.WAIT.value,
                timestamp=time.time() - self.base_time,
                duration=duration
            )
            self.actions.append(action)
    
    def save(self, filepath: str) -> bool:
        """
        Зберегти макрос у файл JSON
        
        Args:
            filepath: Шлях до файлу
        
        Returns:
            bool: True якщо успішно
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'name': self.name,
                'created': datetime.now().isoformat(),
                'action_count': len(self.actions),
                'actions': [action.to_dict() for action in self.actions]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"[Збереження] Макрос збережено: {filepath}")
            return True
        except Exception as e:
            print(f"Помилка збереження макросу: {e}")
            return False
    
    def load(self, filepath: str) -> bool:
        """
        Завантажити макрос з файлу JSON
        
        Args:
            filepath: Шлях до файлу
        
        Returns:
            bool: True якщо успішно
        """
        try:
            if not Path(filepath).exists():
                raise FileNotFoundError(f"Файл не знайдено: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.name = data.get('name', 'macro')
            self.actions = []
            
            for action_data in data.get('actions', []):
                action = RecordedAction(
                    action_type=action_data['action_type'],
                    timestamp=action_data['timestamp'],
                    x=action_data.get('x'),
                    y=action_data.get('y'),
                    button=action_data.get('button'),
                    key=action_data.get('key'),
                    text=action_data.get('text'),
                    dx=action_data.get('dx'),
                    dy=action_data.get('dy'),
                    duration=action_data.get('duration'),
                    count=action_data.get('count')
                )
                self.actions.append(action)
            
            print(f"[Завантаження] Макрос завантажено: {filepath} ({len(self.actions)} дій)")
            return True
        except Exception as e:
            print(f"Помилка завантаження макросу: {e}")
            return False
    
    def playback(self,
                loop_count: int = 1,
                speed: float = 1.0,
                executor: Optional[Callable] = None) -> None:
        """
        Відтворити записані дії
        
        Args:
            loop_count: Кількість повторень
            speed: Швидкість відтворення (1.0 = нормальна)
            executor: Функція-виконавець дій
        """
        if not self.actions:
            print("Немає дій для відтворення")
            return
        
        if executor is None:
            executor = self._default_executor
        
        print(f"[Відтворення] Початок відтворення макросу '{self.name}' ({loop_count} разів)")
        
        for loop in range(loop_count):
            print(f"[Відтворення] Цикл {loop + 1}/{loop_count}")
            
            for i, action in enumerate(self.actions):
                wait_time = action.timestamp / speed
                
                if i > 0:
                    time_diff = (action.timestamp - self.actions[i-1].timestamp) / speed
                    time.sleep(time_diff)
                
                executor(action)
        
        print(f"[Відтворення] Готово")
    
    def _default_executor(self, action: RecordedAction) -> None:
        """Виконавець за замовчуванням (змінити для своїх потреб)"""
        try:
            from . import automation
            
            if action.action_type == ActionType.MOUSE_MOVE.value:
                automation.move_mouse(action.x, action.y, smooth=False)
            elif action.action_type == ActionType.MOUSE_CLICK.value:
                automation.click(x=action.x, y=action.y, button=action.button, count=action.count or 1)
            elif action.action_type == ActionType.MOUSE_SCROLL.value:
                automation.scroll(action.dx or 0, action.dy or 1)
            elif action.action_type == ActionType.KEY_PRESS.value:
                automation.press_key(action.key)
            elif action.action_type == ActionType.TEXT_TYPE.value:
                automation.type_text(action.text)
            elif action.action_type == ActionType.WAIT.value:
                time.sleep(action.duration or 1.0)
        except Exception as e:
            print(f"Помилка виконання дії: {e}")
    
    def playback_async(self,
                      loop_count: int = 1,
                      speed: float = 1.0,
                      executor: Optional[Callable] = None) -> threading.Thread:
        """
        Відтворити дії у фоновому потоці
        
        Args:
            loop_count: Кількість повторень
            speed: Швидкість відтворення
            executor: Функція-виконавець
        
        Returns:
            Thread: Об'єкт потоку
        """
        thread = threading.Thread(
            target=self.playback,
            args=(loop_count, speed, executor)
        )
        thread.daemon = True
        thread.start()
        return thread
    
    def edit_action(self, index: int, **kwargs) -> bool:
        """
        Редагувати дію за індексом
        
        Args:
            index: Індекс дії
            **kwargs: Параметри для зміни
        
        Returns:
            bool: True якщо успішно
        """
        try:
            if 0 <= index < len(self.actions):
                action = self.actions[index]
                for key, value in kwargs.items():
                    if hasattr(action, key):
                        setattr(action, key, value)
                return True
            return False
        except Exception as e:
            print(f"Помилка редагування дії: {e}")
            return False
    
    def delete_action(self, index: int) -> bool:
        """
        Видалити дію за індексом
        
        Args:
            index: Індекс дії
        
        Returns:
            bool: True якщо успішно
        """
        try:
            if 0 <= index < len(self.actions):
                self.actions.pop(index)
                return True
            return False
        except Exception as e:
            print(f"Помилка видалення дії: {e}")
            return False
    
    def clear(self) -> None:
        """Очистити всі дії"""
        self.actions = []
        print(f"[Макрос] '{self.name}' очищено")
    
    def get_statistics(self) -> Dict:
        """
        Отримати статистику макросу
        
        Returns:
            Dict: Словник зі статистикою
        """
        action_counts = {}
        for action in self.actions:
            action_type = action.action_type
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        total_duration = self.actions[-1].timestamp if self.actions else 0
        
        return {
            'name': self.name,
            'total_actions': len(self.actions),
            'total_duration': total_duration,
            'action_breakdown': action_counts
        }
    
    def __str__(self) -> str:
        """Строкове представлення макросу"""
        stats = self.get_statistics()
        return f"Макрос '{self.name}': {stats['total_actions']} дій, {stats['total_duration']:.2f} сек"
    
    def __len__(self) -> int:
        """Кількість дій в макросі"""
        return len(self.actions)
    
    def __getitem__(self, index: int) -> RecordedAction:
        """Отримати дію за індексом"""
        return self.actions[index]
