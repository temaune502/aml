"""
Performance модуль для оптимізації та аналізу

Модуль забезпечує вимірювання продуктивності, логування, батчинг операцій,
асинхронне виконання та профілювання коду.

Функції:
    - Таймер та вимірювання часу
    - Батчинг операцій
    - Асинхронне виконання
    - Кешування результатів
    - Логування та профілювання
"""

import time
import functools
import threading
import json
from typing import Callable, Optional, Any, Dict, List, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

T = TypeVar('T')


class LogLevel(Enum):
    """Рівні логування"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class PerformanceMetric:
    """Метрика продуктивності"""
    operation_name: str
    execution_time: float
    timestamp: float = field(default_factory=time.time)
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Конвертувати метрику в словник"""
        return {
            'operation': self.operation_name,
            'time': round(self.execution_time, 4),
            'timestamp': self.timestamp,
            'success': self.success,
            'error': self.error_message
        }


class SimpleTimer:
    """Простий таймер для вимірювання часу"""
    
    def __init__(self, name: str = "timer"):
        """
        Ініціалізація таймера
        
        Args:
            name: Назва таймера
        """
        self.name = name
        self.start_time = None
        self.elapsed = 0.0
    
    def start(self) -> 'SimpleTimer':
        """Почати таймер"""
        self.start_time = time.time()
        return self
    
    def stop(self) -> float:
        """
        Зупинити таймер
        
        Returns:
            float: Минулий час в секундах
        """
        if self.start_time:
            self.elapsed = time.time() - self.start_time
            return self.elapsed
        return 0.0
    
    def restart(self) -> float:
        """
        Перезапустити таймер
        
        Returns:
            float: Час з останнього запуску
        """
        elapsed = self.stop()
        self.start()
        return elapsed
    
    def __enter__(self):
        """Context manager вхід"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager вихід"""
        self.stop()
    
    def __str__(self) -> str:
        """Строкове представлення"""
        if self.elapsed > 0:
            return f"{self.name}: {self.elapsed:.4f} сек"
        return f"{self.name}: не закінчено"


class Batch(Generic[T]):
    """Клас для батчингу операцій"""
    
    def __init__(self, batch_size: int = 10,
                 timeout: float = 5.0):
        """
        Ініціалізація батча
        
        Args:
            batch_size: Максимальний розмір батча
            timeout: Таймаут видачі батча в секундах
        """
        self.batch_size = batch_size
        self.timeout = timeout
        self.items: List[T] = []
        self.last_flush_time = time.time()
        self.lock = threading.Lock()
    
    def add(self, item: T) -> bool:
        """
        Додати елемент до батча
        
        Args:
            item: Елемент для додавання
        
        Returns:
            bool: True якщо батч готовий до видачі
        """
        with self.lock:
            self.items.append(item)
            return len(self.items) >= self.batch_size
    
    def should_flush(self) -> bool:
        """
        Перевірити чи батч готовий до видачі
        
        Returns:
            bool: True якщо готовий
        """
        with self.lock:
            time_elapsed = time.time() - self.last_flush_time
            return (len(self.items) >= self.batch_size or
                   (len(self.items) > 0 and time_elapsed >= self.timeout))
    
    def flush(self) -> List[T]:
        """
        Видати батч
        
        Returns:
            List: Елементи батча
        """
        with self.lock:
            items = self.items.copy()
            self.items = []
            self.last_flush_time = time.time()
            return items
    
    def __len__(self) -> int:
        """Кількість елементів в батчі"""
        return len(self.items)
    
    def __bool__(self) -> bool:
        """Чи батч не порожній"""
        return len(self.items) > 0


class Logger:
    """Логгер для запису подій та помилок"""
    
    def __init__(self, name: str,
                 log_file: Optional[str] = None,
                 min_level: LogLevel = LogLevel.INFO):
        """
        Ініціалізація логгера
        
        Args:
            name: Назва логгера
            log_file: Шлях до файлу логу або None
            min_level: Мінімальний рівень логування
        """
        self.name = name
        self.log_file = log_file
        self.min_level = min_level
        self.messages: List[Dict] = []
        self.lock = threading.Lock()
        
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    def _should_log(self, level: LogLevel) -> bool:
        """Перевірити чи логувати повідомлення"""
        levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]
        return levels.index(level) >= levels.index(self.min_level)
    
    def _write_log(self, level: LogLevel, message: str) -> None:
        """Написати логу"""
        if not self._should_log(level):
            return
        
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'logger': self.name,
            'level': level.value,
            'message': message
        }
        
        with self.lock:
            self.messages.append(log_entry)
            
            if self.log_file:
                try:
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                except Exception as e:
                    print(f"Помилка запису в логу: {e}")
        
        print(f"[{level.value}] {timestamp} - {message}")
    
    def debug(self, message: str) -> None:
        """Логувати debug повідомлення"""
        self._write_log(LogLevel.DEBUG, message)
    
    def info(self, message: str) -> None:
        """Логувати інформаційне повідомлення"""
        self._write_log(LogLevel.INFO, message)
    
    def warning(self, message: str) -> None:
        """Логувати попередження"""
        self._write_log(LogLevel.WARNING, message)
    
    def error(self, message: str) -> None:
        """Логувати помилку"""
        self._write_log(LogLevel.ERROR, message)
    
    def get_messages(self, level: Optional[LogLevel] = None) -> List[Dict]:
        """
        Отримати повідомлення з логу
        
        Args:
            level: Фільтрувати за рівнем
        
        Returns:
            List[Dict]: Повідомлення
        """
        with self.lock:
            if level:
                return [m for m in self.messages if m['level'] == level.value]
            return self.messages.copy()
    
    def clear(self) -> None:
        """Очистити логу"""
        with self.lock:
            self.messages = []


def measure_time(func: Callable) -> Callable:
    """
    Декоратор для вимірювання часу виконання функції
    
    Args:
        func: Функція для вимірювання
    
    Returns:
        Callable: Завернута функція
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timer = SimpleTimer(func.__name__)
        timer.start()
        try:
            result = func(*args, **kwargs)
            timer.stop()
            print(f"✓ {timer}")
            return result
        except Exception as e:
            timer.stop()
            print(f"✗ {timer} (помилка: {e})")
            raise
    return wrapper


def retry(max_attempts: int = 3,
         delay: float = 1.0,
         backoff: float = 1.0) -> Callable:
    """
    Декоратор для повторного виконання функції при помилці
    
    Args:
        max_attempts: Максимум спроб
        delay: Затримка перед спробою в секундах
        backoff: Множник для затримки кожної наступної спроби
    
    Returns:
        Callable: Декоратор
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"Спроба {attempt + 1}/{max_attempts} не вдалась. Повтор через {current_delay}с...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        print(f"Всі {max_attempts} спроб невдалі")
            
            raise last_exception
        return wrapper
    return decorator


def cache(ttl: float = 60.0) -> Callable:
    """
    Декоратор для кешування результатів функції
    
    Args:
        ttl: Час життя кешу в секундах
    
    Returns:
        Callable: Декоратор
    """
    def decorator(func: Callable) -> Callable:
        cache_data = {}
        cache_time = {}
        lock = threading.Lock()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            
            with lock:
                current_time = time.time()
                
                if key in cache_data:
                    cached_time = cache_time.get(key, 0)
                    if current_time - cached_time < ttl:
                        return cache_data[key]
            
            result = func(*args, **kwargs)
            
            with lock:
                cache_data[key] = result
                cache_time[key] = time.time()
            
            return result
        
        def clear_cache():
            nonlocal cache_data, cache_time
            with lock:
                cache_data.clear()
                cache_time.clear()
        
        wrapper.clear_cache = clear_cache
        return wrapper
    return decorator


class AsyncTaskPool:
    """Пул асинхронних завдань"""
    
    def __init__(self, max_workers: int = 4):
        """
        Ініціалізація пулу
        
        Args:
            max_workers: Максимум робітників
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []
    
    def submit(self, func: Callable, *args, **kwargs):
        """
        Додати завдання до пулу
        
        Args:
            func: Функція для виконання
            *args: Позиційні аргументи
            **kwargs: Ключові аргументи
        
        Returns:
            Future: Об'єкт для отримання результату
        """
        future = self.executor.submit(func, *args, **kwargs)
        self.futures.append(future)
        return future
    
    def wait_all(self, timeout: Optional[float] = None) -> List[Any]:
        """
        Чекати завершення всіх завдань
        
        Args:
            timeout: Максимум секунд для очікування
        
        Returns:
            List: Результати завдань
        """
        results = []
        for future in as_completed(self.futures, timeout=timeout):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"Помилка в завданні: {e}")
                results.append(None)
        
        self.futures = []
        return results
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Вимкнути пул
        
        Args:
            wait: Чекати завершення завдань
        """
        self.executor.shutdown(wait=wait)


class PerformanceMonitor:
    """Монітор продуктивності"""
    
    def __init__(self, name: str = "monitor"):
        """
        Ініціалізація монітора
        
        Args:
            name: Назва монітора
        """
        self.name = name
        self.metrics: List[PerformanceMetric] = []
        self.lock = threading.Lock()
    
    def record_metric(self, operation_name: str,
                     execution_time: float,
                     success: bool = True,
                     error_message: Optional[str] = None) -> None:
        """
        Записати метрику
        
        Args:
            operation_name: Назва операції
            execution_time: Час виконання
            success: Чи успішна
            error_message: Повідомлення про помилку
        """
        metric = PerformanceMetric(
            operation_name=operation_name,
            execution_time=execution_time,
            success=success,
            error_message=error_message
        )
        
        with self.lock:
            self.metrics.append(metric)
    
    def get_statistics(self) -> Dict:
        """
        Отримати статистику
        
        Returns:
            Dict: Статистика
        """
        with self.lock:
            if not self.metrics:
                return {}
            
            stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'errors': 0})
            
            for metric in self.metrics:
                op = metric.operation_name
                stats[op]['count'] += 1
                stats[op]['total_time'] += metric.execution_time
                if not metric.success:
                    stats[op]['errors'] += 1
            
            # Обчислити середній час
            for op in stats:
                stats[op]['avg_time'] = stats[op]['total_time'] / stats[op]['count']
            
            return dict(stats)
    
    def export_metrics(self, filepath: str) -> bool:
        """
        Експортувати метрики
        
        Args:
            filepath: Шлях до файлу
        
        Returns:
            bool: True якщо успішно
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'monitor': self.name,
                'export_time': datetime.now().isoformat(),
                'metrics': [m.to_dict() for m in self.metrics],
                'statistics': self.get_statistics()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Помилка експорту метрик: {e}")
            return False
    
    def clear(self) -> None:
        """Очистити метрики"""
        with self.lock:
            self.metrics = []
