# Документація проєкту `libs`

Повний набір утиліт для автоматизації керування мишею, клавіатурою та роботи з математичними кривими та траєкторіями.

---

## Структура проєкту

```
libs/
├── base.py              # базові утиліти
├── console.py           # робота з консоллю
└── plugins/
    ├── automation.py    # керування мишею та клавіатурою (40+ функцій)
    ├── curves.py        # математичні криві та траєкторії (30+ функцій)
    ├── ocr.py           # розпізнавання тексту з екрану (12 функцій)
    ├── screen.py        # робота з екраном та скрінами (15 функцій)
    ├── recorder.py      # запис та відтворення макросів (18 функцій)
    ├── sensor.py        # сенсори та моніторинг подій (16 функцій)
    ├── performance.py   # оптимізація та логування (20 функцій)
    ├── helpers.py       # практичні утиліти (50+ функцій) ⭐ NEW
    ├── dsl_integration.py # система DSL для оркестрування (10+ команд) ⭐ NEW
    ├── datetime_aml.py   # робота з датою та часом
    ├── file.py          # робота з файлами
    ├── http.py          # HTTP запити
    ├── json.py          # JSON операції
    ├── keyboard.py      # розширена клавіатура
    ├── mouse.py         # розширена миша
    ├── regex.py         # регулярні вирази
    └── system.py        # системні команди
```

### Статистика модулів

| Модуль | Функцій | Опис |
|--------|---------|------|
| **automation.py** | 40+ | Миша, клавіатура, криві, переміщення |
| **curves.py** | 30+ | Математичні траєкторії та інтерполяція |
| **ocr.py** | 12 | Розпізнавання тексту з екрану |
| **screen.py** | 15 | Скрінів, пошук зображень, моніторинг |
| **recorder.py** | 18 | Запис/відтворення користувацьких дій |
| **sensor.py** | 16 | Відстеження подій і реакції на них |
| **performance.py** | 20 | Логування, таймери, оптимізація |
| **helpers.py** ⭐ | 50+ | Конвертування, валідація, файли, кеш |
| **dsl_integration.py** ⭐ | 10+ | DSL парсер, виконавець, інтеграція |
| **Інші модулі** | 15+ | datetime, file, http, json, keyboard, mouse, regex, system, console, base |

**Всього: 110+ функцій по всім модулям**

---

# Модуль `automation.py`

**Основний модуль для керування мишею та клавіатурою.**

Поєднує функціональність `pynput` для безпосереднього керування периферійними пристроями та модуля `curves` для складних траєкторій.

## Залежності
- `pynput` — керування мишею та клавіатурою

## Функції управління мишею

### Базові операції

#### `get_screen_size()`
```python
size = automation.get_screen_size()
# Returns: (1920, 1080)
```
- Повертає розміри екрану у форматі `(width, height)`
- На Windows використовує WinAPI (більш точно)
- Fallback на pynput mouse controller при неудачі

#### `get_mouse_position()`
```python
pos = automation.get_mouse_position()
# Returns: (512, 384)
```
- Повертає поточну позицію миші `(x, y)`

#### `move_mouse_smooth(x, y, duration=0.5, steps=20)`
```python
# Переміщує мишу від поточної позиції до (800, 600) плавно за 0.5 сек
automation.move_mouse_smooth(800, 600, duration=0.5, steps=20)
```
- Плавне переміщення з ease-out анімацією
- `duration` — час руху в секундах
- `steps` — кількість проміжних точок

#### `move_mouse_relative_smooth(dx, dy, duration=0.5, steps=20)`
```python
# Переміщує мишу на 100 пікселів вправо і 50 вниз
automation.move_mouse_relative_smooth(100, -50, duration=0.3)
```
- Відносне переміщення від поточної позиції

#### `move_mouse_to_ratio(rx, ry, duration=0.5, steps=20)`
```python
# Переміщує мишу на 50% ширини та 75% висоти екрану
automation.move_mouse_to_ratio(0.5, 0.75, duration=0.5)
```
- Переміщення у відносних координатах (0..1)

### Кліки та натискання

#### `click(button='left', x=None, y=None, count=1, interval=0.05, smooth=False, duration=0.2, steps=15)`
```python
# Простий клік у поточній позиції
automation.click()

# Клік на координатах (400, 300)
automation.click('left', x=400, y=300)

# Подвійний клік з плавним переміщенням
automation.click('left', x=400, y=300, count=2, smooth=True, duration=0.3)

# Кілька кліків з затримкою
automation.click(count=5, interval=0.1)
```
- `button` — 'left', 'right', 'middle'
- `smooth=True` — плавне переміщення перед кліком

#### `double_click(x=None, y=None, button='left', smooth=False, duration=0.2, steps=15)`
```python
# Подвійний клік
automation.double_click(400, 300)
```

#### `right_click(x=None, y=None, smooth=False, duration=0.2, steps=15)`
```python
# Правий клік
automation.right_click(400, 300)
```

### Перетягування

#### `drag_smooth(x, y, duration=0.5, button='left')`
```python
# Перетяга файл з (100, 100) на (500, 300)
automation.drag_smooth(500, 300, duration=0.5, button='left')
```
- Натискає кнопку, плавно переміщує, відпускає

#### `drag_to_smooth(x, y, duration=0.5, steps=20, button='left')`
```python
automation.drag_to_smooth(600, 400, duration=0.8)
```

#### `drag_relative_smooth(dx, dy, duration=0.5, steps=20, button='left')`
```python
# Перетяга на 200 пікселів вправо
automation.drag_relative_smooth(200, 0, duration=0.5)
```

### Прокрутка

#### `scroll(clicks, direction='vertical')`
```python
# Вертикальна прокрутка на 5 кліків вверх
automation.scroll(5, direction='vertical')

# Горизонтальна прокрутка на 3 кліки вліво
automation.scroll(-3, direction='horizontal')
```
- Позитивні значення — вверх/вправо
- Негативні — вниз/вліво

#### `scroll_smooth(clicks, duration=0.5, steps=10, direction='vertical')`
```python
# Плавна прокрутка, розподілена на 10 кроків
automation.scroll_smooth(10, duration=1.0, steps=10, direction='vertical')
```

### Утримування кнопок миші

#### `mouse_down(button='left')` / `mouse_up(button='left')`
```python
# Натискаємо і утримуємо ліву кнопку
automation.mouse_down('left')
time.sleep(2)  # утримуємо 2 сек
automation.mouse_up('left')
```

---

## Функції управління клавіатурою

#### `press_key(key)`
```python
automation.press_key('a')
automation.press_key('enter')
automation.press_key('escape')
```
- Натискає та відпускає клавішу

#### `hold_key(key)` / `release_key(key)`
```python
automation.hold_key('shift')
automation.press_key('a')
automation.release_key('shift')  # Shift+A
```

#### `hotkey(*keys)`
```python
# Ctrl+C
automation.hotkey('ctrl', 'c')

# Ctrl+Shift+Delete
automation.hotkey('ctrl', 'shift', 'delete')

# Alt+F4
automation.hotkey('alt', 'f4')
```

#### `hotkey_sequence(sequences, interval=0.1)`
```python
# Copy, then paste
automation.hotkey_sequence([
    ['ctrl', 'c'],
    ['ctrl', 'v']
], interval=0.5)
```
- Виконує послідовність комбінацій з затримкою

#### `type_text(text, interval=0.01)`
```python
automation.type_text('Hello, World!', interval=0.05)
```
- Введення текстуз затримкою між символами

#### `type_text_human(text, min_interval=0.01, max_interval=0.05)`
```python
# Введення з випадковою затримкою (імітація людини)
automation.type_text_human('Secret password', min_interval=0.02, max_interval=0.1)
```

#### `wait_for_key(target_key=None, timeout=None)`
```python
# Чекаємо на натиск будь-якої клавіші (макс 30 сек)
pressed_key = automation.wait_for_key(timeout=30)
print(f"You pressed: {pressed_key}")

# Чекаємо на натиск Escape
automation.wait_for_key(target_key='escape')
```
- Повертає назву натиснутої клавіші або None

---

## Просунуті рухи миші (криві та траєкторії)

Ці функції використовують модуль `curves` для складних, природних траєкторій.

#### `move_mouse_sine(start, end, amplitude=50, frequency=2, duration=0.5, button_hold=None)`
```python
# Рух по синусоїді
automation.move_mouse_sine((100, 100), (500, 200), amplitude=60, frequency=2, duration=1.0)

# Рух по синусоїді з утримуванням ліву кнопку (малювання)
automation.move_mouse_sine((100, 100), (500, 200), amplitude=30, frequency=1, duration=0.8, button_hold='left')
```
- Природне хвильоподібне переміщення

#### `move_mouse_spiral(center, start_radius=10, end_radius=100, turns=2, duration=0.5)`
```python
# Спіраль від центру екрану, розширюється
center = (automation.get_screen_size()[0]//2, automation.get_screen_size()[1]//2)
automation.move_mouse_spiral(center, start_radius=20, end_radius=200, turns=3, duration=1.5)
```
- Рух по розширюючій чи звужуючій спіралі

#### `move_mouse_circle(center, radius, steps_count=100, start_angle=0, end_angle=360, duration=0.5)`
```python
# Коло навколо центру
automation.move_mouse_circle((500, 400), radius=100, steps_count=100, start_angle=0, end_angle=360, duration=1.0)

# Дуга (180 градусів)
automation.move_mouse_circle((500, 400), radius=80, steps_count=50, start_angle=0, end_angle=180, duration=0.8)
```

#### `move_mouse_zigzag(start, end, amplitude=30, zigzags=5, duration=0.5)`
```python
# Зигзагоподібний рух
automation.move_mouse_zigzag((100, 100), (500, 300), amplitude=40, zigzags=6, duration=0.8)
```

#### `move_mouse_random_walk(start, end, step_size=10, duration=0.5)`
```python
# Випадковий маршрут від A до B (природний, непередбачуваний)
automation.move_mouse_random_walk((100, 100), (500, 400), step_size=15, duration=1.0)
```

#### `move_mouse_noisy(start, end, sigma=20, duration=0.5)`
```python
# Рух з гаусівським шумом (як людина з невеликими дрижаннями)
automation.move_mouse_noisy((100, 100), (500, 300), sigma=25, duration=0.5)
```

#### `move_mouse_interpolated(points, steps_per_segment=10, curve_type='catmull', duration=0.5)`
```python
# Рух через вузлові точки з гладкою інтерполяцією
waypoints = [(100, 100), (200, 300), (400, 150), (500, 400)]
automation.move_mouse_interpolated(waypoints, steps_per_segment=15, curve_type='catmull', duration=1.5)

# З різними типами кривих
automation.move_mouse_interpolated(waypoints, curve_type='cubic', duration=1.0)
automation.move_mouse_interpolated(waypoints, curve_type='linear', duration=0.8)
```

#### `move_mouse_composite(start, end, pattern='sine', secondary_noise=5, duration=0.5)`
```python
# Комбінований рух: синусоїда + шум
automation.move_mouse_composite((100, 100), (500, 500), pattern='sine', secondary_noise=10, duration=1.0)

# Зигзаг + шум
automation.move_mouse_composite((100, 100), (500, 500), pattern='zigzag', secondary_noise=8, duration=0.8)

# Випадковий маршрут + шум
automation.move_mouse_composite((100, 100), (500, 500), pattern='random_walk', secondary_noise=5, duration=1.2)

# Спіраль + шум
automation.move_mouse_composite((300, 300), (400, 400), pattern='spiral', secondary_noise=3, duration=1.0)
```

---

## Допоміжні функції

#### `tuple_to_list(obj)`
```python
result = automation.tuple_to_list((1, 2, (3, 4)))
# Returns: [1, 2, [3, 4]]

result = automation.tuple_to_list([(1, 2), (3, 4)])
# Returns: [[1, 2], [3, 4]]
```
- Рекурсивно конвертує кортежі в списки

#### `clamp_to_screen(x, y)`
```python
x, y = automation.clamp_to_screen(5000, -50)
# Returns: (screen_width-1, 0) — координати обмежені межами екрану
```

#### `move_mouse_path(points, per_segment_duration=0.4, steps_per_segment=20)`
```python
path = [(100, 100), (200, 150), (300, 100), (400, 200)]
automation.move_mouse_path(path, per_segment_duration=0.3, steps_per_segment=20)
```

#### `move_mouse_bezier_to(x, y, duration=0.8, steps=40, c1=None, c2=None, jitter=0)`
```python
# Рух по кривій Безьє з авто-контрольними точками
automation.move_mouse_bezier_to(500, 400, duration=0.8, jitter=5)

# З визначеними контрольними точками
automation.move_mouse_bezier_to(500, 400, duration=0.8, c1=(250, 200), c2=(350, 300), jitter=0)
```

---

# Модуль `curves.py`

**Математичні функції для роботи з кривими та траєкторіями.**

Самостійний модуль для генерування та обробки шляхів, що використовується `automation.py`.

## Функції easing (згладжування)

```python
from plugins import curves

# Easing функції визначають темп змін (0..1)
# Вхід: t від 0 до 1 (прогрес)
# Вихід: значення від 0 до 1 (згладжене)

t = 0.5

# Лінійна інтерполяція
value = curves.linear(t)  # 0.5

# Квадратичні
value = curves.ease_in_quad(t)       # повільний старт
value = curves.ease_out_quad(t)      # повільний кінець
value = curves.ease_in_out_quad(t)   # обидва

# Кубічні
value = curves.ease_in_cubic(t)
value = curves.ease_out_cubic(t)
value = curves.ease_in_out_cubic(t)

# Синусоїдальні
value = curves.ease_in_sin(t)
value = curves.ease_out_sin(t)
value = curves.ease_in_out_sin(t)
```

## Інтерполяція точок

```python
from plugins import curves

# Лінійна інтерполяція між двома точками
p1 = (100, 100)
p2 = (500, 300)
mid_point = curves.lerp(p1, p2, 0.5)  # (300, 200)

# Квадратична крива Безьє (3 контрольні точки)
start = (100, 100)
control = (300, 50)
end = (500, 300)
point_at_50_percent = curves.quadratic_bezier(start, control, end, 0.5)

# Кубічна крива Безьє (4 контрольні точки)
p0 = (100, 100)
p1 = (200, 50)
p2 = (400, 50)
p3 = (500, 300)
point = curves.cubic_bezier(p0, p1, p2, p3, 0.5)

# Сплайн Катмулла-Рома (гладка крива через p1, p2)
p0 = (50, 100)
p1 = (100, 200)
p2 = (400, 150)
p3 = (500, 300)
point = curves.catmull_rom(p0, p1, p2, p3, 0.5)
```

## Генерація траєкторій

### Приклад 1: Синусоїдальний рух

```python
from plugins import curves

# Рух від (100, 100) до (500, 300) по синусоїді
start = (100, 100)
end = (500, 300)
amplitude = 60      # max відхилення від прямої лінії
frequency = 2       # кількість повних коливань
steps = 100         # кількість точок у шляху

path = curves.sine_wave(start, end, amplitude=amplitude, frequency=frequency, steps=steps)

# path містить 100 точок (x, y)
print(f"Path length: {len(path)} points")
print(f"First point: {path[0]}")
print(f"Last point: {path[-1]}")

# Використання з automation
from plugins import automation
for x, y in path:
    automation._mouse_controller.position = (int(x), int(y))
    import time
    time.sleep(0.01)
```

### Приклад 2: Спіральний рух

```python
from plugins import curves

# Спіраль від центру экрана, що розширюється
center = (500, 400)         # центр спіралі
start_radius = 20           # стартовий радіус
end_radius = 200            # кінцевий радіус
turns = 3                   # кількість повних обертів
steps = 150                 # кількість точок

spiral = curves.spiral_path(center, start_radius=start_radius, end_radius=end_radius, turns=turns, steps=steps)

# Рух по спіралі
from plugins import automation
automation.move_mouse_spiral(center, start_radius, end_radius, turns, duration=1.5)
```

### Приклад 3: Коло та дуги

```python
from plugins import curves

# Рух по повному колу
center = (500, 400)
radius = 100
steps = 100

full_circle = curves.circle_path(center, radius=radius, steps=steps, start_angle=0, end_angle=360)

# Рух по дузі (90 градусів)
quarter_circle = curves.circle_path(center, radius=radius, steps=50, start_angle=0, end_angle=90)

# Рух по S-образній дузі (180-360 градусів)
s_curve = curves.circle_path(center, radius=radius, steps=100, start_angle=180, end_angle=360)
```

### Приклад 4: Зигзаг

```python
from plugins import curves

# Зигзагоподібний рух від A до B
start = (100, 100)
end = (500, 300)
amplitude = 40          # висота зигзагу
zigzags = 5             # кількість зигзагів
steps = 150             # кількість точок

zigzag = curves.zigzag_path(start, end, amplitude=amplitude, zigzags=zigzags, steps=steps)

# Використання
from plugins import automation
automation.move_mouse_zigzag(start, end, amplitude=amplitude, zigzags=zigzags, duration=1.0)
```

### Приклад 5: Випадковий маршрут

```python
from plugins import curves

# Випадковий маршрут від стартової точки до кінцевої
start = (100, 100)
end = (500, 400)
step_size = 15          # макс. переміщення за крок
steps = 60              # кількість кроків

random_path = curves.random_walk_path(start, step_size=step_size, steps=steps)

# Переконатися, що кінцева точка це target
random_path[-1] = end

# З обмеженнями границі
bounds = ((0, 0), (800, 600))
random_bounded = curves.random_walk_path(start, step_size=step_size, steps=steps, bounds=bounds)
```

### Приклад 6: Гаусівський шум (реалістичний рух)

```python
from plugins import curves

# Рух з природним дрижанням (як людина)
start = (100, 100)
end = (500, 300)
sigma = 25              # стандартне відхилення шуму
steps = 100             # кількість точок

noisy_path = curves.gaussian_noise_path(start, end, sigma=sigma, steps=steps)

# Використання
from plugins import automation
automation.move_mouse_noisy(start, end, sigma=sigma, duration=0.5)
```

### Приклад 7: Інтерполяція шляху через вузлові точки

```python
from plugins import curves

# Вузлові точки (waypoints)
points = [
    (100, 100),
    (200, 300),
    (400, 150),
    (500, 400),
    (600, 200)
]

# Інтерполяція різними методами
linear_path = curves.interpolate_path(points, steps_per_segment=20, curve_type='linear')
quadratic_path = curves.interpolate_path(points, steps_per_segment=20, curve_type='quadratic')
cubic_path = curves.interpolate_path(points, steps_per_segment=20, curve_type='cubic')
catmull_path = curves.interpolate_path(points, steps_per_segment=20, curve_type='catmull')

# Рух через вузлові точки
from plugins import automation
automation.move_mouse_interpolated(points, steps_per_segment=15, curve_type='catmull', duration=2.0)
```

### Приклад 8: Комбінований рух з реалізмом

```python
from plugins import curves
from plugins import automation

# Комбінація первинного патерну + вторинного шуму для максимального реалізму

# Синусоїда + шум
path1 = curves.composite_path((100, 100), (500, 300), primary_pattern='sine', secondary_noise=10, steps=100)

# Зигзаг + шум
path2 = curves.composite_path((100, 100), (500, 300), primary_pattern='zigzag', secondary_noise=8, steps=100)

# Випадковий маршрут + шум
path3 = curves.composite_path((100, 100), (500, 300), primary_pattern='random_walk', secondary_noise=5, steps=100)

# Спіраль + шум
path4 = curves.composite_path((300, 300), (400, 400), primary_pattern='spiral', secondary_noise=3, steps=100)

# Використання з automation
automation.move_mouse_composite((100, 100), (500, 500), pattern='sine', secondary_noise=10, duration=1.0)
automation.move_mouse_composite((100, 100), (500, 500), pattern='zigzag', secondary_noise=8, duration=1.0)
automation.move_mouse_composite((100, 100), (500, 500), pattern='random_walk', secondary_noise=5, duration=1.0)
```

### Приклад 9: Аналіз траєкторій

```python
from plugins import curves
import math

# Генеруємо шлях
path = curves.sine_wave((100, 100), (500, 300), amplitude=50, frequency=2, steps=100)

# Розраховуємо довжину шляху
total_length = curves.path_length(path)
print(f"Path length: {total_length:.2f} pixels")

# Розраховуємо швидкість на кожному етапі
time_steps = [0.01] * (len(path) - 1)  # 0.01 сек між точками
velocities = curves.path_velocity(path, time_steps)
avg_velocity = sum(velocities) / len(velocities)
print(f"Average velocity: {avg_velocity:.2f} pixels/frame")

# Переискавлюємо шлях для рівномірної швидкості
uniform_path = curves.resample_path(path, total_distance=total_length)
print(f"Original path: {len(path)} points")
print(f"Resampled path: {len(uniform_path)} points")
```

### Приклад 10: Комплексний сценарій

```python
from plugins import automation, curves
import time

# Сценарій: рисування на екрані

# Визначаємо вузлові точки для рисування
drawing_points = [
    (200, 100),
    (300, 50),
    (400, 100),
    (500, 150),
    (400, 250),
    (300, 200),
    (200, 250),
    (100, 150)
]

print("Drawing shape...")

# Рисуємо з інтерполяцією через вузлові точки
waypoints = drawing_points

# Метод 1: Гладка інтерполяція (Catmull-Rom)
print("Method 1: Catmull-Rom spline")
automation.move_mouse_interpolated(waypoints, steps_per_segment=20, curve_type='catmull', duration=3.0)
time.sleep(0.5)

# Метод 2: Рух по всіх точках зі спіралями
print("Method 2: Spiral paths between points")
for i in range(len(waypoints) - 1):
    start = waypoints[i]
    end = waypoints[i + 1]
    automation.move_mouse_spiral(start, start_radius=0, end_radius=50, turns=1, duration=0.5)
    automation.move_mouse_interpolated([start, end], duration=0.3)
time.sleep(0.5)

# Метод 3: Комбінована траєкторія з реалізмом
print("Method 3: Composite with noise")
automation.move_mouse_composite(waypoints[0], waypoints[-1], pattern='sine', secondary_noise=5, duration=2.0)

print("Drawing complete!")
```

---

## Рекомендації для найкращих результатів

1. **Для природного руху**: використовуйте `move_mouse_noisy()` або `move_mouse_composite(pattern='random_walk')`
2. **Для малювання**: використовуйте `move_mouse_interpolated()` з `curve_type='catmull'`
3. **Для анімації**: комбінуйте `move_mouse_sine()`, `move_mouse_spiral()`, `move_mouse_circle()`
4. **Для скритих дій**: використовуйте `move_mouse_random_walk()` з більшою тривалістю
5. **Для тестування**: використовуйте `move_mouse_composite()` з різними `secondary_noise` значеннями

---

## Встановлення залежностей

```bash
pip install pynput
```

Всі модулі в `plugins/` готові до використання після встановлення `pynput`.

---

## Примітки щодо безпеки

- Усі функції управління мишею та клавіатурою можуть контролювати ваш комп'ютер
- Завжди протестуйте скрипти на маленькому діапазоні координат перед повномасштабним використанням
- Збережіть можливість зупинити скрипт (наприклад, Ctrl+C або переміщення миші в кут екрану)
