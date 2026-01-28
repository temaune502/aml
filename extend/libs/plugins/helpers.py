"""
Helpers модуль - QoL утиліти для повсякденного використання

Модуль забезпечує корисні функції для конвертування, валідації,
форматування, кешування та інших практичних операцій.

Функції:
    - Конвертування типів даних
    - Валідація даних
    - Форматування текстів та дат
    - Кешування з TTL
    - Парсинг і обробка даних
    - Роботи з файлами та шляхами
    - Утиліти для стрічок
"""

import json
import re
import os
from typing import Any, List, Dict, Optional, Callable, Union, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import pickle
from functools import wraps
import time


# ============================================================================
# КОНВЕРТУВАННЯ ТИПІВ ДАНИХ
# ============================================================================

def to_int(value: Any, default: int = 0) -> int:
    """
    Конвертувати значення на int з забезпеченням
    
    Args:
        value: Значення для конвертування
        default: Значення за замовчуванням при помилці
    
    Returns:
        int: Конвертоване значення
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    """Конвертувати на float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def to_bool(value: Any) -> bool:
    """
    Конвертувати на bool розумно
    
    Args:
        value: Значення для конвертування
    
    Returns:
        bool: Логічне значення
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 'ok', 'да')
    return bool(value)


def to_list(value: Any) -> List:
    """
    Конвертувати на список
    
    Args:
        value: Значення для конвертування
    
    Returns:
        List: Список
    """
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    if isinstance(value, str):
        return [value]
    return [value]


def to_dict(value: Any) -> Dict:
    """
    Конвертувати на словник
    
    Args:
        value: Значення для конвертування (JSON стрічка або dict)
    
    Returns:
        Dict: Словник
    """
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}
    return {}


def to_string(value: Any) -> str:
    """Конвертувати на стрічку"""
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


# ============================================================================
# ВАЛІДАЦІЯ ДАНИХ
# ============================================================================

def is_email(email: str) -> bool:
    """Перевірити чи стрічка є email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_url(url: str) -> bool:
    """Перевірити чи стрічка є URL"""
    pattern = r'^https?://[^\s]+$'
    return bool(re.match(pattern, url))


def is_phone(phone: str) -> bool:
    """
    Перевірити чи стрічка є номером телефону
    Формати: +380..., 380..., 0..., (0...) ...
    """
    pattern = r'^(\+?3)?8[0-9]{9,10}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')))


def is_ipv4(ip: str) -> bool:
    """Перевірити чи стрічка є IPv4 адресою"""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    return all(0 <= to_int(part, -1) <= 255 for part in parts)


def is_valid_json(text: str) -> bool:
    """Перевірити чи стрічка є валідним JSON"""
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def has_length(value: Any, min_len: int = 0, max_len: Optional[int] = None) -> bool:
    """Перевірити довжину значення"""
    try:
        length = len(value)
        return min_len <= length and (max_len is None or length <= max_len)
    except TypeError:
        return False


def matches_pattern(text: str, pattern: str) -> bool:
    """Перевірити чи текст відповідає regex паттерну"""
    try:
        return bool(re.search(pattern, text))
    except re.error:
        return False


# ============================================================================
# ФОРМАТУВАННЯ ТЕКСТІВ
# ============================================================================

def capitalize_first(text: str) -> str:
    """Капіталізувати першу букву"""
    return text[0].upper() + text[1:] if text else text


def to_camel_case(text: str) -> str:
    """Конвертувати на camelCase"""
    parts = text.split('_')
    return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])


def to_snake_case(text: str) -> str:
    """Конвертувати на snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_kebab_case(text: str) -> str:
    """Конвертувати на kebab-case"""
    return to_snake_case(text).replace('_', '-')


def to_title_case(text: str) -> str:
    """Конвертувати на Title Case"""
    return ' '.join(word.capitalize() for word in text.split())


def truncate(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Обрізати текст до максимальної довжини
    
    Args:
        text: Текст для обрізання
        max_length: Максимальна довжина
        suffix: Суфікс для обрізаного тексту
    
    Returns:
        str: Обрізаний текст
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def remove_special_chars(text: str, keep: str = '') -> str:
    """
    Видалити спеціальні символи
    
    Args:
        text: Текст для обробки
        keep: Символи для збереження
    
    Returns:
        str: Текст без спеціальних символів
    """
    pattern = f'[^a-zA-Z0-9Ї-я{re.escape(keep)}\\s]'
    return re.sub(pattern, '', text, flags=re.UNICODE)


def slugify(text: str) -> str:
    """Конвертувати текст на slug (для URL)"""
    # Видалити спеціальні символи та пробіли
    text = remove_special_chars(text.lower(), keep='-')
    text = re.sub(r'\s+', '-', text.strip())
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def reverse_string(text: str) -> str:
    """Розвернути стрічку"""
    return text[::-1]


def repeat_string(text: str, count: int, separator: str = '') -> str:
    """Повторити стрічку кілька разів"""
    return separator.join([text] * count)


# ============================================================================
# ФОРМАТУВАННЯ ДУРИ І ЧАСУ
# ============================================================================

def format_date(date_obj: Union[datetime, str],
               format_str: str = '%d.%m.%Y') -> str:
    """
    Форматувати дату
    
    Args:
        date_obj: Об'єкт дати або стрічка
        format_str: Формат (за замовч. 'dd.mm.yyyy')
    
    Returns:
        str: Форматована дата
    """
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj)
        except ValueError:
            return date_obj
    
    return date_obj.strftime(format_str)


def format_datetime(dt: datetime,
                   format_str: str = '%d.%m.%Y %H:%M:%S') -> str:
    """Форматувати дату і час"""
    return dt.strftime(format_str)


def format_time(seconds: float) -> str:
    """
    Форматувати час в зрозумілій формі
    
    Args:
        seconds: Кількість секунд
    
    Returns:
        str: Форматований час (напр. "2h 30m 45s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return ' '.join(parts)


def format_bytes(bytes_count: int) -> str:
    """
    Форматувати кількість байтів в зрозумілій формі
    
    Args:
        bytes_count: Кількість байтів
    
    Returns:
        str: Форматований розмір (напр. "2.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"


def format_number(number: Union[int, float], decimals: int = 2) -> str:
    """Форматувати число з розділювачами тисяч"""
    return f"{number:,.{decimals}f}"


def human_readable_time_delta(dt: datetime) -> str:
    """
    Описати час від дати у людяній формі
    
    Args:
        dt: Дата для порівняння
    
    Returns:
        str: Описаний час (напр. "2 дні тому")
    """
    delta = datetime.now() - dt
    
    if delta.days > 365:
        return f"{delta.days // 365} років тому"
    if delta.days > 30:
        return f"{delta.days // 30} місяців тому"
    if delta.days > 0:
        return f"{delta.days} днів тому"
    
    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours} годин тому"
    
    minutes = (delta.seconds % 3600) // 60
    if minutes > 0:
        return f"{minutes} хвилин тому"
    
    return "щойно"


# ============================================================================
# КЕШУВАННЯ З TTL
# ============================================================================

class SimpleCache:
    """Простий кеш з TTL"""
    
    def __init__(self, ttl: float = 300.0):
        """
        Ініціалізація кешу
        
        Args:
            ttl: Time to live в секундах
        """
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
    
    def set(self, key: str, value: Any) -> None:
        """Встановити значення в кеш"""
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def get(self, key: str) -> Optional[Any]:
        """Отримати значення з кешу"""
        if key not in self.cache:
            return None
        
        if time.time() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key]
    
    def delete(self, key: str) -> bool:
        """Видалити значення з кешу"""
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
            return True
        return False
    
    def clear(self) -> None:
        """Очистити кеш"""
        self.cache.clear()
        self.timestamps.clear()
    
    def __contains__(self, key: str) -> bool:
        """Перевірити наявність ключа"""
        return self.get(key) is not None


# ============================================================================
# РОБОТА З ФАЙЛАМИ І ШЛЯХАМИ
# ============================================================================

def ensure_dir(dirpath: str) -> Path:
    """
    Переконатися що директорія існує
    
    Args:
        dirpath: Шлях до директорії
    
    Returns:
        Path: Об'єкт Path директорії
    """
    path = Path(dirpath)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_file(filepath: str, encoding: str = 'utf-8') -> Optional[str]:
    """
    Прочитати вміст файлу
    
    Args:
        filepath: Шлях до файлу
        encoding: Кодування
    
    Returns:
        str: Вміст файлу або None
    """
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Помилка читання файлу: {e}")
        return None


def write_file(filepath: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    Написати вміст у файл
    
    Args:
        filepath: Шлях до файлу
        content: Вміст для запису
        encoding: Кодування
    
    Returns:
        bool: True якщо успішно
    """
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Помилка запису файлу: {e}")
        return False


def read_lines(filepath: str, encoding: str = 'utf-8') -> List[str]:
    """Прочитати рядки з файлу"""
    content = read_file(filepath, encoding)
    return content.split('\n') if content else []


def append_file(filepath: str, content: str, encoding: str = 'utf-8') -> bool:
    """Додати вміст у кінець файлу"""
    try:
        with open(filepath, 'a', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Помилка додавання до файлу: {e}")
        return False


def file_size(filepath: str) -> int:
    """Отримати розмір файлу в байтах"""
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0


def file_exists(filepath: str) -> bool:
    """Перевірити чи файл існує"""
    return os.path.isfile(filepath)


def delete_file(filepath: str) -> bool:
    """Видалити файл"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        return True
    except Exception as e:
        print(f"Помилка видалення файлу: {e}")
        return False


# ============================================================================
# УТИЛІТИ ДЛЯ СТРІЧОК
# ============================================================================

def count_words(text: str) -> int:
    """Порахувати слова в тексті"""
    return len(text.split())


def count_lines(text: str) -> int:
    """Порахувати рядки в тексті"""
    return len(text.split('\n'))


def count_chars(text: str, ignore_spaces: bool = False) -> int:
    """Порахувати символи в тексті"""
    if ignore_spaces:
        text = text.replace(' ', '')
    return len(text)


def find_all_matches(text: str, pattern: str) -> List[str]:
    """Знайти всі збіги регулярного виразу"""
    try:
        return re.findall(pattern, text)
    except re.error:
        return []


def replace_all(text: str, replacements: Dict[str, str]) -> str:
    """Замінити кілька пар у тексті"""
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def remove_duplicates(items: List[str], case_sensitive: bool = True) -> List[str]:
    """Видалити дублікати зберігаючи порядок"""
    seen = set()
    result = []
    for item in items:
        key = item if case_sensitive else item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def dedent(text: str) -> str:
    """Видалити спільний відступ з тексту"""
    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    
    if not non_empty_lines:
        return text
    
    min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
    
    return '\n'.join(line[min_indent:] if line.strip() else line for line in lines)


# ============================================================================
# УТИЛІТИ ДЛЯ ХЕШУВАННЯ
# ============================================================================

def hash_md5(text: str) -> str:
    """Отримати MD5 хеш тексту"""
    return hashlib.md5(text.encode()).hexdigest()


def hash_sha256(text: str) -> str:
    """Отримати SHA256 хеш тексту"""
    return hashlib.sha256(text.encode()).hexdigest()


def hash_file(filepath: str, algorithm: str = 'sha256') -> Optional[str]:
    """Отримати хеш файлу"""
    try:
        hash_obj = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f"Помилка хешування файлу: {e}")
        return None


# ============================================================================
# УТИЛІТИ ДЛЯ СПИСКІВ
# ============================================================================

def flatten(lst: List[List[Any]]) -> List[Any]:
    """Сплющити вложену список"""
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Розділити список на частини"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def unique(lst: List[Any]) -> List[Any]:
    """Отримати унікальні елементи зберігаючи порядок"""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def find_index(lst: List[Any], item: Any) -> int:
    """Знайти індекс елемента (повертає -1 якщо не знайдено)"""
    try:
        return lst.index(item)
    except ValueError:
        return -1


def intersect(lst1: List[Any], lst2: List[Any]) -> List[Any]:
    """Отримати перетин двох списків"""
    return [item for item in lst1 if item in lst2]


def difference(lst1: List[Any], lst2: List[Any]) -> List[Any]:
    """Отримати різницю двох списків"""
    return [item for item in lst1 if item not in lst2]


def group_by(lst: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict[str, Any]]]:
    """Групувати список словників за ключем"""
    result = {}
    for item in lst:
        group_key = item.get(key)
        if group_key not in result:
            result[group_key] = []
        result[group_key].append(item)
    return result


# ============================================================================
# УТИЛІТИ ДЛЯ СЛОВНИКІВ
# ============================================================================

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Об'єднати кілька словників"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def filter_dict(d: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Отримати словник тільки з вказаними ключами"""
    return {k: v for k, v in d.items() if k in keys}


def exclude_dict(d: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Отримати словник без вказаних ключів"""
    return {k: v for k, v in d.items() if k not in keys}


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Сплющити вложений словник"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def deep_get(d: Dict[str, Any], keys: str, default: Any = None) -> Any:
    """
    Отримати значення з вложеного словника за точковою нотацією
    
    Args:
        d: Словник
        keys: Ключи з точками (напр. "user.profile.name")
        default: Значення за замовчуванням
    
    Returns:
        Any: Значення або default
    """
    for key in keys.split('.'):
        if isinstance(d, dict):
            d = d.get(key)
        else:
            return default
    return d if d is not None else default


# ============================================================================
# СИСТЕМНІ УТИЛІТИ
# ============================================================================

def get_current_timestamp() -> int:
    """Отримати поточний UNIX timestamp"""
    return int(time.time())


def sleep_ms(milliseconds: float) -> None:
    """Спати вказану кількість мілісекунд"""
    time.sleep(milliseconds / 1000.0)


def get_env(key: str, default: str = '') -> str:
    """Отримати змінну середовища"""
    return os.getenv(key, default)


def set_env(key: str, value: str) -> None:
    """Встановити змінну середовища"""
    os.environ[key] = value
