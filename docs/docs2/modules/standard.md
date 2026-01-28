# Стандартні модулі AML

Ця документація описує базові модулі, доступні в папці `temaune/`.

## 1. Математика (`temaune/math/core`)

Модуль для виконання математичних операцій.

- `abs(n)`: Модуль числа.
- `pow(base, exp)`: Піднесення до степеня.
- `sqrt(n)`: Квадратний корінь.
- `sin(x)`, `cos(x)`, `tan(x)`: Тригонометричні функції.
- `floor(n)`, `ceil(n)`: Округлення.
- `min(a, b)`, `max(a, b)`: Мінімальне та максимальне значення.
- `gcd(a, b)`, `lcm(a, b)`: НСД та НСК.

## 2. Робота з рядками (`temaune/string/utils`)

- `upper(s)`, `lower(s)`: Зміна регістру.
- `trim(s)`: Видалення пробілів по краях.
- `split(s, sep)`: Розбиття рядка на список.
- `join(list, sep)`: Об'єднання списку в рядок.
- `replace(s, old, new)`: Заміна підрядка.
- `contains(s, sub)`: Перевірка наявності підрядка.
- `starts_with(s, prefix)`, `ends_with(s, suffix)`: Перевірка початку/кінця рядка.

## 3. Колекції (`temaune/collections/list`)

- `len(list)`: Довжина списку або словника.
- `append(list, item)`: Додавання елемента в кінець.
- `remove(list, index)`: Видалення за індексом.
- `first(list)`, `last(list)`: Перший та останній елементи.
- `reverse(list)`: Розвертає список.
- `sort(list)`: Сортує список.
- `has_key(dict, key)`: Перевірка наявності ключа у словнику.

## 4. Файлова система (`temaune/io/file`)

- `read(path)`: Читання всього файлу.
- `write(path, content)`: Запис у файл.
- `append(path, content)`: Дозапис у файл.
- `exists(path)`: Чи існує файл/папка.
- `copy(src, dst)`, `move(src, dst)`: Копіювання та переміщення.
- `join(a, b)`: Об'єднання шляхів.
- `basename(path)`, `dirname(path)`, `extname(path)`: Робота зі складовими шляху.

## 5. Системні функції (`temaune/sys/env`)

- `get_env(name, default)`: Отримання змінної оточення.
- `os_name()`: Повертає "windows" або "unix".
- `run(cmd)`: Виконання системної команди.
- `sleep(ms)`: Пауза у мілісекундах.

## 6. Мережа (`temaune/net/http`)

- `get(url, params, headers)`: HTTP GET запит.
- `post(url, data, headers)`: HTTP POST запит.
- `put(url, data)`, `patch(url, data)`, `delete(url)`: Інші HTTP методи.

## 7. Події та колбеки (`temaune/sys/event`)

- `on(event_name, callback)`: Підписка на подію. Повертає ID.
- `off(event_name, id)`: Відписка від події.
- `emit(event_name, data)`: Виклик події з передачею даних.

## 8. Автоматизація UI (`temaune/ui/`)

### Клавіатура (`keyboard.aml`)
- `press(key)`: Натиснути клавішу.
- `type(text)`: Набрати текст.
- `hotkey(k1, k2, ...)`: Натиснути комбінацію.
- `wait_key()`: Очікування натискання клавіші.

### Гарячі клавіші (`hotkey.aml`)
- `register(hotkey_str, callback)`: Реєстрація глобальної гарячої клавіші.
- `unregister(id)`: Видалення реєстрації.
