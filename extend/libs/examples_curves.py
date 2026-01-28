# Приклади використання модуля curves

"""
Цей файл містить практичні приклади використання функцій з модуля curves
для генерування різних траєкторій та криві.
"""

from plugins import curves
import time

# ============================================================================
# ПРИКЛАД 1: Синусоїдальна траєкторія
# ============================================================================

def example_sine_wave():
    """Генерує синусоїдальну траєкторію від точки A до B"""
    print("\n--- ПРИКЛАД 1: Синусоїдальна хвиля ---")
    
    start = (100, 100)
    end = (800, 300)
    
    # Параметри
    amplitude = 70      # висота хвилі
    frequency = 3       # кількість коливань
    steps = 200         # кількість точок у шляху
    
    path = curves.sine_wave(start, end, amplitude=amplitude, frequency=frequency, steps=steps)
    
    print(f"Кількість точок: {len(path)}")
    print(f"Перша точка: {path[0]}")
    print(f"Остання точка: {path[-1]}")
    print(f"Довжина шляху: {curves.path_length(path):.2f} пікселів")


# ============================================================================
# ПРИКЛАД 2: Спіральна траєкторія
# ============================================================================

def example_spiral():
    """Генерує спіральну траєкторію"""
    print("\n--- ПРИКЛАД 2: Спіраль ---")
    
    center = (500, 400)
    start_radius = 30
    end_radius = 250
    turns = 3           # три повних оберти
    steps = 300
    
    spiral = curves.spiral_path(center, start_radius=start_radius, end_radius=end_radius, turns=turns, steps=steps)
    
    print(f"Центр спіралі: {center}")
    print(f"Радіус: від {start_radius} до {end_radius} пікселів")
    print(f"Обертів: {turns}")
    print(f"Кількість точок: {len(spiral)}")
    print(f"Довжина шляху: {curves.path_length(spiral):.2f} пікселів")


# ============================================================================
# ПРИКЛАД 3: Коло та дуги
# ============================================================================

def example_circle():
    """Генерує коло та різні дуги"""
    print("\n--- ПРИКЛАД 3: Коло та дуги ---")
    
    center = (500, 400)
    radius = 120
    
    # Повне коло
    full = curves.circle_path(center, radius=radius, steps=100, start_angle=0, end_angle=360)
    print(f"Повне коло: {len(full)} точок, довжина {curves.path_length(full):.2f}")
    
    # Чверть кола (0-90 градусів)
    quarter = curves.circle_path(center, radius=radius, steps=50, start_angle=0, end_angle=90)
    print(f"Чверть кола (90°): {len(quarter)} точок, довжина {curves.path_length(quarter):.2f}")
    
    # Дуга (180-360 градусів)
    semicircle = curves.circle_path(center, radius=radius, steps=100, start_angle=180, end_angle=360)
    print(f"Піл-кола (180-360°): {len(semicircle)} точок")


# ============================================================================
# ПРИКЛАД 4: Зигзаг
# ============================================================================

def example_zigzag():
    """Генерує зигзагоподібну траєкторію"""
    print("\n--- ПРИКЛАД 4: Зигзаг ---")
    
    start = (100, 200)
    end = (700, 500)
    
    amplitude = 50      # висота одного зигзагу
    zigzags = 4         # кількість зигзагів
    steps = 150
    
    path = curves.zigzag_path(start, end, amplitude=amplitude, zigzags=zigzags, steps=steps)
    
    print(f"Від {start} до {end}")
    print(f"Амплітуда: {amplitude} пікселів")
    print(f"Зигзагів: {zigzags}")
    print(f"Точок у шляху: {len(path)}")
    print(f"Довжина шляху: {curves.path_length(path):.2f} пікселів")


# ============================================================================
# ПРИКЛАД 5: Гаусівський шум (реалістичний рух)
# ============================================================================

def example_gaussian_noise():
    """Додає природний шум до траєкторії (імітація дрижання руки)"""
    print("\n--- ПРИКЛАД 5: Гаусівський шум (реалістичний рух) ---")
    
    start = (100, 100)
    end = (600, 400)
    
    # Різні рівні шуму
    for sigma in [5, 20, 50]:
        path = curves.gaussian_noise_path(start, end, sigma=sigma, steps=100)
        print(f"Сигма={sigma}: довжина шляху {curves.path_length(path):.2f} пікселів")


# ============================================================================
# ПРИКЛАД 6: Випадковий маршрут
# ============================================================================

def example_random_walk():
    """Генерує випадковий маршрут від стартової до кінцевої точки"""
    print("\n--- ПРИКЛАД 6: Випадковий маршрут ---")
    
    start = (100, 100)
    end = (700, 500)
    
    step_size = 20
    steps = 80
    
    # Без обмежень
    path = curves.random_walk_path(start, step_size=step_size, steps=steps)
    path[-1] = end  # Переконуємось, що кінцева точка це мета
    
    print(f"Від {start} до {end}")
    print(f"Розмір кроку: {step_size} пікселів")
    print(f"Кількість кроків: {steps}")
    print(f"Довжина шляху: {curves.path_length(path):.2f} пікселів")
    
    # З обмеженнями
    bounds = ((0, 0), (800, 600))
    path_bounded = curves.random_walk_path(start, step_size=step_size, steps=steps, bounds=bounds)
    print(f"З обмеженнями {bounds}: {len(path_bounded)} точок")


# ============================================================================
# ПРИКЛАД 7: Інтерполяція через вузлові точки
# ============================================================================

def example_interpolation():
    """Рух через серію вузлових точок різними методами"""
    print("\n--- ПРИКЛАД 7: Інтерполяція через вузлові точки ---")
    
    # Вузлові точки
    waypoints = [
        (100, 100),
        (250, 300),
        (400, 150),
        (550, 400),
        (700, 200)
    ]
    
    print(f"Вузлові точки: {len(waypoints)}")
    
    methods = ['linear', 'quadratic', 'cubic', 'catmull']
    for method in methods:
        path = curves.interpolate_path(waypoints, steps_per_segment=20, curve_type=method)
        length = curves.path_length(path)
        print(f"Метод '{method}': {len(path)} точок, довжина {length:.2f}")


# ============================================================================
# ПРИКЛАД 8: Комбінований рух (первинна крива + вторинний шум)
# ============================================================================

def example_composite():
    """Комбінує первинний патерн з вторинним шумом для реалізму"""
    print("\n--- ПРИКЛАД 8: Комбінований рух ---")
    
    start = (100, 100)
    end = (600, 400)
    
    patterns = ['sine', 'zigzag', 'random_walk']
    
    for pattern in patterns:
        path = curves.composite_path(start, end, primary_pattern=pattern, secondary_noise=10, steps=150)
        length = curves.path_length(path)
        print(f"Патерн '{pattern}': {len(path)} точок, довжина {length:.2f}")


# ============================================================================
# ПРИКЛАД 9: Easing функції
# ============================================================================

def example_easing():
    """Демонструє еasing функції для згладжування анімацій"""
    print("\n--- ПРИКЛАД 9: Easing функції ---")
    
    # Тестуємо різні easing функції
    easing_functions = [
        ('linear', curves.linear),
        ('ease_in_quad', curves.ease_in_quad),
        ('ease_out_quad', curves.ease_out_quad),
        ('ease_in_out_quad', curves.ease_in_out_quad),
        ('ease_in_cubic', curves.ease_in_cubic),
        ('ease_out_cubic', curves.ease_out_cubic),
        ('ease_in_out_cubic', curves.ease_in_out_cubic),
        ('ease_in_sin', curves.ease_in_sin),
        ('ease_out_sin', curves.ease_out_sin),
        ('ease_in_out_sin', curves.ease_in_out_sin),
    ]
    
    t_values = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    for name, func in easing_functions:
        values = [func(t) for t in t_values]
        print(f"{name:20} -> {[f'{v:.3f}' for v in values]}")


# ============================================================================
# ПРИКЛАД 10: Аналіз траєкторій
# ============================================================================

def example_analysis():
    """Аналізує траєкторію: довжина, швидкість, перепробування"""
    print("\n--- ПРИКЛАД 10: Аналіз траєкторій ---")
    
    path = curves.sine_wave((100, 100), (600, 300), amplitude=60, frequency=2, steps=200)
    
    # Довжина шляху
    length = curves.path_length(path)
    print(f"Довжина шляху: {length:.2f} пікселів")
    
    # Швидкість
    time_steps = [0.01] * (len(path) - 1)
    velocities = curves.path_velocity(path, time_steps)
    avg_velocity = sum(velocities) / len(velocities) if velocities else 0
    max_velocity = max(velocities) if velocities else 0
    print(f"Середня швидкість: {avg_velocity:.2f} пікселів/кадр")
    print(f"Максимальна швидкість: {max_velocity:.2f} пікселів/кадр")
    
    # Перепробування для рівномірної швидкості
    uniform_path = curves.resample_path(path, total_distance=length)
    print(f"Оригінальний шлях: {len(path)} точок")
    print(f"Перепробований шлях: {len(uniform_path)} точок")


# ============================================================================
# ПРИКЛАД 11: Практичний сценарій - рисування фігур
# ============================================================================

def example_drawing_shapes():
    """Рисує різні фігури на екрані"""
    print("\n--- ПРИКЛАД 11: Рисування фігур ---")
    
    from plugins import automation
    
    # Зупинте скрипт, якщо потрібно
    print("Коли будете готові, натисніть Enter...")
    # input()
    
    # 1. Рисуємо прямокутник зигзагом
    print("Малюємо прямокутник...")
    rect_points = [
        (200, 200), (400, 200), (400, 400), (200, 400), (200, 200)
    ]
    # automation.move_mouse_interpolated(rect_points, curve_type='linear', duration=2.0)
    
    # 2. Рисуємо коло
    print("Малюємо коло...")
    center = (500, 300)
    radius = 100
    circle = curves.circle_path(center, radius=radius, steps=100, start_angle=0, end_angle=360)
    # for x, y in circle:
    #     automation._mouse_controller.position = (int(x), int(y))
    #     time.sleep(0.005)
    
    # 3. Рисуємо спіраль
    print("Малюємо спіраль...")
    spiral = curves.spiral_path(center, start_radius=10, end_radius=100, turns=3, steps=150)
    # for x, y in spiral:
    #     automation._mouse_controller.position = (int(x), int(y))
    #     time.sleep(0.005)


# ============================================================================
# ПРИКЛАД 12: Практичний сценарій - автозаповнення форми
# ============================================================================

def example_form_filling():
    """Заповнює форму з реалістичними рухами миші"""
    print("\n--- ПРИКЛАД 12: Автозаповнення форми ---")
    
    from plugins import automation
    
    # Координати полів форми
    fields = {
        'name': (300, 100),
        'email': (300, 150),
        'phone': (300, 200),
        'submit': (400, 300)
    }
    
    data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1234567890'
    }
    
    print("Зупинте скрипт, якщо потрібно")
    # Розкомментуйте для тестування:
    # for field, value in data.items():
    #     x, y = fields[field]
    #     # Рух миші реалістичною траєкторією
    #     automation.move_mouse_noisy((automation.get_mouse_position()[0], automation.get_mouse_position()[1]), 
    #                                (x, y), sigma=10, duration=0.5)
    #     automation.click()
    #     automation.type_text_human(value, min_interval=0.05, max_interval=0.15)
    #     time.sleep(0.3)
    # 
    # # Натискаємо Submit
    # sx, sy = fields['submit']
    # automation.move_mouse_sine((automation.get_mouse_position()[0], automation.get_mouse_position()[1]), 
    #                           (sx, sy), duration=0.5)
    # automation.click()


# ============================================================================
# Запуск всіх прикладів
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("ПРИКЛАДИ ВИКОРИСТАННЯ МОДУЛЯ curves")
    print("=" * 70)
    
    example_sine_wave()
    example_spiral()
    example_circle()
    example_zigzag()
    example_gaussian_noise()
    example_random_walk()
    example_interpolation()
    example_composite()
    example_easing()
    example_analysis()
    example_drawing_shapes()
    example_form_filling()
    
    print("\n" + "=" * 70)
    print("Усі приклади завершено!")
    print("=" * 70)
