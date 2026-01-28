"""
Практичні приклади використання нових модулів
Приклади 1-25: Реальні сценарії автоматизації
"""

# ============================================================================
# ПРИКЛАД 1: Читання тексту з екрану
# ============================================================================
def example_1_read_screen_text():
    """Прочитати весь текст з екрану"""
    from plugins import ocr
    
    text = ocr.read_text_from_screen()
    print(f"Прочитано {len(text)} символів")
    print(text[:100])  # Перші 100 символів


# ============================================================================
# ПРИКЛАД 2: Пошук тексту на екрані
# ============================================================================
def example_2_find_text():
    """Знайти текст на екрані та кліцнути на нього"""
    from plugins import ocr, automation
    
    # Знайти кнопку "Зберегти"
    coords = ocr.find_text_on_screen("Зберегти")
    
    if coords:
        x, y, w, h = coords
        center_x = x + w // 2
        center_y = y + h // 2
        
        print(f"Кнопка 'Зберегти' знайдена на ({center_x}, {center_y})")
        automation.click(center_x, center_y)
    else:
        print("Кнопка 'Зберегти' не знайдена")


# ============================================================================
# ПРИКЛАД 3: Отримання координат текстових блоків
# ============================================================================
def example_3_text_blocks():
    """Отримати координати всіх текстових блоків на екрані"""
    from plugins import ocr
    
    boxes = ocr.get_text_boxes(lang='ukr')
    
    print(f"Знайдено {len(boxes)} текстових блоків")
    
    # Вивести перші 5 блоків
    for i, box in enumerate(boxes[:5]):
        print(f"\nБлок {i+1}:")
        print(f"  Текст: {box['text']}")
        print(f"  Позиція: ({box['x']}, {box['y']})")
        print(f"  Розмір: {box['w']}x{box['h']}")
        print(f"  Впевненість: {box['conf']}%")


# ============================================================================
# ПРИКЛАД 4: Чекання появи тексту
# ============================================================================
def example_4_wait_for_text():
    """Чекати поки на екрані з'явиться певний текст"""
    from plugins import ocr
    import time
    
    print("Чекаю появи тексту 'Завантаження...'")
    
    if ocr.wait_for_text("Завантаження", timeout=60, interval=1):
        print("✓ Текст з'явився!")
    else:
        print("✗ Таймаут - текст не з'явився")


# ============================================================================
# ПРИКЛАД 5: Аналіз кольорів пікселів
# ============================================================================
def example_5_pixel_colors():
    """Отримати колір пікселя та знайти всі пікселі цього кольору"""
    from plugins import ocr
    
    # Отримати колір певного пікселя
    r, g, b = ocr.get_pixel_color(500, 300)
    print(f"Колір пікселя на (500, 300): RGB({r}, {g}, {b})")
    
    # Знайти всі подібні пікселі на екрані
    color = (r, g, b)
    matches = ocr.find_color_on_screen(color, threshold=20)
    
    print(f"Знайдено {len(matches)} подібних пікселів")
    
    # Вивести перші 5 позицій
    for x, y in matches[:5]:
        print(f"  ({x}, {y})")


# ============================================================================
# ПРИКЛАД 6: Пошук на екрані та клацання
# ============================================================================
def example_6_find_and_click():
    """Знайти красну кнопку на екрані та клацнути на неї"""
    from plugins import ocr, automation
    
    red = (255, 0, 0)
    matches = ocr.find_color_on_screen(red, threshold=10)
    
    if matches:
        # Клацнути на першу знайдену позицію
        x, y = matches[0]
        print(f"Кліцаю на червону кнопку на ({x}, {y})")
        automation.click(x, y)


# ============================================================================
# ПРИКЛАД 7: Збереження скріншота
# ============================================================================
def example_7_save_screenshot():
    """Зберегти скріншот екрану"""
    from plugins import screen
    
    # Зберегти весь екран
    screen.save_screenshot("full_screen.png")
    print("✓ Скріншот екрану збережено")
    
    # Зберегти частину екрану (1024x768)
    screen.save_screenshot("region.png", region=(0, 0, 1024, 768))
    print("✓ Скріншот регіону збережено")


# ============================================================================
# ПРИКЛАД 8: Пошук зображення на екрані
# ============================================================================
def example_8_find_image():
    """Знайти шаблон зображення на екрані"""
    from plugins import screen, automation
    
    # Знайти кнопку за її зображенням
    coords = screen.find_image_on_screen("button.png", confidence=0.9)
    
    if coords:
        x, y = coords
        print(f"Кнопка знайдена на ({x}, {y})")
        automation.click(x, y)
    else:
        print("Кнопка не знайдена")


# ============================================================================
# ПРИКЛАД 9: Знаходження всіх входжень зображення
# ============================================================================
def example_9_find_all_images():
    """Знайти всі входження зображення на екрані"""
    from plugins import screen
    
    # Знайти всі іконки
    matches = screen.find_image_all("icon.png", confidence=0.85)
    
    print(f"Знайдено {len(matches)} іконок:")
    for i, (x, y) in enumerate(matches):
        print(f"  Іконка {i+1}: ({x}, {y})")


# ============================================================================
# ПРИКЛАД 10: Виявлення змін екрану
# ============================================================================
def example_10_detect_changes():
    """Порівняти два скріншоти та виявити зміни"""
    from plugins import screen
    from PIL import ImageGrab
    import time
    
    # Взяти перший скріншот
    img1 = ImageGrab.grab()
    print("Перший скріншот зроблений")
    
    # Чекати 2 секунди
    time.sleep(2)
    
    # Взяти другий скріншот
    img2 = ImageGrab.grab()
    print("Другий скріншот зроблений")
    
    # Порівняти
    has_changes, change_pct, diff_img = screen.detect_changes(img1, img2)
    
    print(f"Зміни виявлені: {has_changes}")
    print(f"Відсоток змін: {change_pct:.2f}%")
    
    # Зберегти зображення різниці
    if diff_img:
        diff_img.save("difference.png")


# ============================================================================
# ПРИКЛАД 11: Розділення екрану на сітку
# ============================================================================
def example_11_screen_grid():
    """Розділити екран на сітку 3x3 та аналізувати кожну ячейку"""
    from plugins import screen
    
    # Розділити на 3x3
    regions = screen.split_screen_grid(cols=3, rows=3)
    
    print(f"Екран розділено на {len(regions)} ячеек:")
    
    for name, (x1, y1, x2, y2) in regions.items():
        width = x2 - x1
        height = y2 - y1
        print(f"  {name}: {width}x{height} на ({x1}, {y1})")
        
        # Отримати домінуючий колір кожної ячейки
        color = screen.get_dominant_color((x1, y1, x2, y2))
        print(f"    Домінуючий колір: RGB{color}")


# ============================================================================
# ПРИКЛАД 12: Очікування зміни екрану
# ============================================================================
def example_12_wait_for_change():
    """Чекати поки екран змінюється"""
    from plugins import screen
    
    print("Чекаю зміни екрану...")
    
    if screen.wait_for_screen_change(timeout=30, threshold=20):
        print("✓ Екран змінився!")
    else:
        print("✗ Таймаут - екран не змінився")


# ============================================================================
# ПРИКЛАД 13: Очікування появи зображення
# ============================================================================
def example_13_wait_for_image():
    """Чекати поки певне зображення з'явиться на екрані"""
    from plugins import screen
    
    print("Чекаю появи діалогу...")
    
    if screen.wait_for_image("dialog.png", timeout=60):
        print("✓ Діалог з'явився!")
    else:
        print("✗ Таймаут - діалог не з'явився")


# ============================================================================
# ПРИКЛАД 14: Запис макросу
# ============================================================================
def example_14_record_macro():
    """Записати послідовність дій у макрос"""
    from plugins.recorder import Recorder
    import time
    
    recorder = Recorder("fill_form")
    recorder.start_recording()
    
    # Записати дії
    print("Запис макросу розпочатий...")
    
    recorder.record_mouse_move(100, 100)
    time.sleep(0.1)
    
    recorder.record_mouse_click(100, 100, button="left")
    time.sleep(0.1)
    
    recorder.record_text("Іван Петренко")
    time.sleep(0.1)
    
    recorder.record_key_press("Tab")
    time.sleep(0.1)
    
    recorder.record_text("ivan@example.com")
    time.sleep(0.1)
    
    recorder.record_mouse_click(500, 400, button="left")  # Кнопка "Зберегти"
    
    recorder.stop_recording()
    
    # Зберегти макрос
    recorder.save("macros/form_filler.json")
    print(f"✓ Макрос збережено: {len(recorder)} дій")


# ============================================================================
# ПРИКЛАД 15: Відтворення макросу
# ============================================================================
def example_15_playback_macro():
    """Завантажити і відтворити записаний макрос"""
    from plugins.recorder import Recorder
    
    recorder = Recorder()
    
    # Завантажити макрос
    if recorder.load("macros/form_filler.json"):
        print(f"Макрос завантажено: {recorder}")
        
        # Показати статистику
        stats = recorder.get_statistics()
        print(f"Всього дій: {stats['total_actions']}")
        print(f"Загальна тривалість: {stats['total_duration']:.2f} сек")
        
        # Відтворити макрос
        print("Починаю відтворення...")
        recorder.playback(loop_count=1, speed=1.0)
        print("✓ Відтворення завершено")


# ============================================================================
# ПРИКЛАД 16: Редагування макросу
# ============================================================================
def example_16_edit_macro():
    """Редагувати записаний макрос"""
    from plugins.recorder import Recorder
    
    recorder = Recorder()
    recorder.load("macros/form_filler.json")
    
    print(f"Вихідний макрос: {len(recorder)} дій")
    
    # Показати першу дію
    print(f"Дія 0: {recorder[0].to_dict()}")
    
    # Редагувати першу дію
    recorder.edit_action(0, x=200, y=200)
    print(f"✓ Дія 0 відредагована")
    
    # Видалити дію
    if len(recorder) > 3:
        recorder.delete_action(3)
        print(f"✓ Дія 3 видалена")
    
    print(f"Оновлений макрос: {len(recorder)} дій")
    
    # Зберегти зміни
    recorder.save("macros/form_filler_edited.json")


# ============================================================================
# ПРИКЛАД 17: Асинхронне відтворення макросу
# ============================================================================
def example_17_async_playback():
    """Відтворити макрос у фоновому потоці"""
    from plugins.recorder import Recorder
    import time
    
    recorder = Recorder()
    recorder.load("macros/form_filler.json")
    
    # Почати асинхронне відтворення
    print("Стартую асинхронне відтворення...")
    thread = recorder.playback_async(loop_count=3, speed=1.5)
    
    # Робити щось в основному потоці
    print("Робоча нить активна, очікування завершення...")
    thread.join()
    
    print("✓ Асинхронне відтворення завершено")


# ============================================================================
# ПРИКЛАД 18: Основний сенсор подій
# ============================================================================
def example_18_sensor_basics():
    """Створити сенсор та додати обробник подій"""
    from plugins.sensor import Sensor, EventType
    import time
    
    sensor = Sensor("my_sensor")
    
    # Додати обробник для змін екрану
    def on_screen_change(event):
        print(f"[ПОДІЯ] Екран змінився: {event.data}")
    
    sensor.add_listener(EventType.SCREEN_CHANGE, on_screen_change)
    
    # Почати моніторинг
    print("Моніторинг розпочатий...")
    sensor.start_monitoring(check_interval=1.0)
    
    # Моніторити протягом 10 секунд
    time.sleep(10)
    
    # Зупинити моніторинг
    sensor.stop_monitoring()
    
    # Вивести статистику
    stats = sensor.get_event_statistics()
    print(f"Подій виявлено: {stats}")


# ============================================================================
# ПРИКЛАД 19: Фільтрація подій
# ============================================================================
def example_19_event_filtering():
    """Додати обробник з фільтром подій"""
    from plugins.sensor import Sensor, EventType
    import time
    
    sensor = Sensor("filtered_sensor")
    
    # Обробник з фільтром - тільки великі зміни
    def on_major_change(event):
        print(f"✓ Значна зміна екрану: {event.data['change_percentage']:.2f}%")
    
    def filter_large_changes(event):
        return event.data.get('change_percentage', 0) > 5.0
    
    sensor.add_listener(
        EventType.SCREEN_CHANGE,
        on_major_change,
        filter_func=filter_large_changes
    )
    
    sensor.start_monitoring(check_interval=0.5)
    time.sleep(10)
    sensor.stop_monitoring()


# ============================================================================
# ПРИКЛАД 20: Експорт подій
# ============================================================================
def example_20_export_events():
    """Експортувати зібрані подій у JSON файл"""
    from plugins.sensor import Sensor, EventType
    import time
    
    sensor = Sensor("export_sensor")
    
    def on_event(event):
        pass  # Просто записуємо
    
    sensor.add_listener(EventType.SCREEN_CHANGE, on_event)
    
    sensor.start_monitoring(check_interval=1.0, log_file="sensor.log")
    time.sleep(5)
    sensor.stop_monitoring()
    
    # Експортувати подій
    sensor.export_events("sensor_events.json")
    print(f"✓ {len(sensor.events_history)} подій експортовано")


# ============================================================================
# ПРИКЛАД 21: Таймер продуктивності
# ============================================================================
def example_21_simple_timer():
    """Використання таймера для вимірювання часу операцій"""
    from plugins.performance import SimpleTimer
    import time
    
    # Вимірювання часу блоку коду
    with SimpleTimer("операція_1") as timer:
        time.sleep(1.5)
    
    print(timer)  # Виведе: операція_1: 1.5023 сек
    
    # Ручний таймер
    timer2 = SimpleTimer("операція_2")
    timer2.start()
    
    time.sleep(0.8)
    
    elapsed = timer2.stop()
    print(f"операція_2: {elapsed:.4f} сек")


# ============================================================================
# ПРИКЛАД 22: Декоратор для вимірювання часу
# ============================================================================
def example_22_measure_time():
    """Використання декоратора для вимірювання часу функції"""
    from plugins.performance import measure_time
    import time
    
    @measure_time
    def slow_function():
        """Повільна функція"""
        time.sleep(2)
        return "результат"
    
    result = slow_function()
    # Виведе: ✓ slow_function: 2.0034 сек


# ============================================================================
# ПРИКЛАД 23: Кешування з TTL
# ============================================================================
def example_23_caching():
    """Використання кешування результатів функції"""
    from plugins.performance import cache
    import time
    
    @cache(ttl=5.0)
    def expensive_calc(x, y):
        print(f"Обчислюю {x} + {y}...")
        time.sleep(1)
        return x + y
    
    # Перший виклик - реальне обчислення
    result1 = expensive_calc(10, 20)  # 1 сек
    print(f"Результат 1: {result1}")
    
    # Другий виклик - з кешу
    result2 = expensive_calc(10, 20)  # Миттєво
    print(f"Результат 2: {result2}")
    
    # Третій виклик з іншими параметрами
    result3 = expensive_calc(5, 15)  # 1 сек
    print(f"Результат 3: {result3}")


# ============================================================================
# ПРИКЛАД 24: Логер з рівнями
# ============================================================================
def example_24_logging():
    """Використання логера з різними рівнями"""
    from plugins.performance import Logger, LogLevel
    
    logger = Logger(
        "my_app",
        log_file="app.log",
        min_level=LogLevel.DEBUG
    )
    
    # Логувати повідомлення різних рівнів
    logger.debug("Деталь для налагодження")
    logger.info("Інформаційне повідомлення")
    logger.warning("Попередження")
    logger.error("Критична помилка")
    
    # Отримати повідомлення певного рівня
    errors = logger.get_messages(level=LogLevel.ERROR)
    print(f"Всього помилок: {len(errors)}")


# ============================================================================
# ПРИКЛАД 25: Асинхронний пул задач
# ============================================================================
def example_25_async_pool():
    """Паралельне обробка задач з пулом"""
    from plugins.performance import AsyncTaskPool
    import time
    
    def process_item(item):
        time.sleep(0.5)
        return f"оброблено_{item}"
    
    # Створити пул з 4 робітниками
    pool = AsyncTaskPool(max_workers=4)
    
    # Додати 10 задач
    items = list(range(10))
    for item in items:
        pool.submit(process_item, item)
    
    print(f"Додано {len(items)} задач до пулу...")
    
    # Чекати завершення (має зайняти ~2.5 сек замість 5 сек)
    start = time.time()
    results = pool.wait_all(timeout=30)
    elapsed = time.time() - start
    
    print(f"✓ Оброблено {len(results)} задач за {elapsed:.1f} сек")
    
    pool.shutdown()


# ============================================================================
# КОМБІНОВАНИЙ ПРИКЛАД: Повна автоматизація з усіма модулями
# ============================================================================
def example_combined_full_automation():
    """
    Комбінований приклад: записуємо макрос, потім монікоримо екран,
    чекаємо на змінення і відтворюємо
    """
    from plugins import automation, ocr, screen
    from plugins.recorder import Recorder
    from plugins.sensor import Sensor, EventType
    from plugins.performance import SimpleTimer, Logger
    import time
    
    logger = Logger("automation", min_level=0)
    
    # 1. Записати макрос
    logger.info("=== ЕТАП 1: Запис макросу ===")
    
    with SimpleTimer("запис_макросу") as timer:
        recorder = Recorder("auto_fill")
        recorder.start_recording()
        
        # Записуємо дії
        recorder.record_mouse_move(500, 300)
        recorder.record_mouse_click(500, 300)
        recorder.record_text("Тестові дані")
        
        recorder.stop_recording()
        recorder.save("macros/auto_fill.json")
    
    print(timer)
    
    # 2. Запустити сенсор для моніторингу
    logger.info("=== ЕТАП 2: Моніторинг екрану ===")
    
    sensor = Sensor()
    event_count = 0
    
    def on_change(event):
        nonlocal event_count
        event_count += 1
    
    sensor.add_listener(EventType.SCREEN_CHANGE, on_change)
    sensor.start_monitoring(check_interval=0.5)
    
    # 3. Чекаємо зміну екрану і відтворюємо макрос
    logger.info("=== ЕТАП 3: Очікування зміни ===")
    
    if screen.wait_for_screen_change(timeout=30):
        logger.info("Екран змінився, запускаю макрос...")
        
        # Відтворити макрос
        recorder.playback(loop_count=1, speed=1.0)
        
        logger.info(f"Макрос виконаний за {recorder.get_statistics()['total_duration']:.2f} сек")
    
    # 4. Зупинити сенсор
    sensor.stop_monitoring()
    logger.info(f"Всього подій виявлено: {event_count}")
    
    # 5. Експортувати результати
    logger.info("=== ЕТАП 4: Експорт ===")
    sensor.export_events("final_events.json")
    logger.info("Готово!")


# ============================================================================
# ЗАПУСК ПРИКЛАДІВ
# ============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("Практичні приклади нових модулів")
    print("=" * 70)
    print("\nДоступні приклади:")
    print("  1. example_1_read_screen_text() - Читання тексту з екрану")
    print("  2. example_2_find_text() - Пошук та клацання тексту")
    print("  3. example_3_text_blocks() - Отримання координат текстових блоків")
    print("  4. example_4_wait_for_text() - Очікування появи тексту")
    print("  5. example_5_pixel_colors() - Аналіз кольорів")
    print("  6. example_6_find_and_click() - Пошук та клацання за кольором")
    print("  7. example_7_save_screenshot() - Збереження скріншотів")
    print("  8. example_8_find_image() - Пошук зображення")
    print("  9. example_9_find_all_images() - Пошук всіх входжень")
    print("  10. example_10_detect_changes() - Виявлення змін")
    print("  11. example_11_screen_grid() - Розділення екрану на сітку")
    print("  12. example_12_wait_for_change() - Очікування зміни екрану")
    print("  13. example_13_wait_for_image() - Очікування появи зображення")
    print("  14. example_14_record_macro() - Запис макросу")
    print("  15. example_15_playback_macro() - Відтворення макросу")
    print("  16. example_16_edit_macro() - Редагування макросу")
    print("  17. example_17_async_playback() - Асинхронне відтворення")
    print("  18. example_18_sensor_basics() - Основи сенсора")
    print("  19. example_19_event_filtering() - Фільтрація подій")
    print("  20. example_20_export_events() - Експорт подій")
    print("  21. example_21_simple_timer() - Таймер продуктивності")
    print("  22. example_22_measure_time() - Декоратор для вимірювання")
    print("  23. example_23_caching() - Кешування результатів")
    print("  24. example_24_logging() - Логування з рівнями")
    print("  25. example_25_async_pool() - Асинхронний пул задач")
    print("  combined. example_combined_full_automation() - Повна автоматизація")
    print("\nДля запуску прикладу виклиціть функцію:")
    print("  python examples_new_modules.py")
