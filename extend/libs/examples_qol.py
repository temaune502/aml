"""
Практичні приклади QoL модулів та DSL інтеграції
Приклади 1-35: Реальні сценарії використання
"""

# ============================================================================
# ПРИМЕРЫ HELPERS МОДУЛЯ
# ============================================================================

# ============================================================================
# ПРИКЛАД 1: Конвертування типів
# ============================================================================
def example_1_type_conversion():
    """Конвертувати різні типи даних"""
    from plugins import helpers
    
    # Конвертування на int
    num1 = helpers.to_int("42")  # 42
    num2 = helpers.to_int("invalid", default=0)  # 0
    
    # Конвертування на bool розумно
    bool1 = helpers.to_bool("true")  # True
    bool2 = helpers.to_bool("yes")  # True
    bool3 = helpers.to_bool("1")  # True
    bool4 = helpers.to_bool("0")  # False
    
    # Конвертування на список
    list1 = helpers.to_list("один")  # ["один"]
    list2 = helpers.to_list((1, 2, 3))  # [1, 2, 3]
    
    print(f"int: {num1}, {num2}")
    print(f"bool: {bool1}, {bool2}")
    print(f"list: {list1}, {list2}")


# ============================================================================
# ПРИКЛАД 2: Валідація даних
# ============================================================================
def example_2_validation():
    """Валідувати різні формати даних"""
    from plugins import helpers
    
    # Email
    if helpers.is_email("user@example.com"):
        print("✓ Коректний email")
    
    # URL
    if helpers.is_url("https://example.com"):
        print("✓ Коректний URL")
    
    # Телефон
    if helpers.is_phone("+380961234567"):
        print("✓ Коректний номер телефону")
    
    # IPv4
    if helpers.is_ipv4("192.168.1.1"):
        print("✓ Коректна IPv4 адреса")
    
    # JSON
    if helpers.is_valid_json('{"key": "value"}'):
        print("✓ Коректний JSON")
    
    # Довжина
    if helpers.has_length("password", min_len=8):
        print("✓ Пароль має достатню довжину")


# ============================================================================
# ПРИКЛАД 3: Форматування текстів
# ============================================================================
def example_3_text_formatting():
    """Форматувати текст в різні формати"""
    from plugins import helpers
    
    text = "hello_world_example"
    
    # CamelCase
    camel = helpers.to_camel_case(text)  # helloWorldExample
    print(f"CamelCase: {camel}")
    
    # snake_case
    snake = helpers.to_snake_case("HelloWorld")  # hello_world
    print(f"snake_case: {snake}")
    
    # kebab-case
    kebab = helpers.to_kebab_case("helloWorld")  # hello-world
    print(f"kebab-case: {kebab}")
    
    # Title Case
    title = helpers.to_title_case("hello world")  # Hello World
    print(f"Title Case: {title}")
    
    # Обрізання
    long_text = "Це дуже довгий текст що потребує обрізання"
    truncated = helpers.truncate(long_text, max_length=30)  # Це дуже довгий текст що п...
    print(f"Truncated: {truncated}")
    
    # Slug
    slug = helpers.slugify("My Awesome Blog Post!")  # my-awesome-blog-post
    print(f"Slug: {slug}")


# ============================================================================
# ПРИКЛАД 4: Форматування дати і часу
# ============================================================================
def example_4_date_time_formatting():
    """Форматувати дати та часи"""
    from plugins import helpers
    from datetime import datetime, timedelta
    
    # Поточна дата
    now = datetime.now()
    
    # Форматування дати
    formatted = helpers.format_date(now, '%d.%m.%Y')  # 16.11.2025
    print(f"Дата: {formatted}")
    
    # Форматування часу
    time_str = helpers.format_time(3665)  # 1h 1m 5s
    print(f"Час: {time_str}")
    
    # Форматування байтів
    bytes_str = helpers.format_bytes(1536)  # 1.50 KB
    print(f"Розмір: {bytes_str}")
    
    # Форматування числа
    num_str = helpers.format_number(1234567.89, decimals=2)  # 1,234,567.89
    print(f"Число: {num_str}")
    
    # Людяний час
    past = now - timedelta(days=2)
    human_time = helpers.human_readable_time_delta(past)  # 2 дні тому
    print(f"Час: {human_time}")


# ============================================================================
# ПРИКЛАД 5: Кешування
# ============================================================================
def example_5_caching():
    """Використовувати простий кеш з TTL"""
    from plugins import helpers
    import time
    
    # Створити кеш з TTL 2 секунди
    cache = helpers.SimpleCache(ttl=2.0)
    
    # Додати значення
    cache.set("user_1", {"name": "Іван", "age": 25})
    
    # Отримати значення
    user = cache.get("user_1")
    print(f"Користувач: {user}")
    
    # Перевірити наявність
    if "user_1" in cache:
        print("✓ Користувач в кеші")
    
    # Чекати 3 секунди - кеш експайрив
    time.sleep(3)
    
    # Значення вже видалено
    user = cache.get("user_1")
    print(f"Після TTL: {user}")  # None


# ============================================================================
# ПРИКЛАД 6: Робота з файлами
# ============================================================================
def example_6_file_operations():
    """Працювати з файлами"""
    from plugins import helpers
    
    # Написати файл
    content = "Це текст для файлу\nДругий рядок"
    helpers.write_file("test.txt", content)
    
    # Прочитати файл
    read_content = helpers.read_file("test.txt")
    print(f"Прочитано: {read_content}")
    
    # Прочитати рядки
    lines = helpers.read_lines("test.txt")
    print(f"Рядків: {len(lines)}")
    
    # Розмір файлу
    size = helpers.file_size("test.txt")
    print(f"Розмір: {helpers.format_bytes(size)}")
    
    # Перевірити наявність
    exists = helpers.file_exists("test.txt")
    print(f"Файл існує: {exists}")
    
    # Видалити файл
    helpers.delete_file("test.txt")


# ============================================================================
# ПРИКЛАД 7: Утиліти для стрічок
# ============================================================================
def example_7_string_utilities():
    """Утиліти для обробки стрічок"""
    from plugins import helpers
    
    text = "Hello World Hello"
    
    # Рахування
    words = helpers.count_words(text)  # 3
    print(f"Слів: {words}")
    
    # Пошук збігів
    matches = helpers.find_all_matches(text, r"\w+o\w*")  # ['Hello', 'Hello']
    print(f"Збіги: {matches}")
    
    # Заміни
    replacements = {"Hello": "Hi", "World": "Universe"}
    replaced = helpers.replace_all(text, replacements)  # Hi Universe Hi
    print(f"Замінено: {replaced}")
    
    # Видалення дублікатів
    items = ["apple", "banana", "apple", "cherry"]
    unique = helpers.remove_duplicates(items)  # ['apple', 'banana', 'cherry']
    print(f"Унікальні: {unique}")


# ============================================================================
# ПРИКЛАД 8: Утиліти для списків
# ============================================================================
def example_8_list_utilities():
    """Утиліти для списків"""
    from plugins import helpers
    
    lst = [1, 2, 3, 4, 5]
    
    # Розділити на частини
    chunks = helpers.chunk_list(lst, chunk_size=2)  # [[1, 2], [3, 4], [5]]
    print(f"Частини: {chunks}")
    
    # Унікальні елементи
    items = [1, 2, 2, 3, 3, 3]
    unique = helpers.unique(items)  # [1, 2, 3]
    print(f"Унікальні: {unique}")
    
    # Перетин
    list1 = [1, 2, 3, 4]
    list2 = [3, 4, 5, 6]
    intersection = helpers.intersect(list1, list2)  # [3, 4]
    print(f"Перетин: {intersection}")
    
    # Різниця
    difference = helpers.difference(list1, list2)  # [1, 2]
    print(f"Різниця: {difference}")
    
    # Групування
    data = [
        {"category": "A", "value": 1},
        {"category": "B", "value": 2},
        {"category": "A", "value": 3}
    ]
    grouped = helpers.group_by(data, "category")
    print(f"Згруповано: {grouped}")


# ============================================================================
# ПРИКЛАД 9: Утиліти для словників
# ============================================================================
def example_9_dict_utilities():
    """Утиліти для словників"""
    from plugins import helpers
    
    dict1 = {"a": 1, "b": 2}
    dict2 = {"c": 3, "d": 4}
    
    # Об'єднання
    merged = helpers.merge_dicts(dict1, dict2)  # {"a": 1, "b": 2, "c": 3, "d": 4}
    print(f"Об'єднано: {merged}")
    
    # Фільтрування
    d = {"name": "Іван", "age": 25, "city": "Київ"}
    filtered = helpers.filter_dict(d, ["name", "age"])  # {"name": "Іван", "age": 25}
    print(f"Відфільтровано: {filtered}")
    
    # Глибокий доступ
    nested = {"user": {"profile": {"name": "Марія"}}}
    name = helpers.deep_get(nested, "user.profile.name")  # Марія
    print(f"Значення: {name}")


# ============================================================================
# ПРИКЛАД 10: Хешування
# ============================================================================
def example_10_hashing():
    """Хешування текстів і файлів"""
    from plugins import helpers
    
    text = "secret_password"
    
    # MD5 хеш
    md5_hash = helpers.hash_md5(text)
    print(f"MD5: {md5_hash}")
    
    # SHA256 хеш
    sha_hash = helpers.hash_sha256(text)
    print(f"SHA256: {sha_hash}")


# ============================================================================
# ПРИМЕРЫ DSL_INTEGRATION МОДУЛЯ
# ============================================================================

# ============================================================================
# ПРИКЛАД 11: Простий DSL скрипт
# ============================================================================
def example_11_simple_dsl():
    """Виконати простий DSL скрипт"""
    from plugins.dsl_integration import create_dsl_system
    
    context, executor = create_dsl_system()
    
    script = """
    set(name, "Іван")
    set(age, 25)
    print("Привіт", $name)
    print("Ваш вік:", $age)
    """
    
    success = executor.execute_script(script)
    print(f"Результат: {success}")
    print(f"Вивід: {context.output}")


# ============================================================================
# ПРИКЛАД 12: DSLBuilder з методами ланцюжками
# ============================================================================
def example_12_dsl_builder():
    """Побудувати DSL скрипт через builder"""
    from plugins.dsl_integration import DSLBuilder
    
    script = DSLBuilder() \
        .add_comment("Автоматизація з DSL") \
        .set_var("user", "Марія") \
        .set_var("points", 100) \
        .print_msg("Привіт", "$user") \
        .sleep(0.5) \
        .print_msg("Ви маєте", "$points", "очків") \
        .build()
    
    print("DSL скрипт:")
    print(script)


# ============================================================================
# ПРИКЛАД 13: Комбінація helpers + automation через DSL
# ============================================================================
def example_13_dsl_with_automation():
    """Використовувати automation модуль через DSL"""
    from plugins.dsl_integration import create_dsl_system
    
    context, executor = create_dsl_system()
    
    script = """
    # Встановити координати
    set(x_pos, 500)
    set(y_pos, 300)
    
    # Записати у лог
    print("Переміщую мишу на позицію $x_pos,$y_pos")
    
    # Клацнути на позицію (якщо automation модуль інтегрований)
    # click($x_pos, $y_pos)
    
    print("Завдання виконано")
    """
    
    executor.execute_script(script)
    print(f"Логи: {context.output}")


# ============================================================================
# ПРИКЛАД 14: Макроси в DSL
# ============================================================================
def example_14_dsl_macros():
    """Використовувати макроси в DSL"""
    from plugins.dsl_integration import create_dsl_system
    
    context, executor = create_dsl_system()
    
    script = """
    macro(greeting, "Привіт, ${name}! Ти маєш ${age} років.")
    
    set(user_name, "Петро")
    set(user_age, 30)
    
    print(expand(greeting, name=$user_name, age=$user_age))
    """
    
    executor.execute_script(script)
    print(f"Макрос розширено: {context.output}")


# ============================================================================
# ПРИКЛАД 15: Функції helpers через DSL
# ============================================================================
def example_15_dsl_helpers():
    """Використовувати функції helpers через DSL"""
    from plugins.dsl_integration import create_dsl_system
    
    context, executor = create_dsl_system()
    
    script = """
    set(text, "hello_world")
    set(number, "42")
    
    # Використовувати функції helpers
    print("to_int:", to_int($number))
    print("to_camel_case:", to_camel_case($text))
    print("format_bytes:", format_bytes(1024))
    
    # Валідація
    set(email, "user@example.com")
    assert(is_email($email), "Email не валідний")
    print("✓ Email валідний")
    """
    
    executor.execute_script(script)


# ============================================================================
# КОМБІНОВАНІ ПРИМЕРЫ (DSL + HELPERS + AUTOMATION)
# ============================================================================

# ============================================================================
# ПРИКЛАД 16: Повна автоматизація через DSL
# ============================================================================
def example_16_full_automation_dsl():
    """Повна автоматизація з DSL - симуляція"""
    from plugins.dsl_integration import create_dsl_system
    
    context, executor = create_dsl_system()
    
    script = """
    # Ініціалізація
    set(form_username, "input_user")
    set(form_password, "input_pass")
    
    print("=== Формула входу ===")
    print("Заповнюю форму входу...")
    
    # Формування даних
    set(user_email, "test@example.com")
    set(user_pass, "secure_password_123")
    
    # Валідація
    assert(is_email($user_email), "Email не валідний")
    
    print("✓ Email валідний:", $user_email)
    print("✓ Пароль встановлено (довжина:", count_chars($user_pass), ")")
    
    sleep(1)
    print("Форма заповнена успішно")
    """
    
    executor.execute_script(script)


# ============================================================================
# ПРИКЛАД 17: Обробка даних через DSL
# ============================================================================
def example_17_data_processing_dsl():
    """Обробити дані через DSL"""
    from plugins.dsl_integration import create_dsl_system
    import json
    
    context, executor = create_dsl_system()
    
    script = """
    set(text, "Hello World Example")
    
    # Трансформації
    print("Оригінал:", $text)
    print("Title Case:", to_title_case($text))
    print("Slug:", slugify($text))
    print("Реверс:", reverse_string($text))
    
    # Аналіз
    print("Слів:", count_words($text))
    print("Символів:", count_chars($text))
    """
    
    executor.execute_script(script)


# ============================================================================
# ПРИКЛАД 18: Кешування через DSL (розширене)
# ============================================================================
def example_18_caching_workflow():
    """Кешування в DSL робочому потоці"""
    from plugins.dsl_integration import create_dsl_system
    
    context, executor = create_dsl_system()
    
    script = """
    # Встановити дані
    set(user_id, "123")
    set(user_name, "Марія")
    set(user_role, "admin")
    
    print("Завантажу дані користувача з кешу...")
    print("ID:", $user_id)
    print("Ім'я:", $user_name)
    print("Роль:", $user_role)
    
    # Форматування результату
    print("Готово за:", format_time(0.5))
    """
    
    executor.execute_script(script)


# ============================================================================
# ПРИКЛАД 19: Обробка помилок через DSL
# ============================================================================
def example_19_error_handling_dsl():
    """Обробити помилки в DSL"""
    from plugins.dsl_integration import create_dsl_system
    
    context, executor = create_dsl_system()
    
    script = """
    set(password, "weak")
    
    print("Перевіряю пароль...")
    
    # Валідація довжини
    assert(has_length($password, min_len=8), "Пароль занадто короткий")
    
    print("✓ Пароль надійний")
    """
    
    success = executor.execute_script(script)
    
    if not success:
        print(f"Помилка: {context.error_log}")


# ============================================================================
# ПРИКЛАД 20: Конфіг файл у DSL форматі
# ============================================================================
def example_20_dsl_config_file():
    """Конфіг файл у DSL форматі"""
    from plugins.dsl_integration import create_dsl_system
    
    # Читаємо конфіг як DSL
    config_dsl = """
    # Конфіг приложення
    set(app_name, "AutoBot")
    set(app_version, "1.0.0")
    set(debug_mode, true)
    set(log_level, "INFO")
    set(timeout, 30)
    
    print("Завантажив конфіг для", $app_name, "версія", $app_version)
    """
    
    context, executor = create_dsl_system()
    executor.execute_script(config_dsl)
    
    print(f"Збережені змінні: {context.variables}")


# ============================================================================
# ЗАПУСК ПРИМЕРОВ
# ============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("Практичні приклади QoL модулів та DSL інтеграції")
    print("=" * 70)
    print("\nДоступні приклади:")
    print("  1. example_1_type_conversion() - Конвертування типів")
    print("  2. example_2_validation() - Валідація даних")
    print("  3. example_3_text_formatting() - Форматування текстів")
    print("  4. example_4_date_time_formatting() - Дата і час")
    print("  5. example_5_caching() - Кешування")
    print("  6. example_6_file_operations() - Робота з файлами")
    print("  7. example_7_string_utilities() - Утиліти для стрічок")
    print("  8. example_8_list_utilities() - Утиліти для списків")
    print("  9. example_9_dict_utilities() - Утиліти для словників")
    print("  10. example_10_hashing() - Хешування")
    print("  11. example_11_simple_dsl() - Простий DSL скрипт")
    print("  12. example_12_dsl_builder() - DSL Builder")
    print("  13. example_13_dsl_with_automation() - DSL + Automation")
    print("  14. example_14_dsl_macros() - Макроси в DSL")
    print("  15. example_15_dsl_helpers() - Helpers через DSL")
    print("  16. example_16_full_automation_dsl() - Повна автоматизація")
    print("  17. example_17_data_processing_dsl() - Обробка даних")
    print("  18. example_18_caching_workflow() - Кешування робочого потоку")
    print("  19. example_19_error_handling_dsl() - Обробка помилок")
    print("  20. example_20_dsl_config_file() - Конфіг файл DSL")
    print("\nДля запуску прикладу виклиціть функцію:")
    print("  python examples_qol.py")
