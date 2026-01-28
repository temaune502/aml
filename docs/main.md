# AML - Automation Macro Language

AML (Automation Macro Language) - це інтерпретована мова програмування на базі Python, створена для автоматизації задач. Мова має простий синтаксис, схожий на Python, але з деякими спрощеннями для полегшення парсингу.

## Особливості мови

- Інтерпретована мова на базі Python
- Можливість імпорту Python функцій та класів
- Можливість імпорту інших AML файлів
- Простий синтаксис без крапки з комою в кінці рядків
- Підтримка змінних, функцій, циклів, умов, списків та масивів
- Розширювана архітектура

## Синтаксис

### Імпорт Python модулів
```
import_py {
    base
    plugins\mouse
    plugins\keyboard
    console
}
```

### Імпорт AML файлів
```
import_aml {
    some_file
    some_file2
}
```

### Визначення змінних
```
var some = 131
var some2 = -123
var some3 = some + some2
```

### Виклик функцій
```
var func_return = some_func(a, b)
some_func2()
```

### Визначення функцій
```
func name(arg, args) {
    // код функції
}
```

### Namespace (простори імен)
```
namespace util {
    func add(a, b) {
        return a + b
    }
    var greeting = "Hi"
}

// Виклик функції у namespace
var r = util.add(2, 3)
console.print_line("util.add: " + base.to_str(r))
```

### Асинхронний виклик функції (spawn)
```
// Запуск функції у окремому потоці
var task = spawn long_running()

// Очікування завершення та отримання результату
task.join()
console.print_line("Результат: " + base.to_str(task.result))

// Також підтримується виклик методу: spawn util.add(1,2)
```
Примітка: асинхронні AML-функції виконуються паралельно у потоках.
Спільні змінні можуть оновлюватися без синхронізації, тому рекомендується
повертати значення через `return` та не модифікувати глобальний стан у spawn.

### Робота зі списками
```
var list = [1, 2, 23, 3, 4, 4, 5, 6, 544737457, 3464, -34343, -34327, -4765, -342342]
```

### Робота з Python класами
```
var python_class_instance = Python.Some_imported_class(arg, args)
python_class_instance.some_func_in_class()
```

## Інтеграція з Python (AMLRuntime)
Ви можете інтегрувати AML у свій Python-проєкт через `AMLRuntime`:
```
from aml_runtime import AMLRuntime

rt = AMLRuntime(
    default_py_modules=["base", "plugins\\file", "plugins\\system"],
    default_aml_modules=["examples\\other_script"],
    aml_search_paths=["."],
    python_search_paths=["."]
)

rt.start()
rt.set_variable("name", "Світ")
rt.run_source("console.print_line('Привіт, ' + name)")

# Отримання змінних
val = rt.get_variable("name")

# Імпорт додаткових модулів
rt.import_py(["plugins\\keyboard"])  # потребує встановлений pynput

# Зупинка виконання (кооперативна)
rt.stop()
```

### Крапковий доступ до змінних та функцій (dotted names)
`AMLRuntime` підтримує крапкові імена для доступу до змінних та виклику функцій у просторах імен та об'єктах.

```
from aml_runtime import AMLRuntime

rt = AMLRuntime(default_py_modules=["base", "console"], aml_search_paths=["."], python_search_paths=["."])
rt.start()

# Створюємо namespace та додаємо змінні/функції
ns = rt.create_namespace('a')
rt.set_namespace_var('a', 'x', 10)
rt.set_variable('a.y', 'hello')              # крапковий set
print(rt.get_variable('a.x'))                # => 10
print(rt.get_variable('a.y'))                # => "hello"

# Додаємо Python-функцію у namespace та викликаємо її
rt.add_namespace_function('a', 'sum_two', lambda a, b: a + b)
print(rt.call_function('a.sum_two', 1, 2))   # => 3

# Якщо у AML визначено: namespace a { func main() { return "aaa" } }
# то з Python можна викликати:
print(rt.call_function('a.main'))            # => "aaa"

rt.stop()
```

### Namespace API з Python
`AMLRuntime` надає повний набір методів для роботи з просторами імен:
- `create_namespace(name)` — створює/повертає `Namespace` у корені.
- `get_namespace(name)` — повертає існуючий `Namespace` або кидає помилку.
- `set_namespace_var(ns_name, var_name, value)` — встановлює значення змінної у namespace.
- `get_namespace_var(ns_name, var_name)` — отримує значення змінної у namespace.
- `add_namespace_function(ns_name, func_name, func)` — додає AML `Function` або Python `callable` у namespace.
- `add_namespace_functions(ns_name, mapping)` — пакетне додавання кількох функцій.

Також для роботи зі змінними можна використовувати крапкові імена напряму:
- `set_variable('a.some', value)`
- `get_variable('a.some')`
- `override_variable('a.some', new_value)`

Зверніть увагу: крапковий доступ працює не лише для `Namespace`, а й для будь-яких Python-об'єктів та словників, що зберігаються у середовищі AML.