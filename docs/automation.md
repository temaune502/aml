# Модуль `plugins/automation`

Розширений модуль для автоматизації миші та клавіатури в AML. Містить плавні переміщення курсора (абсолютні, відносні, по траєкторіях та Безьє), кліки, перетягування, прокрутку, гарячі комбінації клавіш, друк тексту з людською паузою та інші корисні функції.

- Залежності: `pyautogui` (миша), `pynput` (клавіатура)
- Встановлення: `pip install pyautogui pynput`

## Імпорт у AML

```aml
import_py {
  console
  plugins\automation
  base
}
```

## Функції миші

### get_screen_size()
- Опис: повертає розмір екрана як кортеж `(width, height)`.
- Повертає: `[width, height]` (список у AML).
- Приклад:
```aml
var size = automation.get_screen_size()
console.print_line("Екран: " + base.to_string(size))
```

### get_mouse_position()
- Опис: повертає поточні координати курсора `(x, y)`.
- Повертає: `[x, y]`.
- Приклад:
```aml
var pos = automation.get_mouse_position()
console.print_line("Курсор: " + base.to_string(pos))
```

### move_mouse_smooth(x, y, duration=0.5, steps=20)
- Опис: плавне абсолютне переміщення курсора до координат `(x, y)` з кривою ease-out.
- Аргументи:
  - `x`, `y`: цільові координати (int).
  - `duration`: загальний час руху в секундах (float).
  - `steps`: кількість проміжних кроків (int).
- Приклад:
```aml
automation.move_mouse_smooth(800, 400, 1.0, 30)
```

### move_mouse_relative_smooth(dx, dy, duration=0.5, steps=20)
- Опис: плавний відносний рух курсора на `dx`, `dy` від поточної позиції.
- Аргументи: як у `move_mouse_smooth`, але `dx`, `dy` — відносні зсуви.
- Приклад:
```aml
automation.move_mouse_relative_smooth(120, -60, 0.8, 25)
```

### clamp_to_screen(x, y)
- Опис: обмежує координати межами екрана.
- Повертає: `[cx, cy]` — скореговані координати.
- Приклад:
```aml
var clamped = automation.clamp_to_screen(99999, 99999)
console.print_line(base.to_string(clamped))
```

### move_mouse_to_ratio(rx, ry, duration=0.5, steps=20)
- Опис: рух у позицію, задану як частка від розміру екрана (`0..1`).
- Аргументи:
  - `rx`, `ry`: частки ширини/висоти (float).
  - `duration`, `steps`: див. вище.
- Приклад:
```aml
// Центр екрана
automation.move_mouse_to_ratio(0.5, 0.5, 1.0, 30)
```

### move_mouse_path(points, per_segment_duration=0.4, steps_per_segment=20)
- Опис: рух по списку точок з плавністю для кожного сегмента.
- Аргументи:
  - `points`: список точок `[[x1,y1],[x2,y2],...]`.
  - `per_segment_duration`: тривалість руху на кожен сегмент.
  - `steps_per_segment`: кроків на сегмент.
- Приклад:
```aml
var path = [[200,200],[600,300],[800,700]]
automation.move_mouse_path(path, 0.3, 20)
```

### move_mouse_bezier_to(x, y, duration=0.8, steps=40, c1=None, c2=None, jitter=0)
- Опис: рух за кубічною кривою Безьє від поточної позиції до `(x,y)`.
- Аргументи:
  - `x`, `y`: цільові координати.
  - `duration`: загальний час руху.
  - `steps`: кількість кроків дискретизації.
  - `c1`, `c2`: опціональні контрольні точки `[cx, cy]`, автогенеруються якщо не задані.
  - `jitter`: випадковий відхил для контрольних точок у пікселях.
- Приклад:
```aml
automation.move_mouse_bezier_to(1000, 500, 0.9, 45, jitter=15)
```

### mouse_down(button='left') / mouse_up(button='left')
- Опис: натиснути або відпустити кнопку миші.
- Аргументи: `button` — `'left'|'right'|'middle'`.
- Приклад:
```aml
automation.mouse_down("left")
automation.mouse_up("left")
```

### click(button='left', x=None, y=None, count=1, interval=0.05, smooth=False, duration=0.2, steps=15)
- Опис: клік з опцією плавного підводу до координат перед кліком.
- Аргументи:
  - `button`: тип кнопки.
  - `x`, `y`: опціональні координати для кліку.
  - `count`: кількість кліків.
  - `interval`: пауза між кліками.
  - `smooth`: якщо `true`, перед кліком плавно підвести курсор.
  - `duration`, `steps`: параметри плавного руху.
- Приклад:
```aml
automation.click("left", 900, 400, count=2, smooth=True, duration=0.4, steps=25)
```

### double_click(x=None, y=None, button='left', smooth=False, duration=0.2, steps=15)
- Опис: подвійний клік у поточній або заданій позиції, з опцією плавного підводу.
- Приклад:
```aml
automation.double_click(600, 300, "left", True, 0.3, 20)
```

### right_click(x=None, y=None, smooth=False, duration=0.2, steps=15)
- Опис: правий клік, з опцією плавного підводу.
- Приклад:
```aml
automation.right_click(750, 500, True, 0.25, 15)
```

### drag_smooth(x, y, duration=0.5, button='left')
- Опис: перетягування до координат із вбудованою плавністю (через `pyautogui.dragTo`).
- Приклад:
```aml
automation.drag_smooth(1200, 700, 0.8, "left")
```

### drag_to_smooth(x, y, duration=0.5, steps=20, button='left')
- Опис: перетягування з явним натисканням/відпусканням і плавним рухом у кроках.
- Приклад:
```aml
automation.drag_to_smooth(1000, 600, 0.6, 30, "left")
```

### drag_relative_smooth(dx, dy, duration=0.5, steps=20, button='left')
- Опис: плавне перетягування на відносний вектор.
- Приклад:
```aml
automation.drag_relative_smooth(150, -80, 0.6, 30, "left")
```

### scroll(clicks, direction='vertical')
- Опис: проста прокрутка колесом миші вертикально чи горизонтально.
- Аргументи: `clicks` — кількість «кліків», `direction`: `'vertical'|'horizontal'`.
- Приклад:
```aml
automation.scroll(-500, "vertical")
automation.scroll(50, "horizontal")
```

### scroll_smooth(clicks, duration=0.5, steps=10, direction='vertical')
- Опис: плавна прокрутка, розбита на кроки з паузами.
- Приклад:
```aml
automation.scroll_smooth(-600, 0.8, 12, "vertical")
```

## Функції клавіатури

### hotkey(*keys)
- Опис: натиснути комбінацію клавіш (утримати всі, відпустити у зворотному порядку).
- Аргументи: список рядків клавіш, наприклад `"ctrl"`, `"shift"`, `"a"`.
- Приклад:
```aml
automation.hotkey("ctrl", "shift", "esc")
automation.hotkey("ctrl", "t")
```

### press_key(key) / hold_key(key) / release_key(key)
- Опис: натиснути, утримати або відпустити клавішу.
- Аргументи: `key` — односимвольна або службова (`enter`, `space`, `tab`, `f5`, тощо).
- Приклад:
```aml
automation.press_key("enter")
automation.hold_key("ctrl")
automation.release_key("ctrl")
```

### type_text(text, interval=0.01)
- Опис: надрукувати текст із фіксованою паузою між символами.
- Приклад:
```aml
automation.type_text("Hello AML Automation!", 0.02)
```

### type_text_human(text, min_interval=0.01, max_interval=0.05)
- Опис: надрукувати текст із випадковою паузою між символами (імітація людини).
- Приклад:
```aml
automation.type_text_human("Набір з варіативною паузою", 0.02, 0.08)
```

### hotkey_sequence(sequences, interval=0.1)
- Опис: послідовно виконати кілька комбінацій клавіш.
- Аргументи: `sequences` — список списків клавіш, `interval` — пауза між комбінаціями.
- Приклад:
```aml
automation.hotkey_sequence([["ctrl","c"],["ctrl","v"],["alt","tab"]], 0.2)
```

### wait_for_key(target_key=None, timeout=None)
- Опис: зачекати натискання клавіші. Якщо `target_key` задано, чекає конкретну клавішу. Повертає рядок або `None` при таймауті.
- Приклад:
```aml
console.print_line("Натисніть ESC...")
var pressed = automation.wait_for_key("esc", 10)
if (pressed == "esc") {
  console.print_colored("ESC натиснуто", "green")
} else {
  console.print_colored("Таймаут очікування", "red")
}
```

## Зауваження
- На Windows `pyautogui` може вимагати дозвіл керування мишею/екраном; перевіряйте налаштування безпеки.
- Уникайте занадто малих `duration` і великих `steps`: надмірно дрібні кроки можуть бути нестабільними.
- Для точних сценаріїв варто використовувати `clamp_to_screen` перед рухами/кліками.