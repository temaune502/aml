# 📚 Розширена документація нових модулів

## Огляд нових модулів

У цьому розділі описані 5 потужних модулів, які розширюють функціональність бібліотеки automation:

### 1. **ocr.py** - Розпізнавання тексту (OCR)
Модуль для читання тексту з екрану та зображень за допомогою Tesseract OCR.

### 2. **screen.py** - Робота з екраном
Модуль для зміни скріншотів, пошуку зображень, аналізу змін на екрані.

### 3. **recorder.py** - Запис та відтворення макросів
Модуль для запису послідовності дій користувача та їх автоматичного відтворення.

### 4. **sensor.py** - Моніторинг подій
Модуль для моніторингу екрану в реальному часі та обробки подій.

### 5. **performance.py** - Оптимізація та аналіз
Модуль для вимірювання продуктивності, логування та асинхронного виконання.

---

## 1. OCR Модуль (ocr.py)

### Опис
Дозволяє розпізнавати текст з екрану та зображень, знаходити текстові блоки, аналізувати кольори пікселів.

### Встановлення залежностей
```bash
pip install pytesseract pillow numpy
# Встановіть також Tesseract OCR:
# Windows: Завантажте з https://github.com/UB-Mannheim/tesseract/wiki
```

### Основні функції

#### `read_text_from_screen(region=None, lang='ukr', config='')`
Прочитати текст з екрану за допомогою OCR.

```python
from plugins import ocr

# Прочитати весь текст з екрану
text = ocr.read_text_from_screen()
print(text)

# Прочитати текст з певної області
text = ocr.read_text_from_screen(region=(100, 100, 500, 300))

# Англійська мова
text = ocr.read_text_from_screen(lang='eng')
```

#### `get_text_boxes(region=None, lang='ukr')`
Отримати координати та впевненість розпізнавання текстових блоків.

```python
from plugins import ocr

# Отримати текстові блоки з їх позиціями
boxes = ocr.get_text_boxes()

for box in boxes:
    print(f"Текст: {box['text']}")
    print(f"Позиція: ({box['x']}, {box['y']})")
    print(f"Розмір: {box['w']}x{box['h']}")
    print(f"Впевненість: {box['conf']}%")
```

#### `find_text_on_screen(text, region=None, lang='ukr')`
Знайти текст на екрані та повернути його координати.

```python
from plugins import ocr

# Знайти текст на екрані
coords = ocr.find_text_on_screen("Зберегти")
if coords:
    x, y, w, h = coords
    print(f"Текст знайдено на позиції ({x}, {y})")
```

#### `get_pixel_color(x, y)`
Отримати RGB колір пікселя на координатах.

```python
from plugins import ocr

# Отримати колір пікселя
r, g, b = ocr.get_pixel_color(100, 200)
print(f"Колір: RGB({r}, {g}, {b})")
```

#### `find_color_on_screen(color, threshold=10, region=None)`
Знайти всі пікселі певного кольору на екрані.

```python
from plugins import ocr

# Знайти всі червоні пікселі
red = (255, 0, 0)
matches = ocr.find_color_on_screen(red, threshold=20)
print(f"Знайдено {len(matches)} червоних пікселів")
```

#### `wait_for_text(text, timeout=30, interval=0.5, lang='ukr')`
Чекати поки текст з'явиться на екрані.

```python
from plugins import ocr

# Чекати появи тексту
if ocr.wait_for_text("Завантаження завершено", timeout=60):
    print("Текст знайдено!")
else:
    print("Таймаут")
```

---

## 2. Screen Модуль (screen.py)

### Опис
Модуль для роботи зі скріншотами, пошуку зображень, виділення областей та аналізу змін на екрані.

### Встановлення залежностей
```bash
pip install pillow numpy opencv-python
```

### Основні функції

#### `save_screenshot(filepath, region=None)`
Зберегти скріншот у файл.

```python
from plugins import screen

# Зберегти весь екран
screen.save_screenshot("screenshot.png")

# Зберегти частину екрану
screen.save_screenshot("region.png", region=(0, 0, 800, 600))
```

#### `find_image_on_screen(template_path, confidence=0.8, region=None)`
Знайти шаблон зображення на екрані.

```python
from plugins import screen

# Знайти кнопку на екрані
coords = screen.find_image_on_screen("button.png", confidence=0.9)
if coords:
    x, y = coords
    print(f"Кнопка знайдена в центрі ({x}, {y})")
```

#### `find_image_all(template_path, confidence=0.8, region=None)`
Знайти всі входження шаблону на екрані.

```python
from plugins import screen

# Знайти всі іконки
matches = screen.find_image_all("icon.png", confidence=0.85)
for i, (x, y) in enumerate(matches):
    print(f"Іконка {i+1}: ({x}, {y})")
```

#### `detect_changes(screenshot1, screenshot2, threshold=30)`
Виявити зміни між двома скріншотами.

```python
from plugins import screen
from PIL import ImageGrab

# Взяти перший скріншот
img1 = ImageGrab.grab()

# Зробити якісь дії...

# Взяти другий скріншот
img2 = ImageGrab.grab()

# Порівняти
has_changes, change_pct, diff_img = screen.detect_changes(img1, img2)
print(f"Змінилось: {change_pct:.2f}%")
```

#### `split_screen_grid(cols=2, rows=2)`
Розділити екран на сітку областей.

```python
from plugins import screen

# Розділити екран на 3x3 сітку
regions = screen.split_screen_grid(cols=3, rows=3)

for name, (x1, y1, x2, y2) in regions.items():
    print(f"{name}: ({x1}, {y1}) -> ({x2}, {y2})")
```

#### `get_dominant_color(region=None)`
Отримати домінуючий колір області.

```python
from plugins import screen

# Отримати домінуючий колір екрану
r, g, b = screen.get_dominant_color()
print(f"Домінуючий колір: RGB({r}, {g}, {b})")
```

#### `wait_for_screen_change(timeout=30, interval=0.5, threshold=30)`
Чекати поки екран змінюється.

```python
from plugins import screen

if screen.wait_for_screen_change(timeout=60):
    print("Екран змінився!")
```

#### `wait_for_image(template_path, timeout=30, interval=0.5, confidence=0.8)`
Чекати поки зображення з'явиться на екрані.

```python
from plugins import screen

if screen.wait_for_image("dialog.png", timeout=30):
    print("Діалог з'явився!")
```

---

## 3. Recorder Модуль (recorder.py)

### Опис
Дозволяє записувати послідовність дій користувача та відтворювати їх як макроси.

### Основні класи

#### Клас `Recorder`
Основний клас для запису та управління макросами.

```python
from plugins.recorder import Recorder

# Створити макрос
recorder = Recorder("my_macro")

# Почати запис
recorder.start_recording()

# Записати дії
recorder.record_mouse_move(100, 100)
recorder.record_mouse_click(100, 100, button="left")
recorder.record_text("Привіт")
recorder.record_wait(1.0)

# Зупинити запис
recorder.stop_recording()

# Зберегти макрос
recorder.save("macros/my_macro.json")
```

#### Методи запису дій

```python
# Рух миші
recorder.record_mouse_move(x=500, y=300)

# Клацання миші
recorder.record_mouse_click(x=500, y=300, button="left", count=1)

# Гортання
recorder.record_mouse_scroll(x=500, y=300, dx=0, dy=3)

# Натиск клавіші
recorder.record_key_press(key="Enter")

# Введення тексту
recorder.record_text("Текст для вводу")

# Пауза
recorder.record_wait(duration=2.0)
```

#### Відтворення макросів

```python
# Завантажити макрос
recorder = Recorder()
recorder.load("macros/my_macro.json")

# Відтворити 1 раз
recorder.playback(loop_count=1, speed=1.0)

# Відтворити 3 рази з половинною швидкістю
recorder.playback(loop_count=3, speed=2.0)

# Відтворити у фоновому потоці
thread = recorder.playback_async(loop_count=1)
```

#### Редагування макросів

```python
recorder = Recorder()
recorder.load("macros/my_macro.json")

# Редагувати дію за індексом
recorder.edit_action(0, x=600, y=400)

# Видалити дію
recorder.delete_action(2)

# Отримати статистику
stats = recorder.get_statistics()
print(stats)

# Збереги зміни
recorder.save("macros/my_macro.json")
```

---

## 4. Sensor Модуль (sensor.py)

### Опис
Модуль для моніторингу екрану та обробки подій у реальному часі.

### Основні класи

#### Клас `Sensor`
Основний клас для моніторингу.

```python
from plugins.sensor import Sensor, EventType

# Створити сенсор
sensor = Sensor("my_sensor")

# Додати слухача подій
def on_screen_change(event):
    print(f"Екран змінився: {event.data}")

sensor.add_listener(EventType.SCREEN_CHANGE, on_screen_change)

# Почати моніторинг
sensor.start_monitoring(check_interval=1.0, log_file="events.log")

# ... робити дії ...

# Зупинити моніторинг
sensor.stop_monitoring()

# Отримати статистику
stats = sensor.get_event_statistics()
print(stats)
```

#### Обробка подій

```python
from plugins.sensor import Sensor, EventType

sensor = Sensor("my_sensor")

# Клацання миші
def on_click(event):
    print(f"Клацання миші в ({event.data['x']}, {event.data['y']})")

# Подія з фільтром
def filter_important(event):
    return event.data.get('important', False)

sensor.add_listener(
    EventType.MOUSE_CLICK,
    on_click,
    filter_func=filter_important
)

# Чекати певну подію
event = sensor.wait_for_event(EventType.SCREEN_CHANGE, timeout=30)
if event:
    print(f"Подія виявлена: {event.to_dict()}")
```

#### Експорт подій

```python
# Експортувати подій у JSON
sensor.export_events("events.json")

# Очистити історію подій
sensor.clear_history()

# Отримати останні подій
recent = sensor.get_recent_events(count=50)
```

#### ScreenSensor

```python
from plugins.sensor import ScreenSensor

# Спеціалізований сенсор для екрану
screen_sensor = ScreenSensor()

def on_change(event):
    print("Екран змінився!")

screen_sensor.add_listener(EventType.SCREEN_CHANGE, on_change)
screen_sensor.start_monitoring()
```

---

## 5. Performance Модуль (performance.py)

### Опис
Модуль для вимірювання продуктивності, логування та асинхронного виконання.

### Основні компоненти

#### Таймер

```python
from plugins.performance import SimpleTimer

# Використання як контекстний менеджер
with SimpleTimer("my_operation") as timer:
    # робити щось
    time.sleep(1)

print(timer)  # Виведе: my_operation: 1.0023 сек
```

#### Декоратор для вимірювання часу

```python
from plugins.performance import measure_time

@measure_time
def slow_operation():
    time.sleep(2)
    return "готово"

result = slow_operation()
# Виведе: ✓ slow_operation: 2.0045 сек
```

#### Повторне виконання при помилці

```python
from plugins.performance import retry
import random

@retry(max_attempts=3, delay=1.0, backoff=2.0)
def unstable_operation():
    if random.random() < 0.7:
        raise Exception("Помилка!")
    return "успіх"

try:
    result = unstable_operation()
except Exception as e:
    print(f"Не вдалось: {e}")
```

#### Кешування результатів

```python
from plugins.performance import cache

@cache(ttl=60.0)  # Кеш на 60 секунд
def expensive_calculation(x, y):
    return x + y

# Перший виклик - реальний розрахунок
result1 = expensive_calculation(10, 20)  # Обчислюється

# Другий виклик - з кешу
result2 = expensive_calculation(10, 20)  # З кешу

# Очистити кеш
expensive_calculation.clear_cache()
```

#### Логгер

```python
from plugins.performance import Logger, LogLevel

# Створити логгер
logger = Logger(
    "my_app",
    log_file="app.log",
    min_level=LogLevel.INFO
)

# Логувати повідомлення
logger.debug("Деталь для налагодження")
logger.info("Інформація")
logger.warning("Попередження")
logger.error("Помилка")

# Отримати повідомлення
messages = logger.get_messages(level=LogLevel.ERROR)
```

#### Батчинг операцій

```python
from plugins.performance import Batch

# Створити батч
batch = Batch(batch_size=100, timeout=5.0)

# Додавати елементи
for i in range(250):
    should_flush = batch.add(f"item_{i}")
    
    if should_flush or batch.should_flush():
        items = batch.flush()
        # Обробити батч
        print(f"Обробляю {len(items)} елементів")
```

#### Асинхронний пул задач

```python
from plugins.performance import AsyncTaskPool
import time

def process_item(item):
    time.sleep(1)
    return item * 2

# Створити пул з 4 робітниками
pool = AsyncTaskPool(max_workers=4)

# Додавати задачі
for i in range(10):
    pool.submit(process_item, i)

# Чекати завершення
results = pool.wait_all(timeout=30)
print(results)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

pool.shutdown()
```

#### Монітор продуктивності

```python
from plugins.performance import PerformanceMonitor

# Створити монітор
monitor = PerformanceMonitor()

# Записати метрики
monitor.record_metric("operation_1", 0.25, success=True)
monitor.record_metric("operation_2", 1.50, success=True)
monitor.record_metric("operation_3", 0.10, success=False, error_message="Помилка")

# Отримати статистику
stats = monitor.get_statistics()
for op, data in stats.items():
    print(f"{op}: {data['count']} разів, {data['avg_time']:.3f} сек")

# Експортувати метрики
monitor.export_metrics("metrics.json")
```

---

## Комбіновані приклади

### Приклад 1: Автоматизація з OCR та Recorder

```python
from plugins import automation, ocr
from plugins.recorder import Recorder

# Записати дії для заповнення форми
recorder = Recorder("fill_form")
recorder.start_recording()

# Знайти поле для імені
coords = ocr.find_text_on_screen("Ім'я:")
if coords:
    x, y = coords[0] + 100, coords[1]
    automation.click(x, y)
    automation.type_text("Іван")

recorder.stop_recording()
recorder.save("form_filler.json")

# Відтворити макрос кілька разів
recorder.playback(loop_count=5)
```

### Приклад 2: Моніторинг з сенсором

```python
from plugins.sensor import Sensor, EventType
from plugins import screen

sensor = Sensor()

def on_change(event):
    # Зберегти скріншот при зміні
    screen.save_screenshot(f"changes/screen_{event.timestamp:.0f}.png")

sensor.add_listener(EventType.SCREEN_CHANGE, on_change)
sensor.start_monitoring(log_file="monitor.log")

# Чекати 5 хвилин
import time
time.sleep(300)

sensor.stop_monitoring()
sensor.export_events("events.json")
```

### Приклад 3: Оптимізована пакетна обробка

```python
from plugins.performance import AsyncTaskPool, measure_time

@measure_time
def process_file(filename):
    # Обробити файл
    return f"processed_{filename}"

files = [f"file_{i}.txt" for i in range(100)]
pool = AsyncTaskPool(max_workers=8)

for file in files:
    pool.submit(process_file, file)

results = pool.wait_all()
print(f"Оброблено {len(results)} файлів")
pool.shutdown()
```

---

## Залежності та встановлення

### Для OCR модуля
```bash
pip install pytesseract pillow numpy
```
Встановіть Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki

### Для Screen модуля
```bash
pip install pillow numpy opencv-python
```

### Для інших модулів (вже встановлені)
```bash
pip install pynput
```

### Повне встановлення
```bash
pip install pytesseract pillow numpy opencv-python pynput
```
