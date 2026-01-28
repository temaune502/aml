# Документація до модуля `automation`

Модуль `automation` надає функції для автоматизації керування мишею та клавіатурою, а також допоміжні утиліти. Для роботи з мишею використовується бібліотека `pynput`.

---

## Функції модуля

### get_screen_size()
- **Аргументи:** немає
- **Повертає:** кортеж (width, height) — розміри екрану в пікселях. Якщо не вдалося визначити — (0, 0).

### get_mouse_position()
- **Аргументи:** немає
- **Повертає:** кортеж (x, y) — поточна позиція миші на екрані в пікселях.

### move_mouse_smooth(x, y, duration=0.5, steps=20)
- **Аргументи:**
    - `x`, `y` — координати кінцевої точки (int)
    - `duration` — тривалість руху (секунди, float)
    - `steps` — кількість кроків (int)
- **Повертає:** нічого. Переміщує мишу плавно до (x, y).

### move_mouse_relative_smooth(dx, dy, duration=0.5, steps=20)
- **Аргументи:**
    - `dx`, `dy` — зміщення по осях (int)
    - `duration`, `steps` — як у move_mouse_smooth
- **Повертає:** нічого. Переміщує мишу відносно поточної позиції.

### drag_smooth(x, y, duration=0.5, button='left')
- **Аргументи:**
    - `x`, `y` — координати кінцевої точки (int)
    - `duration` — тривалість (float)
    - `button` — кнопка миші ('left', 'right', 'middle')
- **Повертає:** нічого. Плавно перетягує мишу з натиснутою кнопкою.

### scroll(clicks, direction='vertical')
- **Аргументи:**
    - `clicks` — кількість кліків коліщатка (int)
    - `direction` — 'vertical' або 'horizontal'
- **Повертає:** нічого. Прокручує екран.

### clamp_to_screen(x, y)
- **Аргументи:**
    - `x`, `y` — координати (int)
- **Повертає:** кортеж (x, y), обмежений розмірами екрану.

### move_mouse_to_ratio(rx, ry, duration=0.5, steps=20)
- **Аргументи:**
    - `rx`, `ry` — відносні координати (0..1, float)
    - `duration`, `steps` — як у move_mouse_smooth
- **Повертає:** нічого. Переміщує мишу у відносну позицію.

### move_mouse_path(points, per_segment_duration=0.4, steps_per_segment=20)
- **Аргументи:**
    - `points` — список кортежів [(x1, y1), (x2, y2), ...]
    - `per_segment_duration` — тривалість руху між точками (float)
    - `steps_per_segment` — кроків між точками (int)
- **Повертає:** нічого. Плавно переміщує мишу по заданому шляху.

### move_mouse_bezier_to(x, y, duration=0.8, steps=40, c1=None, c2=None, jitter=0)
- **Аргументи:**
    - `x`, `y` — кінцева точка (int)
    - `duration`, `steps` — як у move_mouse_smooth
    - `c1`, `c2` — контрольні точки (tuple) або None
    - `jitter` — випадковий зсув контрольних точок (int)
- **Повертає:** нічого. Плавно переміщує мишу по кривій Безьє.

### mouse_down(button='left')
- **Аргументи:**
    - `button` — кнопка миші ('left', 'right', 'middle')
- **Повертає:** нічого. Натискає кнопку миші.

### mouse_up(button='left')
- **Аргументи:**
    - `button` — кнопка миші ('left', 'right', 'middle')
- **Повертає:** нічого. Відпускає кнопку миші.

### click(button='left', x=None, y=None, count=1, interval=0.05, smooth=False, duration=0.2, steps=15)
- **Аргументи:**
    - `button` — кнопка миші ('left', 'right', 'middle')
    - `x`, `y` — координати (int) або None
    - `count` — кількість кліків (int)
    - `interval` — затримка між кліками (float)
    - `smooth` — чи переміщати плавно (bool)
    - `duration`, `steps` — для плавного руху
- **Повертає:** нічого. Виконує клік(и) мишею.

### double_click(x=None, y=None, button='left', smooth=False, duration=0.2, steps=15)
- **Аргументи:**
    - як у click
- **Повертає:** нічого. Подвійний клік мишею.

### right_click(x=None, y=None, smooth=False, duration=0.2, steps=15)
- **Аргументи:**
    - як у click, але кнопка завжди 'right'
- **Повертає:** нічого. Правий клік мишею.

### drag_to_smooth(x, y, duration=0.5, steps=20, button='left')
- **Аргументи:**
    - як у drag_smooth
- **Повертає:** нічого. Плавно перетягує мишу з натиснутою кнопкою.

### drag_relative_smooth(dx, dy, duration=0.5, steps=20, button='left')
- **Аргументи:**
    - як у move_mouse_relative_smooth, але з натиснутою кнопкою
- **Повертає:** нічого.

### scroll_smooth(clicks, duration=0.5, steps=10, direction='vertical')
- **Аргументи:**
    - як у scroll, але прокрутка розбивається на кроки
- **Повертає:** нічого.

---

## Клавіатурні функції

### press_key(key)
- **Аргументи:**
    - `key` — символ або спецклавіша (str)
- **Повертає:** нічого. Натискає і відпускає клавішу.

### hold_key(key)
- **Аргументи:**
    - `key` — символ або спецклавіша (str)
- **Повертає:** нічого. Натискає клавішу (утримує).

### release_key(key)
- **Аргументи:**
    - `key` — символ або спецклавіша (str)
- **Повертає:** нічого. Відпускає клавішу.

### hotkey(*keys)
- **Аргументи:**
    - `*keys` — послідовність клавіш (str), наприклад 'ctrl', 'shift', 'a'
- **Повертає:** нічого. Натискає комбінацію клавіш.

### hotkey_sequence(sequences, interval=0.1)
- **Аргументи:**
    - `sequences` — список списків клавіш, наприклад [['ctrl','c'], ['ctrl','v']]
    - `interval` — затримка між комбінаціями (float)
- **Повертає:** нічого.

### type_text(text, interval=0.01)
- **Аргументи:**
    - `text` — рядок для введення (str)
    - `interval` — затримка між символами (float)
- **Повертає:** нічого. Вводить текст.

### type_text_human(text, min_interval=0.01, max_interval=0.05)
- **Аргументи:**
    - `text` — рядок для введення (str)
    - `min_interval`, `max_interval` — межі випадкової затримки (float)
- **Повертає:** нічого. Вводить текст з імітацією людини.

### wait_for_key(target_key=None, timeout=None)
- **Аргументи:**
    - `target_key` — очікувана клавіша (str) або None (будь-яка)
    - `timeout` — таймаут у секундах (float) або None
- **Повертає:** рядок з назвою натиснутої клавіші або None (якщо таймаут).

---

## Допоміжні функції

### tuple_to_list(obj)
- **Аргументи:**
    - `obj` — будь-який об'єкт (tuple, list, set, ...)
- **Повертає:** список, якщо obj — кортеж (рекурсивно), інакше obj без змін.

---

## Просунуті рухи миші (криві та траєкторії)

### move_mouse_sine(start, end, amplitude=50, frequency=2, duration=0.5, button_hold=None)
- **Аргументи:**
    - `start`, `end` — початкова та кінцева координати (x, y)
    - `amplitude` — відхилення від прямої лінії (пікселі)
    - `frequency` — кількість коливань
    - `duration` — час руху (секунди)
    - `button_hold` — кнопка миші для утримування ('left', 'right', None)
- **Повертає:** нічого. Рухає мишу по синусоїді.

### move_mouse_spiral(center, start_radius=10, end_radius=100, turns=2, duration=0.5)
- **Аргументи:**
    - `center` — центр спіралі (x, y)
    - `start_radius`, `end_radius` — стартовий та кінцевий радіус (пікселі)
    - `turns` — кількість обертів
    - `duration` — час руху (секунди)
- **Повертає:** нічого. Рухає мишу по спіралі.

### move_mouse_circle(center, radius, steps_count=100, start_angle=0, end_angle=360, duration=0.5)
- **Аргументи:**
    - `center` — центр кола (x, y)
    - `radius` — радіус кола (пікселі)
    - `steps_count` — кількість точок вздовж дуги
    - `start_angle`, `end_angle` — межі дуги (градуси)
    - `duration` — час руху (секунди)
- **Повертає:** нічого. Рухає мишу по круговій дузі.

### move_mouse_zigzag(start, end, amplitude=30, zigzags=5, duration=0.5)
- **Аргументи:**
    - `start`, `end` — початкова та кінцева координати (x, y)
    - `amplitude` — амплітуда зигзагу (пікселі)
    - `zigzags` — кількість зигзагів
    - `duration` — час руху (секунди)
- **Повертає:** нічого. Рухає мишу зигзагоподібно.

### move_mouse_random_walk(start, end, step_size=10, duration=0.5)
- **Аргументи:**
    - `start`, `end` — початкова та кінцева координати (x, y)
    - `step_size` — макс. переміщення за крок (пікселі)
    - `duration` — час руху (секунди)
- **Повертає:** нічого. Рухає мишу випадковим маршрутом (природний, непередбачуваний).

### move_mouse_noisy(start, end, sigma=20, duration=0.5)
- **Аргументи:**
    - `start`, `end` — початкова та кінцева координати (x, y)
    - `sigma` — стандартне відхилення шуму (пікселі)
    - `duration` — час руху (секунди)
- **Повертає:** нічого. Рухає мишу з додаванням гаусівського шуму (як людина).

### move_mouse_interpolated(points, steps_per_segment=10, curve_type='catmull', duration=0.5)
- **Аргументи:**
    - `points` — список вузлових точок [(x1, y1), (x2, y2), ...]
    - `steps_per_segment` — кроків інтерполяції між точками
    - `curve_type` — 'linear', 'quadratic', 'cubic', 'catmull'
    - `duration` — час руху (секунди)
- **Повертає:** нічого. Рухає мишу плавно через список вузлових точок.

### move_mouse_composite(start, end, pattern='sine', secondary_noise=5, duration=0.5)
- **Аргументи:**
    - `start`, `end` — початкова та кінцева координати (x, y)
    - `pattern` — первинний патерн ('sine', 'zigzag', 'random_walk', 'spiral')
    - `secondary_noise` — сигма вторинного шуму (0 = без шуму)
    - `duration` — час руху (секунди)
- **Повертає:** нічого. Комбінує первинний патерн з вторинним шумом для реалізму.

---

## Примітки
- Для роботи більшості функцій потрібна встановлена бібліотека `pynput`.
- На Windows для визначення розміру екрану використовується WinAPI.
- Просунуті рухи миші потребують модуля `curves.py`.
- Якщо функція не може виконати дію (наприклад, pynput не встановлено), вона виведе попередження і нічого не зробить.
