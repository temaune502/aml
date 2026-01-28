"""
Модуль для перетворення типів та валідації даних в AML.
"""

def to_str(value):
    """Перетворити значення в рядок."""
    if value is None:
        return ""
    return str(value)

def to_int(value, default=0):
    """Перетворити значення в ціле число. Повертає default при помилці."""
    try:
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            if not value.strip():
                return default
            return int(float(value)) # Handles '1.0' as well
        return int(value)
    except (ValueError, TypeError):
        return default

def to_float(value, default=0.0):
    """Перетворити значення в число з плаваючою комою. Повертає default при помилці."""
    try:
        if isinstance(value, str) and not value.strip():
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def to_bool(value):
    """
    Перетворити значення в логічний тип.
    Рядки 'true', '1', 'yes', 'on' вважаються True.
    Рядки 'false', '0', 'no', 'off' вважаються False.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.lower().strip()
        if v in ('true', '1', 'yes', 'on'): return True
        if v in ('false', '0', 'no', 'off'): return False
        return bool(v)
    return bool(value)

def to_list(value):
    """Перетворити значення в список (підтримує tuple, set, range)."""
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set, range)):
        return list(value)
    if value is None:
        return []
    return [value]

def to_aml(value):
    """
    Рекурсивно перетворює типи Python в типи, прийнятні для AML.
    - tuple, set, range -> list
    - complex -> dict {real, imag}
    - bytes -> string (hex)
    - datetime -> string (ISO format)
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    
    if isinstance(value, (list, tuple, set, range)):
        return [to_aml(item) for item in value]
    
    if isinstance(value, dict):
        return {str(k): to_aml(v) for k, v in value.items()}
    
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.hex()
            
    # Перевірка на об'єкти дати/часу без імпорту datetime на початку
    type_name = type(value).__name__
    if type_name in ('datetime', 'date', 'time'):
        return value.isoformat()
        
    # Якщо це об'єкт з методом to_dict або подібним
    if hasattr(value, '__dict__'):
        return {k: to_aml(v) for k, v in value.__dict__.items() if not k.startswith('_')}

    return str(value)

def get_type(value):
    """Повернути назву типу значення."""
    if value is None: return "null"
    if isinstance(value, bool): return "boolean"
    if isinstance(value, (int, float)): return "number"
    if isinstance(value, str): return "string"
    if isinstance(value, list): return "list"
    if isinstance(value, dict): return "dict"
    return type(value).__name__

def is_num(value):
    """Чи є значення числом."""
    return isinstance(value, (int, float))

def is_str(value):
    """Чи є значення рядком."""
    return isinstance(value, str)

def is_list(value):
    """Чи є значення списком."""
    return isinstance(value, list)

def is_dict(value):
    """Чи є значення словником."""
    return isinstance(value, dict)

def is_bool(value):
    """Чи є значення логічним типом."""
    return isinstance(value, bool)

def is_null(value):
    """Чи є значення null."""
    return value is None
