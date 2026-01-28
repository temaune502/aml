"""
JSON модуль для AML: парсинг та серіалізація.
"""

import json

def parse(text):
    """Розпарсити JSON-рядок у Python-об'єкт."""
    return json.loads(text)

def stringify(obj, indent=None, ensure_ascii=False):
    """Перетворити Python-об'єкт у JSON-рядок."""
    return json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii)

def read_json(path, encoding='utf-8'):
    """Прочитати JSON-файл та повернути Python-об'єкт."""
    with open(path, 'r', encoding=encoding) as f:
        return json.load(f)

def write_json(path, obj, indent=2, ensure_ascii=False, encoding='utf-8'):
    """Записати Python-об'єкт у JSON-файл."""
    with open(path, 'w', encoding=encoding) as f:
        json.dump(obj, f, indent=indent, ensure_ascii=ensure_ascii)