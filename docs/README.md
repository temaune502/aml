# AML Docs

Ласкаво просимо до документації AML.

## Початок роботи

- Створіть `namespace` з функцією `main`.
- Використовуйте `console.print_line` для виводу.

```aml
namespace app {
  func main() {
    console.print_line("Hello")
  }
}
app.main()
```

## Імпорт Python

```aml
import_py{
  console
}
console.print_colored("Hello", "green")
```

## Нові можливості: meta та parallel

- `meta { ... }` — зберігає метадані файлу та дозволяє вказати точку входу через `entry`.
- `parallel { ... }` — запускає виклики функцій у паралельних потоках без блокування.

Швидкий приклад:

```aml
import_py { console, base }

meta { entry: "app.main", version: "1.0" }

namespace app {
  func worker() { console.print_line("WORKER") }
  func main() {
    parallel { app.worker() app.worker() }
    base.sleep_ms(300)
    console.print_line("MAIN DONE")
  }
}
```