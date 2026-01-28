# Базовий функціонал: модуль `base`

Модуль `base` містить набір корисних функцій для повсякденних задач: арифметика, робота зі списками та словниками, перетворення типів, рядкові операції, випадкові значення та час.

## Арифметика
- `add(a, b)`, `subtract(a, b)`, `multiply(a, b)`, `divide(a, b)`

```aml
import_py { console, base }
var s = base.add(10, 20)
var q = base.divide(9, 3)
console.print_line("s=" + s + ", q=" + q)
```

## Списки
- Створення: `create_list(a, b, ...)`
- Додавання: `append_to_list(lst, x)`
- Довжина: `list_length(lst)`
- Індекс/встановлення: `get_list_item(lst, i)`, `set_list_item(lst, i, v)`
- Розширення/вставка: `extend_list(lst, other)`, `insert_into_list(lst, i, v)`
- Пошук: `index_of(lst, v)`, `list_contains(lst, v)`
- Слайс: `slice_list(lst, start, end, step)`
- Конкатенація: `concat_lists(a, b)`
- Сортування/реверс: `sort_list(lst)`, `reverse_list(lst)`
- Унікальні: `unique_list(lst)`

```aml
import_py { console, base }
var xs = base.create_list(3, 1, 2)
base.sort_list(xs)
console.print_line(base.to_str(xs)) // [1,2,3]
console.print_line("містить 2: " + base.list_contains(xs, 2))
```

## Словники
- Доступ: `dict_get(d, key)`, `dict_set(d, key, v)`
- Перевірка ключа: `has_key(d, key)`
- Ключі/значення/пари: `dict_keys(d)`, `dict_values(d)`, `dict_items(d)`
- Злиття/оновлення: `merge_dicts(a, b)`, `update_dict(d, updates)`

```aml
import_py { console, base }
var d = { name: "AML", ver: 1 }
base.dict_set(d, "active", True)
console.print_line(base.to_str(base.dict_keys(d)))
```

## Перетворення типів
- `to_str(x)`, `to_int(x)`, `to_float(x)`, `to_bool(x)`
- Перевірка типу: `type_of(x)`, `is_number(x)`, `is_string(x)`, `is_list(x)`, `is_dict(x)`, `is_bool(x)`, `is_none(x)`

```aml
import_py { console, base }
var s = base.to_str(123)
console.print_line("type: " + base.type_of(s)) // string
```

## Операції з рядками
- Регістр: `string_lower(s)`, `string_upper(s)`
- Обрізання: `string_trim(s)`
- Пошук: `starts_with(s, p)`, `ends_with(s, sfx)`, `string_contains(s, sub)`
- Розбиття/збірка: `string_split(s, sep)`, `join_strings(items, sep)`
- Слайс: `string_slice(s, start, end, step)`

```aml
import_py { console, base }
var msg = "  Hello AML  "
console.print_line(base.string_trim(msg))
```

## Математика та утиліти
- Абсолютне: `abs_val(x)`
- Підлога/стеля: `floor(x)`, `ceil(x)`, `round_to(x, ndigits)`
- Мін/макс: `min_val(a, b)`, `max_val(a, b)`
- Сума/середнє списку: `sum_list(lst)`, `average_list(lst)`
- Діапазон: `range_list(start, stop, step)`
- Обмеження: `clamp(v, min, max)`

```aml
import_py { console, base }
var nums = base.range_list(0, 5)
console.print_line(base.to_str(nums)) // [0,1,2,3,4]
```

## Випадкові значення
- `random_int(min, max)`, `random_float(min, max)`, `choose(lst)`, `shuffle_list(lst)`

```aml
import_py { console, base }
var r = base.random_int(1, 6)
console.print_line("кубик: " + r)
```

## Час
- Затримки: `wait(sec)`, `sleep_millis(ms)`
- Поточний час (мс): `current_time_ms()`

```aml
import_py { console, base }
console.print_line("початок: " + base.current_time_ms())
base.wait(0.2)
console.print_line("кінець: " + base.current_time_ms())
```