# Додаткові утиліти AML

Ці модулі розширюють можливості мови для специфічних завдань. Знаходяться в `temaune/util/`.

## 1. Випадкові числа (`temaune/util/random`)

- `int(min, max)`: Випадкове ціле число в діапазоні.
- `float(min, max)`: Випадкове число з плаваючою комою.
- `choice(list)`: Випадковий елемент зі списку.
- `shuffle(list)`: Перемішування списку.

## 2. Робота з JSON (`temaune/util/json`)

- `parse(json_str)`: Перетворює JSON-рядок у типи AML (списки/словники).
- `stringify(val, indent)`: Перетворює об'єкт AML у JSON-рядок.
- `read_file(path)`: Читає JSON безпосередньо з файлу.
- `write_file(path, val)`: Записує об'єкт у файл як JSON.

## 3. Дата та час (`temaune/util/datetime`)

- `now()`: Поточна дата та час у форматі ISO.
- `today()`: Поточна дата.
- `format(iso_str, fmt)`: Форматування дати.
- `timestamp()`: Поточна мітка часу (Unix timestamp).

## 4. Регулярні вирази (`temaune/util/regex`)

- `match(pattern, s)`: Перевірка відповідності рядка шаблону.
- `search(pattern, s)`: Пошук першого входження.
- `find_all(pattern, s)`: Пошук усіх входжень.
- `replace(pattern, s, repl)`: Заміна за шаблоном.

## 5. Перетворення типів (`temaune/util/convert`)

- `to_int(val, default)`: Перетворення в ціле число.
- `to_float(val, default)`: Перетворення в число з плаваючою комою.
- `to_str(val)`: Перетворення в рядок.
- `to_bool(val)`: Перетворення в логічний тип.
- `type_of(val)`: Отримання назви типу ("number", "string", "list" тощо).
