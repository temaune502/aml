# Швидкий старт (Quick Start Guide)

Цей посібник допоможе вам швидко почати роботу з модулями `automation` та `curves`.

---

## ⚡ 5 хвилин на старт

### 1. Встановлення

```bash
# Встановити залежність
pip install pynput
```

### 2. Імпорт модулів

```python
from plugins import automation
from plugins import curves
```

### 3. Перший скрипт: керування мишею

```python
from plugins import automation
import time

# Отримати розмір екрану
width, height = automation.get_screen_size()
print(f"Екран: {width}x{height}")

# Отримати поточну позицію миші
x, y = automation.get_mouse_position()
print(f"Миша на: ({x}, {y})")

# Переміщувати мишу на центр екрану
center_x, center_y = width // 2, height // 2
automation.move_mouse_smooth(center_x, center_y, duration=1.0)

# Натиснути ліву кнопку миші
automation.click()

# Кілька кліків
automation.click(count=3, interval=0.2)

# Подвійний клік
automation.double_click()

# Правий клік
automation.right_click()

# Прокрутка вверх
automation.scroll(5)

# Прокрутка вниз
automation.scroll(-3)
```

### 4. Перший скрипт: введення тексту

```python
from plugins import automation

# Введення простого тексту
automation.type_text('Hello World', interval=0.05)

# Введення з імітацією людини
automation.type_text_human('Password123', min_interval=0.05, max_interval=0.15)

# Комбінація клавіш
automation.hotkey('ctrl', 'a')     # Select all
automation.hotkey('ctrl', 'c')     # Copy
automation.hotkey('ctrl', 'v')     # Paste
automation.hotkey('alt', 'f4')     # Close window

# Послідовність комбінацій
automation.hotkey_sequence([
    ['ctrl', 'c'],  # Copy
    ['ctrl', 'v'],  # Paste
], interval=0.5)
```

### 5. Перший скрипт: рухи по кривих

```python
from plugins import automation

# Синусоїдальний рух
automation.move_mouse_sine((100, 100), (600, 400), amplitude=50, frequency=2, duration=1.5)

# Рух по спіралі
automation.move_mouse_spiral((400, 300), start_radius=30, end_radius=150, turns=2, duration=1.5)

# Рух по колу
automation.move_mouse_circle((500, 400), radius=100, steps_count=100, duration=2.0)

# Зигзаг
automation.move_mouse_zigzag((100, 100), (600, 400), amplitude=40, zigzags=5, duration=1.5)

# Рух з природним шумом (як людина)
automation.move_mouse_noisy((100, 100), (600, 400), sigma=20, duration=1.0)

# Рух через вузлові точки
waypoints = [(100, 100), (250, 300), (400, 150), (600, 400)]
automation.move_mouse_interpolated(waypoints, curve_type='catmull', duration=2.0)

# Комбінований рух (синусоїда + шум)
automation.move_mouse_composite((100, 100), (600, 400), pattern='sine', secondary_noise=10, duration=2.0)
```

---

## 🎯 Найпоширеніші завдання

### Завдання 1: Клік по елементу на екрані

```python
from plugins import automation

# Простий клік
automation.click(x=400, y=300)

# Клік з плавним переміщенням
automation.click(x=400, y=300, smooth=True, duration=0.5)

# Рух до елементу з реалістичною траєкторією
automation.move_mouse_noisy((100, 100), (400, 300), sigma=15, duration=0.5)
automation.click()
```

### Завдання 2: Заповнення форми

```python
from plugins import automation
import time

# Поля форми
fields = {
    'name': (300, 100),
    'email': (300, 150),
    'password': (300, 200),
}

data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'password': 'SecurePass123',
}

# Заповнюємо
for field_name, (x, y) in fields.items():
    # Рухаємось до поля
    automation.move_mouse_noisy((automation.get_mouse_position()[0], automation.get_mouse_position()[1]), 
                              (x, y), sigma=10, duration=0.4)
    
    # Кліємо
    automation.click()
    time.sleep(0.2)
    
    # Вводимо текст
    automation.type_text_human(data[field_name], min_interval=0.03, max_interval=0.1)
    time.sleep(0.3)

# Натискаємо Submit
automation.hotkey('tab')
automation.hotkey('enter')
```

### Завдання 3: Гра або інтерактивна анімація

```python
from plugins import automation, curves
import time

# Малюємо спіраль
center = (400, 300)
for i in range(5):
    automation.move_mouse_spiral(center, start_radius=10, end_radius=100, turns=1, duration=0.8)
    time.sleep(0.3)

# Рисуємо з синусоїдою
automation.move_mouse_sine((100, 100), (700, 100), amplitude=80, frequency=3, duration=2.0, button_hold='left')

# Кола
for radius in [50, 100, 150]:
    automation.move_mouse_circle(center, radius=radius, start_angle=0, end_angle=360, duration=1.0)
    time.sleep(0.2)
```

### Завдання 4: Очікування дії користувача

```python
from plugins import automation

# Очікуємо натиску будь-якої клавіші (макс 30 сек)
print("Натисніть будь-яку клавішу...")
key = automation.wait_for_key(timeout=30)
print(f"Ви натиснули: {key}")

# Очікуємо натиску конкретної клавіші
print("Натисніть ESC...")
automation.wait_for_key(target_key='escape')
print("ESC натиснуто!")

# Очікуємо Ctrl+C всередину скрипту
try:
    while True:
        automation.move_mouse_sine((100, 100), (600, 400), amplitude=50, frequency=1, duration=2.0)
except KeyboardInterrupt:
    print("Скрипт зупинено!")
```

### Завдання 5: Генерування траєкторій для аналізу

```python
from plugins import curves

# Генеруємо шляхи різними методами
sine_path = curves.sine_wave((0, 0), (400, 300), amplitude=50, frequency=2, steps=100)
spiral_path = curves.spiral_path((200, 200), start_radius=10, end_radius=100, turns=2, steps=100)
zigzag_path = curves.zigzag_path((0, 0), (400, 300), amplitude=40, zigzags=5, steps=100)

# Аналізуємо
for name, path in [('Sine', sine_path), ('Spiral', spiral_path), ('Zigzag', zigzag_path)]:
    length = curves.path_length(path)
    print(f"{name}: {len(path)} точок, довжина {length:.2f} пікселів")

# Інтерполюємо вузлові точки
waypoints = [(100, 100), (250, 50), (400, 200)]
smooth_path = curves.interpolate_path(waypoints, steps_per_segment=20, curve_type='catmull')
print(f"Інтерпольована: {len(smooth_path)} точок")

# Переискавлюємо для рівномірної швидкості
resampled = curves.resample_path(smooth_path, total_distance=curves.path_length(smooth_path))
print(f"Переискавлена: {len(resampled)} точок")
```

---

## ⚠️ Важливо: безпека і конфіденційність

1. **Завжди тестуйте на маленьких координатах** перед запуском на повний екран
2. **Зберігайте можливість зупинити скрипт:**
   - Натиснути Ctrl+C
   - Або переміщувати мишу в кут екрану (якщо реалізовано)
3. **Не запускайте на критичних системах** без перевірки
4. **Повідомте користувача**, якщо скрипт керуватиме його комп'ютером
5. **Додайте логування** для відстеження дій

---

## 📖 Що далі?

- **Для детальної документації:** читайте [README.md](README.md)
- **Для прикладів:** дивіться `examples_automation.py` та `examples_curves.py`
- **Для документації модулів:** 
  - [`plugins/automation.md`](plugins/automation.md)
  - [`plugins/curves.md`](plugins/curves.md)

---

## 🆘 Розв'язування проблем

### Помилка: "pynput is not installed"
```bash
pip install pynput
```

### Миша не рухається на Linux
pynput може мати обмеження на деяких Linux дистрибутивах. Спробуйте:
```bash
pip install --upgrade pynput
```

### Тексту не вводиться правильно
Спробуйте зменшити затримку:
```python
automation.type_text_human(text, min_interval=0.02, max_interval=0.08)
```

### Скрипт виконується занадто швидко
Додайте затримку:
```python
import time
time.sleep(1)  # Затримка 1 секунда
```

---

## 📝 Шаблон простого скрипту

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from plugins import automation
import time

def main():
    print("Скрипт почав роботу...")
    
    # Ваш код тут
    
    print("Скрипт завершено!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nСкрипт зупинено користувачем")
    except Exception as e:
        print(f"Помилка: {e}")
```

---

## 🎓 Рекомендовані матеріали

1. **Модуль automation:**
   - Функції управління мишею для просунутих рухів
   - Функції клавіатури для введення та комбінацій
   - Допоміжні функції для роботи з екраном

2. **Модуль curves:**
   - Математичні функції для кривих (Bezier, Catmull-Rom)
   - Генератори траєкторій (синусоїда, спіраль, зигзаг)
   - Аналіз та обробка шляхів

---

**Успіхів в автоматизації! 🚀**
