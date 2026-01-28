# Модулі та інтеграції

Огляд корисних модулів, доступних через `import_py { ... }`. Вони розширюють можливості AML для роботи з файлами, системними командами, HTTP, JSON, regex та датою/часом.

## console

Вивід у консоль:
- `print_line(text)` — друкує рядок.
- `print_colored(text, color)` — друкує з кольором (`red`, `green`, `blue`, ...).

```aml
import_py { console }
console.print_line("Привіт")
console.print_colored("Кольорово", "green")
```

## plugins\file

Робота з файлами/папками: `read_file`, `write_file`, `append_file`, `list_dir`, `make_dir`, `remove_dir`, `delete_file`, `copy_file`, `move_file`, `path_join`, `file_exists`, `dir_exists`, `file_size`.

```aml
import_py { console, plugins\file }
var dir = "data"
file.make_dir(dir)
var path = file.path_join(dir, "hello.txt")
file.write_file(path, "Привіт, файл!")
console.print_line(file.read_file(path))
```

## plugins\system

Запуск команд ОС. На Windows використовується PowerShell.
- `run(cmd)` → `{ output, error, code }`
- `run_shell(cmd)` → `{ output, error, code }`
- `which(program)`

```aml
import_py { console, plugins\system }
var res = system.run("Get-ChildItem")
console.print_line(res["output"]) 
```

## plugins\http

Прості HTTP-запити без залежностей: `get(url)`, `post_json(url, obj)`, `post_form(url, data)`.
Повертають словник: `{ ok, status, headers, text, url, error? }`.

```aml
import_py { console, plugins\http, plugins\json }
var r = http.get("https://httpbin.org/get")
if (r["ok"]) {
  var obj = json.parse(r["text"]) // розпарсити JSON
  console.print_line("url: " + obj["url"]) 
} else {
  console.print_line("Помилка: " + r["error"]) 
}
```

## plugins\json

JSON-парсинг та серіалізація:
- `parse(text)` → об’єкт
- `stringify(obj, indent)` → рядок
- `read_json(path)` / `write_json(path, obj, indent)`

```aml
import_py { console, plugins\json }
var obj = json.parse("{\"a\":1}")
console.print_line("a=" + obj["a"])
```

## plugins\regex

Регулярні вирази: `matches`, `search`, `findall`, `replace`.

```aml
import_py { console, plugins\regex, base }
var pat = "[a-z]+@[a-z]+\\.[a-z]+"
var s = regex.search(pat, "mail: a@b.com")
if (s != None) { console.print_line(s["match"]) }
```

## plugins\datetime

Час/дати: `now_iso()`, `timestamp()`, `format_now(fmt)`, `format_timestamp(ts, fmt)`.

```aml
import_py { console, plugins\datetime }
console.print_line(datetime.now_iso())
console.print_line(datetime.format_now("%Y-%m-%d %H:%M"))
```

## plugins\keyboard та plugins\mouse

Автоматизація вводу. Потребують зовнішніх бібліотек (`pynput`, `pyautogui`).
- keyboard: `press_key`, `type_text`, `hotkey`, `input_key`...
- mouse: `move_mouse`, `click_mouse`, `double_click`, `right_click`, `get_mouse_position`...

```aml
import_py { console, plugins\keyboard, plugins\mouse, base }
mouse.move_mouse(200, 200)
base.wait(0.2)
keyboard.type_text("Hello")
```

## import_aml

Імпорт інших AML-скриптів по шляху:

```aml
import_aml { examples\other_script }
```

Імпортовані функції/змінні стають доступними у поточному середовищі.

## native_data

Нативний формат даних та утиліти конвертації/шляхів.
- `as_native(value)` — перетворює Python значення у нативний формат (скаляри/list/dict).
- `to_json(value, pretty=false)` — серіалізує у JSON.
- `from_json(text)` — парсить JSON у нативний формат.
- `get_path(data, path, default)` — отримує значення за шляхом `a.b[0].c`.
- `set_path(data, path, value, create_missing=true)` — встановлює значення за шляхом.
- `merge(a, b)` — глибоке злиття dict/list/скалярів.
- `pretty(value)` — гарно відформатований JSON.

```aml
import_py { console, native_data }

var d = native_data.as_native({"user": {"id": 10, "name": "Ann"}})
console.print_line(native_data.get_path(d, "user.name"))
native_data.set_path(d, "user.id", 11)
var j = native_data.to_json(d)
console.print_line(j)
```

## Доступ до рантайму у Python‑модулях

Усі модулі, імпортовані через `import_py`, отримують інжектований доступ до рантайму:
- атрибут `_aml_runtime` — проксі для роботи зі змінними/метаданими/скасуванням;
- глобальний модуль `aml_runtime_access` із простим процедурним API.

Приклад у Python‑модулі, який імпортується через `import_py`:

```python
# всередині вашого модуля
from aml_runtime_access import get, define, assign, cancel

def init():
    # прочитати змінну AML
    name = get("user.name")
    # оголосити нову змінну
    define("py.ready", True)
    # змінити значення у неймспейсі
    assign("app.counter", 1)
    # за потреби — кооперативне скасування
    # cancel()

# або через інжектований атрибут
def set_flag():
    runtime = globals().get("_aml_runtime")
    if runtime:
        runtime.define("flags.py", 1)
```