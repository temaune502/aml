"""
Приклади використання автоматизації консолі та системи

Цей файл містить практичні приклади роботи з 4 новими модулями:
- console_automation.py - запуск команд та обробка виводу
- powershell_executor.py - спеціалізовані PowerShell операції
- system_monitor.py - моніторинг ресурсів системи
- windows_automation.py - Windows-специфічні операції
"""

from plugins.console_automation import (
    ConsoleAutomation, run_cmd, run_powershell, run_python
)
from plugins.powershell_executor import (
    PowerShellExecutor, ps_run, ps_get_processes, ps_stop_process
)
from plugins.system_monitor import (
    SystemMonitor, get_system_metrics, get_top_processes, kill_process_by_name
)
from plugins.windows_automation import (
    WindowsAutomation, get_service_status, start_service, stop_service
)
import time


def example_1_basic_commands():
    """Приклад 1: Базові команди консолі"""
    print("=" * 60)
    print("ПРИКЛАД 1: Базові команди консолі")
    print("=" * 60)
    
    # Отримати версію Python
    result = run_python('import sys; print(f"Python {sys.version}")')
    print(f"✓ Python версія:\n{result.stdout}\n")
    
    # Отримати поточну директорію
    result = run_cmd('cd')
    print(f"✓ Поточна директорія:\n{result.stdout}\n")
    
    # Отримати список файлів
    result = run_powershell('Get-ChildItem | Select-Object Name | ConvertTo-Json')
    print(f"✓ Список файлів (return code: {result.return_code})\n")


def example_2_command_parsing():
    """Приклад 2: Парсинг результатів команд"""
    print("=" * 60)
    print("ПРИКЛАД 2: Парсинг результатів команд")
    print("=" * 60)
    
    automation = ConsoleAutomation()
    
    # Отримати список процесів та спарсити таблицю
    result = automation.run_command('tasklist')
    lines = automation.parse_lines(result)
    print(f"✓ Знайдено {len(lines)} процесів")
    print(f"  Перші 3 процеси:")
    for line in lines[:3]:
        print(f"    {line}")
    print()


def example_3_async_execution():
    """Приклад 3: Асинхронне виконання команд"""
    print("=" * 60)
    print("ПРИКЛАД 3: Асинхронне виконання команд")
    print("=" * 60)
    
    automation = ConsoleAutomation()
    
    def on_output(line):
        print(f"  OUT: {line}")
    
    def on_error(line):
        print(f"  ERR: {line}")
    
    # Запустити команду асинхронно
    print("✓ Запуск команди Get-Process асинхронно...")
    process = automation.run_async(
        'Get-Process | Select-Object Name, Id | ConvertTo-Json',
        on_output=on_output,
        on_error=on_error,
        shell='powershell'
    )
    
    # Очікувати завершення
    process.wait(timeout=5)
    print(f"  Процес завершився з кодом: {process.returncode}\n")


def example_4_powershell_objects():
    """Приклад 4: Робота з PowerShell об'єктами"""
    print("=" * 60)
    print("ПРИКЛАД 4: Робота з PowerShell об'єктами")
    print("=" * 60)
    
    executor = PowerShellExecutor()
    
    # Отримати процеси
    processes = executor.get_processes(name_filter='explorer')
    print(f"✓ Знайдено процесів: {len(processes)}")
    for proc in processes[:3]:
        print(f"  {proc['Name']} (PID: {proc['Id']})")
    print()


def example_5_powershell_pipeline():
    """Приклад 5: PowerShell pipeline операції"""
    print("=" * 60)
    print("ПРИКЛАД 5: PowerShell pipeline операції")
    print("=" * 60)
    
    executor = PowerShellExecutor()
    
    # Pipeline: Get-Process | Where-Object | Sort-Object
    result = executor.pipeline(
        'Get-Process',
        'Where-Object {$_.WorkingSet -gt 50MB}',
        'Sort-Object WorkingSet -Descending',
        'Select-Object -First 3 Name,@{N="Memory(MB)";E={[math]::Round($_.WorkingSet/1MB)}}'
    )
    
    print(f"✓ Топ 3 процеси по пам'яті (> 50MB):")
    print(f"  {result.stdout}\n")


def example_6_system_metrics():
    """Приклад 6: Системні метрики"""
    print("=" * 60)
    print("ПРИКЛАД 6: Системні метрики")
    print("=" * 60)
    
    monitor = SystemMonitor()
    
    # Отримати метрики
    metrics = monitor.get_system_metrics()
    print(f"✓ Системні метрики:")
    print(f"  {metrics}\n")
    
    # Деталізована інформація
    cpu_info = monitor.get_cpu_info()
    mem_info = monitor.get_memory_info()
    
    print(f"✓ CPU:")
    print(f"  Cores: {cpu_info['count_logical']}")
    print(f"  Frequency: {cpu_info['frequency_current']:.1f} MHz")
    print(f"  Usage: {cpu_info['percent']}%")
    print()
    
    print(f"✓ Memory:")
    print(f"  Total: {mem_info['total'] / (1024**3):.1f} GB")
    print(f"  Available: {mem_info['available'] / (1024**3):.1f} GB")
    print(f"  Usage: {mem_info['percent']}%")
    print()


def example_7_process_monitoring():
    """Приклад 7: Моніторинг процесів"""
    print("=" * 60)
    print("ПРИКЛАД 7: Моніторинг процесів")
    print("=" * 60)
    
    monitor = SystemMonitor()
    
    # Отримати топ процесів
    top_procs = monitor.get_processes(sort_by='memory_percent', limit=5)
    
    print(f"✓ Топ 5 процесів по пам'яті:")
    for proc in top_procs:
        print(f"  {proc.name} (PID: {proc.pid})")
        print(f"    RAM: {proc.memory_percent:.1f}% | CPU: {proc.cpu_percent:.1f}%")
    print()


def example_8_alerts():
    """Приклад 8: Алерти при перевищенні порогів"""
    print("=" * 60)
    print("ПРИКЛАД 8: Алерти при перевищенні порогів")
    print("=" * 60)
    
    # Встановити низькі пороги для демонстрації
    monitor = SystemMonitor(alert_threshold={
        'cpu': 10,      # 10%
        'memory': 30,   # 30%
        'disk': 95      # 95%
    })
    
    # Зібрати метрики
    metrics = monitor.get_system_metrics()
    
    # Отримати алерти
    alerts = monitor.get_alerts()
    print(f"✓ Алерти (пороги встановлені низько для демо):")
    for alert in alerts[-3:]:
        print(f"  [{alert['timestamp']}]")
        print(f"    Тип: {alert['type'].upper()}")
        print(f"    Значення: {alert['value']:.1f}%")
        print(f"    Повідомлення: {alert['message']}")
    print()


def example_9_windows_services():
    """Приклад 9: Управління Windows сервісами"""
    print("=" * 60)
    print("ПРИКЛАД 9: Управління Windows сервісами")
    print("=" * 60)
    
    # Отримати кілька сервісів
    services = WindowsAutomation.get_services(name_filter='Windows')
    print(f"✓ Найдено {len(services)} сервісів з 'Windows' в імені:")
    for service in services[:3]:
        status = service.get('Status', 'Unknown')
        name = service.get('Name', 'Unknown')
        print(f"  {name}: {status}")
    print()


def example_10_registry():
    """Приклад 10: Робота з реєстром"""
    print("=" * 60)
    print("ПРИКЛАД 10: Робота з реєстром")
    print("=" * 60)
    
    # Прочитати значення з реєстру (сімейна ОС)
    value = WindowsAutomation.registry_read(
        'HKEY_CURRENT_USER\\Control Panel\\Desktop',
        'WallPaper'
    )
    
    if value:
        print(f"✓ Обійма: {value[:50]}...")
    else:
        print(f"✓ Обійма: (не встановлена)")
    print()


def example_11_task_scheduler():
    """Приклад 11: Управління завданнями Task Scheduler"""
    print("=" * 60)
    print("ПРИКЛАД 11: Управління завданнями Task Scheduler")
    print("=" * 60)
    
    # Отримати список завдань
    tasks = WindowsAutomation.get_tasks()
    print(f"✓ Всього завдань в системі: {len(tasks)}")
    
    if tasks:
        print(f"✓ Перші 3 завдання:")
        for task in tasks[:3]:
            name = task.get('TaskName', 'Unknown')
            print(f"  {name}")
    print()


def example_12_system_info():
    """Приклад 12: Інформація про систему"""
    print("=" * 60)
    print("ПРИКЛАД 12: Інформація про систему")
    print("=" * 60)
    
    # Інформація про комп'ютер
    sys_info = WindowsAutomation.get_system_info()
    print(f"✓ Інформація про комп'ютер:")
    for key, value in sys_info.items():
        print(f"  {key}: {value}")
    print()
    
    # Інформація про Windows
    win_info = WindowsAutomation.get_windows_info()
    print(f"✓ Інформація про Windows:")
    for key, value in win_info.items():
        print(f"  {key}: {value}")
    print()


def example_13_continuous_monitoring():
    """Приклад 13: Безперервний моніторинг"""
    print("=" * 60)
    print("ПРИКЛАД 13: Безперервний моніторинг (5 сек)")
    print("=" * 60)
    
    monitor = SystemMonitor()
    
    def on_metric(metrics):
        print(f"  [{metrics.timestamp}] {metrics}")
    
    def on_alert(alert):
        print(f"  🚨 ALERT: {alert['message']}")
    
    print("✓ Моніторинг протягом 5 секунд...")
    monitor.monitor_continuous(
        interval=1,
        duration=5,
        on_metric=on_metric,
        on_alert=on_alert
    )
    print()


def example_14_command_history():
    """Приклад 14: Історія команд"""
    print("=" * 60)
    print("ПРИКЛАД 14: Історія команд")
    print("=" * 60)
    
    automation = ConsoleAutomation()
    
    # Запустити кілька команд
    automation.run_command('echo "Test 1"')
    automation.run_command('echo "Test 2"')
    automation.run_command('echo "Test 3"')
    
    # Отримати історію
    history = automation.get_command_history(limit=3)
    print(f"✓ Історія з останніх {len(history)} команд:")
    for i, cmd_result in enumerate(history, 1):
        print(f"  {i}. {cmd_result.command}")
        print(f"     Return code: {cmd_result.return_code}")
        print(f"     Time: {cmd_result.execution_time:.2f}s")
    print()


def main():
    """Запустити всі приклади"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  ПРИКЛАДИ: Автоматизація консолі та системи".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    try:
        example_1_basic_commands()
        example_2_command_parsing()
        example_3_async_execution()
        example_4_powershell_objects()
        example_5_powershell_pipeline()
        example_6_system_metrics()
        example_7_process_monitoring()
        example_8_alerts()
        example_9_windows_services()
        example_10_registry()
        example_11_task_scheduler()
        example_12_system_info()
        example_13_continuous_monitoring()
        example_14_command_history()
        
        print("=" * 60)
        print("✅ ВСІ ПРИКЛАДИ ВИКОНАНІ УСПІШНО!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
"""
Практичні приклади використання функцій з модуля automation
для керування мишею та клавіатурою.
"""

from plugins import automation
import time

# ============================================================================
# ПРИКЛАД 1: Базові операції з мишею
# ============================================================================

def example_basic_mouse():
    """Демонструє базові операції з мишею"""
    print("\n--- ПРИКЛАД 1: Базові операції з мишею ---")
    
    # Отримуємо розмір екрану
    screen_size = automation.get_screen_size()
    print(f"Розмір екрану: {screen_size}")
    
    # Отримуємо поточну позицію миші
    current_pos = automation.get_mouse_position()
    print(f"Поточна позиція миші: {current_pos}")
    
    # Переміщуємо мишу плавно на центр екрану
    center = (screen_size[0] // 2, screen_size[1] // 2)
    print(f"Переміщуємо мишу на {center}")
    # automation.move_mouse_smooth(center[0], center[1], duration=1.0)
    
    # Отримуємо нову позицію
    # new_pos = automation.get_mouse_position()
    # print(f"Нова позиція миші: {new_pos}")


# ============================================================================
# ПРИКЛАД 2: Кліки та натискання кнопок миші
# ============================================================================

def example_mouse_clicks():
    """Демонструє кліки та натискання кнопок миші"""
    print("\n--- ПРИКЛАД 2: Кліки та натискання ---")
    
    # Простий клік у поточній позиції
    print("Простий клік")
    # automation.click()
    
    # Клік на конкретних координатах
    print("Клік на координатах (400, 300)")
    # automation.click('left', x=400, y=300)
    
    # Подвійний клік
    print("Подвійний клік")
    # automation.double_click(x=400, y=300)
    
    # Правий клік
    print("Правий клік")
    # automation.right_click(x=400, y=300)
    
    # Кілька кліків з затримкою
    print("5 кліків з затримкою")
    # automation.click(count=5, interval=0.2)
    
    # Клік з плавним переміщенням
    print("Клік з плавним переміщенням")
    # automation.click('left', x=600, y=400, smooth=True, duration=0.5)


# ============================================================================
# ПРИКЛАД 3: Перетягування
# ============================================================================

def example_dragging():
    """Демонструє операції перетягування"""
    print("\n--- ПРИКЛАД 3: Перетягування ---")
    
    # Простий drag від поточної позиції до цільової
    print("Перетягуємо з (100, 100) на (500, 300)")
    # automation.drag_smooth(500, 300, duration=1.0, button='left')
    
    # Відносне перетягування
    print("Перетягуємо на 200 пікселів вправо")
    # automation.drag_relative_smooth(200, 0, duration=0.5)
    
    # Переміщення з утримуванням кнопки (як малювання)
    print("Утримуємо кнопку та переміщуємо")
    # automation.mouse_down('left')
    # automation.move_mouse_smooth(600, 400, duration=1.0)
    # automation.mouse_up('left')


# ============================================================================
# ПРИКЛАД 4: Прокрутка
# ============================================================================

def example_scrolling():
    """Демонструє прокрутку"""
    print("\n--- ПРИКЛАД 4: Прокрутка ---")
    
    # Вертикальна прокрутка вверх
    print("Прокрутка вверх на 5 кліків")
    # automation.scroll(5, direction='vertical')
    
    # Вертикальна прокрутка вниз
    print("Прокрутка вниз на 3 кліки")
    # automation.scroll(-3, direction='vertical')
    
    # Горизонтальна прокрутка
    print("Горизонтальна прокрутка")
    # automation.scroll(3, direction='horizontal')
    
    # Плавна прокрутка
    print("Плавна прокрутка на 10 кліків за 1 секунду")
    # automation.scroll_smooth(10, duration=1.0, steps=10, direction='vertical')


# ============================================================================
# ПРИКЛАД 5: Керування клавіатурою
# ============================================================================

def example_keyboard():
    """Демонструє керування клавіатурою"""
    print("\n--- ПРИКЛАД 5: Керування клавіатурою ---")
    
    # Натискання окремої клавіші
    print("Натискаємо 'A'")
    # automation.press_key('a')
    
    # Утримування та відпускання клавіші
    print("Shift+A")
    # automation.hold_key('shift')
    # automation.press_key('a')
    # automation.release_key('shift')
    
    # Гарячі клавіші (комбінації)
    print("Ctrl+C (копіювання)")
    # automation.hotkey('ctrl', 'c')
    
    # Більше комбінацій
    print("Alt+F4 (закриття вікна)")
    # automation.hotkey('alt', 'f4')
    
    # Послідовність комбінацій
    print("Ctrl+C -> Ctrl+V (копіювання та вставлення)")
    # automation.hotkey_sequence([['ctrl', 'c'], ['ctrl', 'v']], interval=0.5)


# ============================================================================
# ПРИКЛАД 6: Введення тексту
# ============================================================================

def example_text_input():
    """Демонструє введення тексту"""
    print("\n--- ПРИКЛАД 6: Введення тексту ---")
    
    # Звичайне введення
    print("Введення простого тексту")
    # automation.type_text('Hello World', interval=0.05)
    
    # Введення з імітацією людини (випадкова затримка)
    print("Введення з імітацією людини")
    # automation.type_text_human('Secret password', min_interval=0.05, max_interval=0.15)
    
    # Введення з особливими символами
    print("Введення з табуляцією та Enter")
    # automation.press_key('tab')
    # automation.type_text('some_email@example.com', interval=0.02)
    # automation.press_key('enter')


# ============================================================================
# ПРИКЛАД 7: Очікування клавіші
# ============================================================================

def example_wait_for_key():
    """Демонструє очікування натиску клавіші"""
    print("\n--- ПРИКЛАД 7: Очікування клавіші ---")
    
    # Очікування будь-якої клавіші з таймаутом
    print("Очікуємо натиску клавіші (таймаут 10 сек)...")
    # key = automation.wait_for_key(timeout=10)
    # if key:
    #     print(f"Ви натиснули: {key}")
    # else:
    #     print("Таймаут вичерпаний")
    
    # Очікування конкретної клавіші
    print("Очікуємо натиску 'ESC'...")
    # automation.wait_for_key(target_key='escape')
    # print("ESC натиснуто!")


# ============================================================================
# ПРИКЛАД 8: Рухи миші по синусоїді
# ============================================================================

def example_sine_movement():
    """Демонструє рухи миші по синусоїді"""
    print("\n--- ПРИКЛАД 8: Синусоїдальний рух ---")
    
    # Простий синусоїдальний рух
    print("Синусоїдальний рух від (100, 100) до (800, 400)")
    # automation.move_mouse_sine((100, 100), (800, 400), amplitude=80, frequency=2, duration=2.0)
    
    # З меншою амплітудою
    print("Менш виражена синусоїда")
    # automation.move_mouse_sine((100, 100), (600, 300), amplitude=30, frequency=1, duration=1.5)
    
    # Синусоїда з утримуванням кнопки (як малювання)
    print("Рисуємо синусоїду")
    # automation.move_mouse_sine((100, 300), (600, 300), amplitude=100, frequency=3, duration=2.0, button_hold='left')


# ============================================================================
# ПРИКЛАД 9: Рухи миші по спіралі
# ============================================================================

def example_spiral_movement():
    """Демонструє рухи миші по спіралі"""
    print("\n--- ПРИКЛАД 9: Спіральний рух ---")
    
    screen_size = automation.get_screen_size()
    center = (screen_size[0] // 2, screen_size[1] // 2)
    
    # Розширюючаяся спіраль
    print(f"Розширюючаяся спіраль від центру {center}")
    # automation.move_mouse_spiral(center, start_radius=20, end_radius=150, turns=2.5, duration=2.0)
    
    # Звужуюча спіраль (інверсія)
    print("Звужуюча спіраль")
    # automation.move_mouse_spiral(center, start_radius=200, end_radius=30, turns=2, duration=1.5)


# ============================================================================
# ПРИКЛАД 10: Рухи миші по колу та дугам
# ============================================================================

def example_circle_movement():
    """Демонструє рухи миші по колу"""
    print("\n--- ПРИКЛАД 10: Коло та дуги ---")
    
    center = (500, 400)
    radius = 120
    
    # Повне коло
    print(f"Повне коло навколо {center}")
    # automation.move_mouse_circle(center, radius=radius, steps_count=100, start_angle=0, end_angle=360, duration=2.0)
    
    # Чверть кола
    print("Чверть кола (0-90 градусів)")
    # automation.move_mouse_circle(center, radius=radius, steps_count=50, start_angle=0, end_angle=90, duration=1.0)
    
    # Дуга від 180 до 360 градусів
    print("Дуга (180-360 градусів)")
    # automation.move_mouse_circle(center, radius=radius, steps_count=100, start_angle=180, end_angle=360, duration=1.5)


# ============================================================================
# ПРИКЛАД 11: Зигзагоподібний рух
# ============================================================================

def example_zigzag_movement():
    """Демонструє зигзагоподібні рухи"""
    print("\n--- ПРИКЛАД 11: Зигзаг ---")
    
    # З великим зигзагом
    print("Зигзаг з 5 коливаннями")
    # automation.move_mouse_zigzag((100, 100), (700, 500), amplitude=60, zigzags=5, duration=2.0)
    
    # З малим зигзагом
    print("Тонкий зигзаг")
    # automation.move_mouse_zigzag((100, 200), (600, 200), amplitude=20, zigzags=8, duration=1.5)


# ============================================================================
# ПРИКЛАД 12: Випадковий маршрут
# ============================================================================

def example_random_walk():
    """Демонструє випадкові маршрути"""
    print("\n--- ПРИКЛАД 12: Випадковий маршрут ---")
    
    # Випадковий маршрут від A до B
    print("Випадковий маршрут від (100, 100) до (700, 400)")
    # automation.move_mouse_random_walk((100, 100), (700, 400), step_size=20, duration=2.0)
    
    # З малим кроком (более детальна траєкторія)
    print("Більш гладкий випадковий маршрут")
    # automation.move_mouse_random_walk((100, 100), (700, 400), step_size=8, duration=1.5)


# ============================================================================
# ПРИКЛАД 13: Рух з гаусівським шумом
# ============================================================================

def example_noisy_movement():
    """Демонструє рухи з природним шумом (дрижанням)"""
    print("\n--- ПРИКЛАД 13: Рух з шумом (реалістичний) ---")
    
    # З малим шумом
    print("Рух з малим шумом")
    # automation.move_mouse_noisy((100, 100), (700, 400), sigma=15, duration=1.0)
    
    # З великим шумом
    print("Рух з великим шумом (дрижання)")
    # automation.move_mouse_noisy((100, 100), (700, 400), sigma=50, duration=1.0)
    
    # Середній шум (рекомендовано)
    print("Природний рух з дрижанням")
    # automation.move_mouse_noisy((100, 100), (700, 400), sigma=25, duration=0.8)


# ============================================================================
# ПРИКЛАД 14: Рух через вузлові точки (інтерполяція)
# ============================================================================

def example_interpolated_movement():
    """Демонструє рух через вузлові точки"""
    print("\n--- ПРИКЛАД 14: Інтерполяція через вузлові точки ---")
    
    waypoints = [
        (100, 100),
        (250, 350),
        (400, 150),
        (550, 450),
        (700, 200)
    ]
    
    print(f"Рух через {len(waypoints)} вузлових точок")
    
    # Catmull-Rom (найбільш гладкий)
    print("Гладка крива (Catmull-Rom)")
    # automation.move_mouse_interpolated(waypoints, steps_per_segment=20, curve_type='catmull', duration=3.0)
    
    # Кубічна крива Безьє
    print("Кубічна крива Безьє")
    # automation.move_mouse_interpolated(waypoints, steps_per_segment=15, curve_type='cubic', duration=2.5)
    
    # Лінійна інтерполяція
    print("Лінійна інтерполяція")
    # automation.move_mouse_interpolated(waypoints, steps_per_segment=10, curve_type='linear', duration=2.0)


# ============================================================================
# ПРИКЛАД 15: Комбінований рух (первинна крива + шум)
# ============================================================================

def example_composite_movement():
    """Демонструє комбіновані рухи з реалізмом"""
    print("\n--- ПРИКЛАД 15: Комбінований рух (первинна + шум) ---")
    
    # Синусоїда + шум (найбільш реалістична)
    print("Синусоїда з шумом")
    # automation.move_mouse_composite((100, 100), (700, 400), pattern='sine', secondary_noise=10, duration=2.0)
    
    # Зигзаг + шум
    print("Зигзаг з шумом")
    # automation.move_mouse_composite((100, 100), (700, 400), pattern='zigzag', secondary_noise=8, duration=1.8)
    
    # Випадковий маршрут + шум
    print("Випадковий маршрут з шумом")
    # automation.move_mouse_composite((100, 100), (700, 400), pattern='random_walk', secondary_noise=5, duration=2.2)
    
    # Спіраль + шум
    print("Спіраль з шумом")
    # automation.move_mouse_composite((400, 300), (500, 300), pattern='spiral', secondary_noise=3, duration=1.5)


# ============================================================================
# ПРИКЛАД 16: Практичний сценарій - автоклік по елементам
# ============================================================================

def example_click_elements():
    """Практичний приклад: клік по елементам на екрані"""
    print("\n--- ПРИКЛАД 16: Автоклік по елементам ---")
    
    # Координати кнопок/елементів
    buttons = [
        {'name': 'Button 1', 'pos': (100, 200)},
        {'name': 'Button 2', 'pos': (300, 200)},
        {'name': 'Button 3', 'pos': (500, 200)},
    ]
    
    print("Кліємо по кнопкам з затримками")
    for button in buttons:
        print(f"  Клік по {button['name']}")
        # automation.click('left', x=button['pos'][0], y=button['pos'][1], smooth=True, duration=0.3)
        # time.sleep(0.5)


# ============================================================================
# ПРИКЛАД 17: Практичний сценарій - заповнення форми
# ============================================================================

def example_form_filling():
    """Практичний приклад: автоматичне заповнення форми"""
    print("\n--- ПРИКЛАД 17: Заповнення форми ---")
    
    # Поля форми (координати)
    form_fields = {
        'name': (300, 100),
        'email': (300, 150),
        'phone': (300, 200),
        'message': (300, 300),
    }
    
    # Дані для заповнення
    form_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1234567890',
        'message': 'Hello! This is a test message.',
    }
    
    print("Заповнюємо форму...")
    # for field_name, field_pos in form_fields.items():
    #     # Рухаємось до поля з реалістичною траєкторією
    #     current_pos = automation.get_mouse_position()
    #     automation.move_mouse_noisy(current_pos, field_pos, sigma=10, duration=0.5)
    #     
    #     # Кліємо по полю
    #     automation.click()
    #     time.sleep(0.2)
    #     
    #     # Вводимо текст
    #     text = form_data.get(field_name, '')
    #     automation.type_text_human(text, min_interval=0.03, max_interval=0.1)
    #     time.sleep(0.3)


# ============================================================================
# Запуск всіх прикладів
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("ПРИКЛАДИ ВИКОРИСТАННЯ МОДУЛЯ automation")
    print("=" * 70)
    
    # Розкомментуйте потрібні приклади для тестування
    
    example_basic_mouse()
    example_mouse_clicks()
    example_dragging()
    example_scrolling()
    example_keyboard()
    example_text_input()
    example_wait_for_key()
    example_sine_movement()
    example_spiral_movement()
    example_circle_movement()
    example_zigzag_movement()
    example_random_walk()
    example_noisy_movement()
    example_interpolated_movement()
    example_composite_movement()
    example_click_elements()
    example_form_filling()
    
    print("\n" + "=" * 70)
    print("Усі приклади готові до запуску!")
    print("=" * 70)
