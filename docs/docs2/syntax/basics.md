# Синтаксис мови AML

AML (Automation Markup Language) — це потужна скриптова мова, розроблена для автоматизації завдань, маніпуляції даними та взаємодії з системними компонентами.

## 1. Типи даних

- **Числа (Number):** Цілі та дробові числа.
  ```aml
  var age = 25
  var price = 19.99
  ```
- **Рядки (String):** Текстові дані у подвійних лапках.
  ```aml
  var name = "AML User"
  ```
- **Логічні значення (Boolean):** `true` або `false`.
  ```aml
  var isActive = true
  ```
- **Null:** Відсутність значення.
  ```aml
  var data = null
  ```
- **Списки (List):** Впорядковані колекції.
  ```aml
  var fruits = ["apple", "banana", "cherry"]
  ```
- **Словники (Dictionary):** Колекції пар ключ-значення.
  ```aml
  var user = {"name": "Ivan", "age": 30}
  ```

## 2. Змінні

Змінні оголошуються за допомогою ключового слова `var`.

```aml
var x = 10
x = 20 // Переприсвоєння
```

## 3. Керуючі конструкції

### Умовні оператори
```aml
if (x > 10) {
    print("Більше за 10")
} else if (x == 10) {
    print("Дорівнює 10")
} else {
    print("Менше за 10")
}
```

### Цикли
**Цикл while:**
```aml
var i = 0
while (i < 5) {
    print(i)
    i = i + 1
}
```

**Цикл for:**
```aml
for (item in ["a", "b", "c"]) {
    print(item)
}
```

## 4. Функції

Оголошуються ключовим словом `func`. Підтримують аргументи за замовчуванням.

```aml
func greet(name, prefix="Hello") {
    return prefix + ", " + name + "!"
}

print(greet("AML")) // Hello, AML!
```

## 5. Comprehensions (Спискові та словникові вирази)

AML підтримує компактний синтаксис для створення колекцій.

### List Comprehensions
```aml
var numbers = [1, 2, 3, 4, 5, 6]
var squares = [x * x for x in numbers if x % 2 == 0]
// Результат: [4, 16, 36]
```

### Dict Comprehensions
```aml
var words = ["apple", "bat", "cherry"]
var lengths = {w: len(w) for w in words}
// Результат: {"apple": 5, "bat": 3, "cherry": 6}
```

## 6. Робота з модулями

Модулі можна імпортувати за допомогою `import`.

```aml
var math = import("temaune/math/core")
print(math.sqrt(16))
```

Також можна імпортувати Python-плагіни:
```aml
import_py { plugins\system as sys }
sys.sleep(1000)
```
