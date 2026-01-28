# Синтаксис AML: огляд з прикладами

Ця сторінка описує основні конструкції мови AML з короткими прикладами коду. AML — проста, зрозуміла DSL із підтримкою неймспейсів, функцій, імпортів модулів та базових структур даних.

## Коментарі
- Однорядкові коментарі починаються з `//`.

```aml
// Це коментар
console.print_line("Hello")
```

## Змінні та типи
- Оголошення змінної: `var name = value`
- Типи: `number`, `string`, `bool` (`True`/`False`), `list`, `dict`, `None`

```aml
var a = 10
var b = 2.5
var s = "строка"
var t = True
var items = [1, 2, 3]
var cfg = { key: "value", count: 3 }
```

## Вирази та оператори
- Арифметика: `+ - * /`
- Порівняння: `== != > >= < <=`
- Логіка: `and`, `or`, `not`

```aml
var sum = 3 + 4
var ok = (sum > 5) and True
```

## Списки та словники
- Індексування списку: `list[idx]`
- Доступ до словника: `dict["key"]`

```aml
var xs = [10, 20, 30]
console.print_line(xs[1]) // 20

var person = { name: "Ada", age: 27 }
console.print_line(person["name"]) // Ada
```

## Умовні оператори
```aml
var x = 7
if (x > 5) {
  console.print_line("x > 5")
} else {
  console.print_line("x <= 5")
}
```

## Цикли
```aml
// while
var i = 0
while (i < 3) {
  console.print_line("i = " + i)
  i = i + 1
}

// for-in по списку
var items = ["a", "b", "c"]
for it in items {
  console.print_line("item: " + it)
}
```

## Функції
- Оголошення: `func name(args) { ... }`
- Повернення значення: `return expr`
- Параметри можна передавати позиційно і за іменем (kwargs) у викликах AML-функцій.

```aml
func add(a, b) {
  return a + b
}
var r = add(2, 3)
console.print_line("result: " + r)

// Виклик із kwargs (прив’язка за іменами)
var r2 = add(a=5, b=7)
console.print_line("result2: " + r2)
```

## Неймспейси
- Групують функції та змінні: `namespace name { ... }`
- Виклик: `ns.func()` або `ns.var`

```aml
namespace mathx {
  func square(x) { return x * x }
}
console.print_line(mathx.square(5))
```

## Імпорт модулів
- Імпорт Python: `import_py { moduleA, plugins\file }`
- Alias для імпорту: `import_py { numpy as np, pandas }`
- Імпорт AML: `import_aml { examples\other_script }`

```aml
import_py { console, base as b, plugins\file }
import_aml { examples\import_example }
console.print_line("Готово")
b.sleep_ms(100)
```

## Обробка помилок (try/catch)
- Блок `catch` має змінну `error` з повідомленням.

```aml
import_py { console, base }
try {
  var x = base.divide(10, 0)
} catch {
  console.print_line("Помилка: " + error)
}
```

## Точка входу
- Рекомендовано мати `namespace app` та виклик `app.main()`.

```aml
import_py { console }
namespace app {
  func main() {
    console.print_line("Hello, AML!")
  }
}
app.main()
```

## Метадані (meta)
- Блок `meta { ... }` задає метадані файлу AML.
- Підтримуються довільні ключі, а також відомі: `version`, `entry`, `author`, `created`, `notes`.
- Якщо задано `entry`, ця функція буде викликана автоматично після виконання топ-рівня.

```aml
import_py { console }

meta {
  version: "1.0.0",
  entry: "app.main",
  author: "Ваше ім’я",
  created: "2025-11-02",
  notes: "Демонстрація метаданих"
}

namespace app {
  func main() {
    console.print_line("MAIN START")
  }
}
// app.main() викликається автоматично за meta.entry
```

## Паралельні виклики (parallel)
- Блок `parallel { ... }` запускає виклики функцій/методів у паралельних потоках.
- Всередині блоку виконуються лише виклики (наприклад `ns.func()` або `obj.method()`).
- Потоки є «daemon» і не блокують завершення головної програми.

```aml
import_py { console, base }

namespace app {
  func worker(n) {
    console.print_line("WORKER " + n)
    base.sleep_ms(300)
  }
  func main() {
    console.print_line("MAIN START")
    // необов’язково: невелика пауза, щоб побачити вивід воркерів
    base.sleep_ms(500)
  }
}

parallel {
  app.worker(n=1)
  app.worker(n=2)
}

// Можна задати точку входу через meta
meta { entry: "app.main" }
```

Примітки:
- Якщо головна програма завершується дуже швидко, паралельні потоки можуть не встигнути вивести все. Додайте коротку паузу або використайте майбутню синхронізацію.
- Значення в `meta { ... }` можуть бути виразами, не лише рядками.
- Виклики Python-функцій підтримують keyword-аргументи: `numpy.array([1,2,3], dtype=numpy.float32)`.
- AML-функції також підтримують keyword-аргументи з прив’язкою до імен параметрів.