"""
ШВИДКИЙ ПОСІБНИК: ПЕРШІ КРОКИ З QOL МОДУЛЯМИ
Для нових користувачів - все що потребно знати для старту
"""

# ============================================================================
# 1. ВСТАНОВЛЕННЯ (2 ХВИЛИНИ)
# ============================================================================

"""
Крок 1: Завантажте файли
  - helpers.py в папку plugins/
  - dsl_integration.py в папку plugins/

Крок 2: Перевірте встановлення
  python -c "from plugins import helpers; print('✓ helpers готовий')"
  python -c "from plugins.dsl_integration import create_dsl_system; print('✓ DSL готовий')"

Крок 3: Готово!
  Ви можете використовувати обидва модулі без додаткових встановлень пакетів
"""

# ============================================================================
# 2. ПЕРША АВТОМАТИЗАЦІЯ З HELPERS (5 ХВИЛИН)
# ============================================================================

def first_automation_example():
    """Перший приклад - чотири операції з helpers"""
    from plugins import helpers
    
    # 1. Конвертування - рядок в число
    user_age_str = "25"
    user_age = helpers.to_int(user_age_str)
    print(f"Вік користувача: {user_age} років")
    
    # 2. Валідація - перевірка email
    email = "john@example.com"
    if helpers.is_email(email):
        print(f"✓ Email валідний: {email}")
    
    # 3. Форматування - текст в slug
    blog_title = "My Awesome Blog Post!"
    slug = helpers.slugify(blog_title)
    print(f"Slug для URL: {slug}")
    
    # 4. Файл - запис та читання
    helpers.write_file("example.txt", "Привіт, світе!")
    content = helpers.read_file("example.txt")
    print(f"Прочитаний файл: {content}")


# ============================================================================
# 3. ПЕРША DSL АВТОМАТИЗАЦІЯ (5 ХВИЛИН)
# ============================================================================

def first_dsl_automation_example():
    """Перший приклад DSL - напишемо сценарій входу"""
    from plugins.dsl_integration import create_dsl_system
    
    # Створимо DSL систему
    context, executor = create_dsl_system()
    
    # Напишемо простий сценарій
    dsl_script = """
    # Встановимо дані користувача
    set(username, "user@example.com")
    set(password, "secret123")
    
    # Перевіримо дані
    print("=== Вхід користувача ===")
    print("Логін:", $username)
    
    # Валідуємо email
    assert(is_email($username), "Username має бути email")
    
    # Перевіримо довжину пароля
    assert(has_length($password, min_len=8), "Пароль занадто короткий")
    
    print("✓ Дані валідні, виконуємо вхід...")
    sleep(1)
    print("✓ Ви успішно увійшли!")
    """
    
    # Виконаємо скрипт
    executor.execute_script(dsl_script)
    
    # Виведемо результати
    print("\nВивід скрипту:")
    for line in context.output:
        print(f"  {line}")


# ============================================================================
# 4. НАЙПОПУЛЯРНІШІ ФУНКЦІЇ HELPERS (ШПАРГАЛКА)
# ============================================================================

def popular_functions_cheatsheet():
    """Шпаргалка найпопулярніших функцій"""
    from plugins import helpers
    
    print("=" * 60)
    print("ШПАРГАЛКА: НАЙПОПУЛЯРНІШІ ФУНКЦІЇ HELPERS")
    print("=" * 60)
    
    # Конвертування
    print("\n1. КОНВЕРТУВАННЯ:")
    print(f"  to_int('42') = {helpers.to_int('42')}")
    print(f"  to_bool('true') = {helpers.to_bool('true')}")
    print(f"  to_list('один') = {helpers.to_list('один')}")
    
    # Валідація
    print("\n2. ВАЛІДАЦІЯ:")
    print(f"  is_email('test@ex.com') = {helpers.is_email('test@ex.com')}")
    print(f"  is_phone('+380961234567') = {helpers.is_phone('+380961234567')}")
    
    # Форматування
    print("\n3. ФОРМАТУВАННЯ:")
    print(f"  to_camel_case('hello_world') = {helpers.to_camel_case('hello_world')}")
    print(f"  slugify('My Blog!') = {helpers.slugify('My Blog!')}")
    print(f"  format_bytes(1536) = {helpers.format_bytes(1536)}")
    
    # Файли
    print("\n4. ФАЙЛИ:")
    helpers.write_file("test.txt", "Hello")
    content = helpers.read_file("test.txt")
    print(f"  write_file + read_file = {content}")
    helpers.delete_file("test.txt")
    
    # Списки
    print("\n5. ОПЕРАЦІЇ ЗІ СПИСКАМИ:")
    print(f"  unique([1,2,2,3]) = {helpers.unique([1,2,2,3])}")
    print(f"  chunk_list([1,2,3,4], 2) = {helpers.chunk_list([1,2,3,4], 2)}")
    
    print("\n" + "=" * 60)


# ============================================================================
# 5. НАЙПОПУЛЯРНІШІ DSL КОМАНДИ (ШПАРГАЛКА)
# ============================================================================

def dsl_commands_cheatsheet():
    """Шпаргалка найпопулярніших DSL команд"""
    from plugins.dsl_integration import create_dsl_system
    
    context, executor = create_dsl_system()
    
    print("\n" + "=" * 60)
    print("ШПАРГАЛКА: DSL КОМАНДИ")
    print("=" * 60)
    
    script = """
    # 1. ЗМІННІ
    set(name, "Іван")
    set(age, 25)
    
    # 2. ВИВІД
    print("Ім'я:", $name)
    print("Вік:", $age)
    
    # 3. УМОВИ
    if($age >= 18,
      print("Дорослий"),
      print("Дитина")
    )
    
    # 4. ЦИКЛИ
    for(i, [1,2,3],
      print("Число:", $i)
    )
    
    # 5. ЗАТРИМКА
    sleep(0.5)
    
    # 6. МАКРОСИ
    macro(greet, "Привіт, ${name}!")
    expand(greet, name=$name)
    
    # 7. ФУНКЦІЇ HELPERS
    set(text, "hello_world")
    print("camelCase:", to_camel_case($text))
    """
    
    executor.execute_script(script)
    
    print("\nВесь вивід:")
    for line in context.output:
        print(f"  {line}")
    
    print("\n" + "=" * 60)


# ============================================================================
# 6. КЕЙСИ ВИКОРИСТАННЯ (РЕАЛЬНІ ПРИКЛАДИ)
# ============================================================================

def use_case_1_validate_form():
    """Кейс 1: Валідація форми реєстрації"""
    from plugins import helpers
    
    print("\n" + "=" * 60)
    print("КЕЙС 1: ВАЛІДАЦІЯ ФОРМИ РЕЄСТРАЦІЇ")
    print("=" * 60)
    
    # Дані з форми
    form_data = {
        "email": "john@example.com",
        "phone": "+380961234567",
        "password": "SecurePass123!",
        "age": "25"
    }
    
    # Валідуємо кожне поле
    errors = []
    
    if not helpers.is_email(form_data["email"]):
        errors.append("Email невалідний")
    
    if not helpers.is_phone(form_data["phone"]):
        errors.append("Телефон невалідний")
    
    if not helpers.has_length(form_data["password"], min_len=8):
        errors.append("Пароль занадто короткий")
    
    age = helpers.to_int(form_data["age"])
    if age < 18:
        errors.append("Користувач має бути старше 18")
    
    # Результат
    if errors:
        print("❌ Помилки при валідації:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Форма валідна! Все готово для реєстрації.")


def use_case_2_log_file_processing():
    """Кейс 2: Обробка лог файлу"""
    from plugins import helpers
    
    print("\n" + "=" * 60)
    print("КЕЙС 2: ОБРОБКА ЛОГ ФАЙЛУ")
    print("=" * 60)
    
    # Створимо лог файл
    log_content = """
    [INFO] Сервер запущено
    [ERROR] Помилка при з'єднанні з БД
    [INFO] Перепідключення...
    [INFO] Успішно підключено
    [WARNING] Повільна відповідь
    [INFO] Операція завершена
    """
    
    helpers.write_file("app.log", log_content)
    
    # Обробляємо лог
    lines = helpers.read_lines("app.log")
    
    error_count = len([l for l in lines if "[ERROR]" in l])
    warning_count = len([l for l in lines if "[WARNING]" in l])
    info_count = len([l for l in lines if "[INFO]" in l])
    
    print(f"Статистика лога:")
    print(f"  [INFO]:    {info_count}")
    print(f"  [ERROR]:   {error_count}")
    print(f"  [WARNING]: {warning_count}")
    
    # Розмір файлу
    size = helpers.file_size("app.log")
    print(f"  Розмір: {helpers.format_bytes(size)}")
    
    helpers.delete_file("app.log")


def use_case_3_dsl_workflow():
    """Кейс 3: Складний робочий процес з DSL"""
    from plugins.dsl_integration import create_dsl_system
    
    print("\n" + "=" * 60)
    print("КЕЙС 3: СКЛАДНИЙ РОБОЧИЙ ПРОЦЕС З DSL")
    print("=" * 60)
    
    context, executor = create_dsl_system()
    
    script = """
    # Робочий процес: обробка замовлень
    
    set(order_id, "ORD-2025-001")
    set(customer_name, "Марія Петренко")
    set(total_amount, 5999.99)
    
    print("=== ОБРОБКА ЗАМОВЛЕННЯ ===")
    print("ID замовлення:", $order_id)
    print("Замовник:", $customer_name)
    print("Сума:", format_bytes(to_int($total_amount)), "грн")
    
    # Валідація
    assert(is_email("maria@example.com"), "Email замовника невалідний")
    assert($total_amount > 0, "Сума має бути позитивною")
    
    # Стани обробки
    set(states, to_list(["Очікування", "Обробка", "Доставка", "Завершено"]))
    
    print("\\nПроцес обробки:")
    for(state, $states,
      print("  → " $state)
      sleep(0.2)
    )
    
    print("\\n✓ Замовлення успішно обробити!")
    """
    
    executor.execute_script(script)
    
    print("\nРезультат:")
    for line in context.output:
        print(f"  {line}")


# ============================================================================
# 7. ПОРІВНЯННЯ: HELPERS VS DSL
# ============================================================================

def comparison_helpers_vs_dsl():
    """Порівняння - коли використовувати что"""
    
    print("\n" + "=" * 70)
    print("ПОРІВНЯННЯ: HELPERS VS DSL")
    print("=" * 70)
    
    comparison = """
    HELPERS.PY:
    ✓ Використовуйте для:
      - Конвертування типів даних
      - Валідації вводу
      - Форматування для виводу
      - Роботи з файлами
      - Простих операцій зі стрічками/списками
      - Кешування результатів
    
    ✓ Приклад:
      email = "user@example.com"
      if helpers.is_email(email):
          print(f"✓ {email} валідний")
    
    ---
    
    DSL_INTEGRATION.PY:
    ✓ Використовуйте для:
      - Складних сценаріїв з умовами/циклами
      - Автоматизації рутинних дій
      - Скриптів замість конфігів
      - Читаємого коду для не-програмістів
      - Макросів та переносимих сценаріїв
      - Інтеграції множини модулів
    
    ✓ Приклад:
      set(email, "user@example.com")
      assert(is_email($email), "Email невалідний")
      print("✓", $email, "валідний")
    
    ---
    
    КОМБІНОВАНО:
    ✓ Найбільш потужна комбінація:
      1. Обробляємо дані в Python з helpers
      2. Запускаємо складну логіку через DSL скрипт
      3. Результати зберігаємо через helpers.write_file()
    """
    
    print(comparison)


# ============================================================================
# 8. ПОМИЛКИ ДЛЯ УНИКНЕННЯ
# ============================================================================

def common_mistakes():
    """Частові помилки та як їх уникнути"""
    
    print("\n" + "=" * 60)
    print("ЧАСТОВІ ПОМИЛКИ ДЛЯ УНИКНЕННЯ")
    print("=" * 60)
    
    mistakes = """
    ❌ ПОМИЛКА 1: Забути імпортувати модуль
    ❌ from plugins import helpers
    ✓ from plugins import helpers
    
    ---
    
    ❌ ПОМИЛКА 2: Використовувати 'to_string' замість конкатенації в Python
    ❌ result = to_string(x) + " more"
    ✓ result = str(x) + " more"
    ✓ або в DSL: print($x, "more")
    
    ---
    
    ❌ ПОМИЛКА 3: Забути встановити дані у контекст перед DSL
    ❌ executor.execute_line('print($data)')  # $data буде None
    ✓ context.set_var("data", value)
    ✓ executor.execute_line('print($data)')
    
    ---
    
    ❌ ПОМИЛКА 4: Максимальна довжина URL slug (200+ символів)
    ❌ slug = helpers.slugify("дуже довгий текст...")  # Буде дуже довгим
    ✓ slug = helpers.slugify(text)[:50]  # Обрізати до 50 символів
    
    ---
    
    ❌ ПОМИЛКА 5: Не закривати файли після запису
    ❌ helpers.write_file("data.json", content)  # Python закриває автоматично ✓
    
    ---
    
    ❌ ПОМИЛКА 6: Забути TTL при використанні кешу
    ❌ cache = helpers.SimpleCache()  # Нескінченний TTL
    ✓ cache = helpers.SimpleCache(ttl=300)  # 5 хвилин
    
    """
    
    print(mistakes)


# ============================================================================
# 9. ТЕСТУВАННЯ ВАШОЇ ІНСТАЛЯЦІЇ
# ============================================================================

def test_installation():
    """Тест - перевірити що все встановлено правильно"""
    
    print("\n" + "=" * 60)
    print("ТЕСТ ІНСТАЛЯЦІЇ")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Тест 1: Import helpers
    tests_total += 1
    try:
        from plugins import helpers
        print("✓ Тест 1: helpers.py імпортовано успішно")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Тест 1: Помилка при імпорті helpers - {e}")
    
    # Тест 2: Import dsl_integration
    tests_total += 1
    try:
        from plugins.dsl_integration import create_dsl_system
        print("✓ Тест 2: dsl_integration.py імпортовано успішно")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Тест 2: Помилка при імпорті dsl_integration - {e}")
    
    # Тест 3: Test helpers functions
    tests_total += 1
    try:
        from plugins import helpers
        assert helpers.to_int("42") == 42
        assert helpers.to_bool("true") == True
        assert helpers.is_email("test@example.com") == True
        print("✓ Тест 3: Функції helpers працюють")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Тест 3: Помилка при тестуванні helpers - {e}")
    
    # Тест 4: Test DSL execution
    tests_total += 1
    try:
        from plugins.dsl_integration import create_dsl_system
        context, executor = create_dsl_system()
        executor.execute_script("set(x, 42)\nprint($x)")
        assert len(context.output) > 0
        print("✓ Тест 4: DSL виконується успішно")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Тест 4: Помилка при тестуванні DSL - {e}")
    
    # Підсумок
    print(f"\n{'=' * 60}")
    print(f"РЕЗУЛЬТАТ: {tests_passed}/{tests_total} тестів пройдено")
    
    if tests_passed == tests_total:
        print("✓ Всі тести пройдені! Інсталяція успішна!")
    else:
        print(f"❌ {tests_total - tests_passed} тестів не пройдено")


# ============================================================================
# ГОЛОВНА ФУНКЦІЯ - ЗАПУСТИ ЦЕ ДЛЯ НАВЧАННЯ
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("\n")
    print("╔" + "=" * 70 + "╗")
    print("║" + " ШВИДКИЙ ПОСІБНИК: QoL МОДУЛІ - ПЕРШІ КРОКИ ".center(70) + "║")
    print("╚" + "=" * 70 + "╝")
    
    options = {
        "1": ("Перша автоматизація з helpers", first_automation_example),
        "2": ("Перша DSL автоматизація", first_dsl_automation_example),
        "3": ("Шпаргалка helpers функцій", popular_functions_cheatsheet),
        "4": ("Шпаргалка DSL команд", dsl_commands_cheatsheet),
        "5": ("Кейс 1: Валідація форми", use_case_1_validate_form),
        "6": ("Кейс 2: Обробка логів", use_case_2_log_file_processing),
        "7": ("Кейс 3: DSL робочий процес", use_case_3_dsl_workflow),
        "8": ("Порівняння: helpers vs DSL", comparison_helpers_vs_dsl),
        "9": ("Частові помилки", common_mistakes),
        "0": ("Тест інсталяції", test_installation),
    }
    
    print("\nВиберіть що вивчити:")
    for key, (desc, _) in options.items():
        print(f"  {key}. {desc}")
    print("  Q. Вихід")
    
    print("\nДля запуску прикладу:")
    print("  python -c \"from QUICKSTART_QOL import first_automation_example; first_automation_example()\"")
    print("  або")
    print("  python QUICKSTART_QOL.py")
