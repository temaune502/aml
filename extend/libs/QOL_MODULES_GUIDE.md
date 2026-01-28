# Посібник QoL модулів: helpers.py та dsl_integration.py

## Огляд

Два нові модулі розроблені для підвищення якості життя розробника та розширення можливостей всієї системи:

- **helpers.py** (1200 рядків) - 50+ практичних функцій для конвертування, валідації та обробки даних
- **dsl_integration.py** (800 рядків) - Повна система DSL для оркестрування всіх модулів

## helpers.py - Утиліти на кожен день

### Основні групи функцій

#### 1. Конвертування типів (6 функцій)
```python
from plugins import helpers

# to_int - розумне конвертування в int
helpers.to_int("42")  # 42
helpers.to_int("invalid", default=0)  # 0

# to_bool - розумно розпізнає істину
helpers.to_bool("true")  # True
helpers.to_bool("yes")  # True
helpers.to_bool("1")  # True
helpers.to_bool("0")  # False

# to_list, to_dict, to_string
helpers.to_list("один")  # ["один"]
helpers.to_list((1, 2, 3))  # [1, 2, 3]
```

#### 2. Валідація даних (7 функцій)
```python
# Email, URL, телефон, IPv4
helpers.is_email("user@example.com")  # True
helpers.is_url("https://example.com")  # True
helpers.is_phone("+380961234567")  # True (українські номери)
helpers.is_ipv4("192.168.1.1")  # True

# JSON та патерни
helpers.is_valid_json('{"key": "value"}')  # True
helpers.matches_pattern("test123", r"\w+\d+")  # True

# Довжина
helpers.has_length("password", min_len=8)  # True/False
```

#### 3. Форматування текстів (10 функцій)
```python
# Case conversions
helpers.to_camel_case("hello_world")  # helloWorld
helpers.to_snake_case("HelloWorld")  # hello_world
helpers.to_kebab_case("helloWorld")  # hello-world
helpers.to_title_case("hello world")  # Hello World

# Truncate, slug, reverse
helpers.truncate("Hello World", 8)  # Hello...
helpers.slugify("My Blog Post!")  # my-blog-post
helpers.reverse_string("hello")  # olleh
```

#### 4. Дата і час (5 функцій)
```python
from datetime import datetime, timedelta

# Форматування
helpers.format_date(datetime.now())  # 16.11.2025
helpers.format_time(3665)  # 1h 1m 5s
helpers.format_bytes(1536)  # 1.50 KB
helpers.format_number(1234567.89, decimals=2)  # 1,234,567.89

# Людяний час
past = datetime.now() - timedelta(days=2)
helpers.human_readable_time_delta(past)  # 2 дні тому
```

#### 5. Файлові операції (8 функцій)
```python
# Базові операції
helpers.write_file("output.txt", "content")
content = helpers.read_file("input.txt")
lines = helpers.read_lines("data.txt")

# Перевірки та операції
helpers.file_exists("config.json")  # True/False
helpers.file_size("document.pdf")  # розмір в байтах
helpers.delete_file("temp.txt")

# Директорії
helpers.ensure_dir("data/output")  # створює якщо не існує
```

#### 6. Кешування (SimpleCache клас)
```python
# Кеш з TTL (Time-To-Live)
cache = helpers.SimpleCache(ttl=60.0)  # 60 секунд

# Використання
cache.set("user_1", {"name": "Іван", "age": 25})
user = cache.get("user_1")  # Отримує або None

# Перевірка та управління
if "user_1" in cache:
    print("Є в кеші")

cache.delete("user_1")
cache.clear()  # очистити весь кеш
```

#### 7. Утиліти для стрічок (11 функцій)
```python
text = "Hello World Example"

# Рахування
helpers.count_words(text)  # 3
helpers.count_lines(text)  # 1
helpers.count_chars(text)  # 19

# Пошук та заміна
helpers.find_all_matches(text, r"\w+o\w*")  # ['Hello', 'World']
helpers.replace_all(text, {"Hello": "Hi", "World": "Earth"})
helpers.remove_duplicates([1, 2, 2, 3])  # [1, 2, 3]
```

#### 8. Операції зі списками (7 функцій)
```python
lst = [1, 2, 3, 4, 5]

# Розділення та фільтрування
helpers.chunk_list(lst, 2)  # [[1, 2], [3, 4], [5]]
helpers.unique([1, 2, 2, 3])  # [1, 2, 3]

# Множинні операції
list1 = [1, 2, 3, 4]
list2 = [3, 4, 5, 6]
helpers.intersect(list1, list2)  # [3, 4]
helpers.difference(list1, list2)  # [1, 2]

# Групування
data = [{"cat": "A", "val": 1}, {"cat": "B", "val": 2}]
helpers.group_by(data, "cat")
```

#### 9. Операції зі словниками (5 функцій)
```python
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3, "d": 4}

# Об'єднання та фільтрування
helpers.merge_dicts(dict1, dict2)  # {"a": 1, "b": 2, "c": 3, "d": 4}

d = {"name": "Іван", "age": 25, "city": "Київ"}
helpers.filter_dict(d, ["name", "age"])  # {"name": "Іван", "age": 25}
helpers.exclude_dict(d, ["city"])  # {"name": "Іван", "age": 25}

# Глибокий доступ
nested = {"user": {"profile": {"name": "Марія"}}}
helpers.deep_get(nested, "user.profile.name")  # Марія
```

#### 10. Хешування (3 функції)
```python
text = "secret_password"

# MD5 та SHA256
helpers.hash_md5(text)
helpers.hash_sha256(text)

# Хеш файлу
helpers.hash_file("document.pdf")
```

#### 11. Системні утиліти (4 функції)
```python
# Час та затримка
timestamp = helpers.get_current_timestamp()
helpers.sleep_ms(500)  # спить 0.5 секунди

# Змінні середовища
helpers.get_env("HOME", "/root")
helpers.set_env("DEBUG", "1")
```

## dsl_integration.py - Система DSL

### Що таке DSL?

DSL (Domain Specific Language) - спеціалізована мова для автоматизації задач. Усі функції інших модулів можна викликати через простий синтаксис.

### Базові концепції

#### 1. Змінні
```dsl
set(name, "Іван")
set(age, 25)
print("Ім'я:", $name)
print("Вік:", $age)
```

#### 2. Команди
```dsl
click(100, 200)               # Клік на координатах
move_mouse(500, 300)          # Переміщення миші
type_text("Hello")            # Набір тексту
press_key("Enter")            # Натискання клавіші
screenshot("screen.png")      # Скрінव
```

#### 3. Умови
```dsl
if($age > 18, 
  print("Дорослий"), 
  print("Дитина")
)
```

#### 4. Цикли
```dsl
for(i, [1,2,3,4,5], 
  print("Число:", $i)
)
```

#### 5. Макроси
```dsl
macro(greeting, "Привіт, ${name}! Тобі ${age} років.")
expand(greeting, name="Петро", age=30)
```

### Приклад 1: Простий скрипт
```python
from plugins.dsl_integration import create_dsl_system

context, executor = create_dsl_system()

script = """
# Мій перший DSL скрипт
set(user_name, "Марія")
set(user_score, 95)

print("========== Результати ==========")
print("Користувач:", $user_name)
print("Очки:", $user_score)

# Перевірка
assert(is_email("test@example.com"), "Email не валідний")
print("✓ Email перевірено")

print("========== Завершено ==========")
"""

executor.execute_script(script)
print("Вивід:")
for line in context.output:
    print(" ", line)
```

### Приклад 2: Builder із методами
```python
from plugins.dsl_integration import DSLBuilder

# Методи ланцюжками для зручності
script = DSLBuilder() \
    .add_comment("Автоматизація форми входу") \
    .set_var("username", "user@example.com") \
    .set_var("password", "secure_pass_123") \
    .print_msg("Заповнюю форму входу...") \
    .sleep(0.5) \
    .print_msg("✓ Форма заповнена") \
    .build()

print("Генерований DSL код:")
print(script)
```

### Приклад 3: Валідація та обробка даних
```python
from plugins.dsl_integration import create_dsl_system

context, executor = create_dsl_system()

script = """
# Валідація користувацьких даних
set(email, "user@example.com")
set(phone, "+380961234567")
set(password, "my_secure_password")

print("=== Валідація даних ===")

# Email
assert(is_email($email), "Email невалідний")
print("✓ Email:", $email)

# Телефон
assert(is_phone($phone), "Телефон невалідний")
print("✓ Телефон:", $phone)

# Пароль
assert(has_length($password, min_len=8), "Пароль занадто короткий")
print("✓ Пароль надійний (довжина:", count_chars($password), ")")

# Форматування
print("\\n=== Форматування ===")
set(text, "hello_world_example")
print("camelCase:", to_camel_case($text))
print("Title Case:", to_title_case($text))
print("Slug:", slugify($text))
"""

executor.execute_script(script)
```

### Приклад 4: Обробка колекцій
```python
from plugins.dsl_integration import create_dsl_system

context, executor = create_dsl_system()

script = """
# Робота зі списками та словниками

# Конвертування
set(numbers_str, "1,2,3,4,5")
set(numbers, to_list([1,2,3,4,5]))

print("=== Списки ===")
print("Оригінал:", $numbers)
print("Унікальні:", unique([1,2,2,3,3]))
print("Перші 3:", chunk_list($numbers, 2))

# Словники
set(user, to_dict('{"name": "Іван", "age": 25}'))
print("\\n=== Словники ===")
print("Користувач:", $user)
"""

executor.execute_script(script)
```

### Приклад 5: Обробка файлів через DSL
```python
from plugins.dsl_integration import create_dsl_system

context, executor = create_dsl_system()

script = """
# Робота з файлами

print("=== Файлові операції ===")

# Запис файлу
write_file("test.txt", "Line 1\\nLine 2\\nLine 3")
print("✓ Файл написаний")

# Читання файлу
set(content, read_file("test.txt"))
print("Вміст:", $content)

# Операції з файлами
print("Існує:", file_exists("test.txt"))
set(size_bytes, file_size("test.txt"))
print("Розмір:", format_bytes($size_bytes))

# Видалення
delete_file("test.txt")
print("✓ Файл видалено")
"""

executor.execute_script(script)
```

## Інтеграція з іншими модулями

### automation.py через DSL
```dsl
# Переміщення миші
move_mouse(100, 200)

# Клік
click(300, 400)

# Набір тексту
type_text("Hello World")

# Натискання клавіші
press_key("Enter")
```

### ocr.py через DSL
```dsl
# Зчитування тексту
set(text, ocr_read_text("screen.png"))
print("Прочитано:", $text)

# Пошук тексту
ocr_find_text("Search Text")
```

### screen.py через DSL
```dsl
# Скрінshot
screen_save("screenshot.png")

# Пошук зображення
screen_find_image("template.png")

# Чекання змін
screen_wait_change(2)
```

## Рекомендації

### Коли використовувати helpers.py
- Конвертування типів даних
- Валідація користувацьких вводів
- Форматування для виводу
- Обробка файлів
- Кешування результатів

### Коли використовувати dsl_integration.py
- Скрипти для автоматизації
- Складні робочі потоки з умовами і циклами
- Конфіги замість JSON
- Тести з читаємим синтаксисом
- Макроси та переносимі сценарії

### Комбінація
```python
# Комбінуємо обидва модулі
from plugins import helpers
from plugins.dsl_integration import create_dsl_system

context, executor = create_dsl_system()

# Підготуємо дані з helpers
email = "user@example.com"
if helpers.is_email(email):
    context.set_var("user_email", email)

# Виконаємо DSL скрипт
script = """
print("Email:", $user_email)
print("Валідний:", is_email($user_email))
"""

executor.execute_script(script)
```

## Залежності

- **helpers.py**: Тільки Python stdlib (pathlib, json, re, datetime, hashlib, time, pickle, os)
- **dsl_integration.py**: Тільки stdlib + локальні модулі (з fallback-ами)

Можна використовувати без установки додаткових пакетів!

## Файли та приклади

- `helpers.py` (1200 рядків) - Модуль з 50+ функціями
- `dsl_integration.py` (800 рядків) - Система DSL
- `examples_qol.py` - 20 практичних прикладів
- `QOL_MODULES_DOCUMENTATION.md` - Повна документація API

## Подальші крокі

1. Завантажте модулі в директорію `plugins/`
2. Прочитайте документацію в `QOL_MODULES_DOCUMENTATION.md`
3. Запустіть приклади з `examples_qol.py`
4. Інтегруйте в ваші проєкти

Успіхів!
