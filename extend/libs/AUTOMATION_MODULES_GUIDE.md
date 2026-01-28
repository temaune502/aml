# 4 Модулі для Автоматизації Консолі та Системи

## 📋 Зміст

1. [Console Automation](#console-automation)
2. [PowerShell Executor](#powershell-executor)
3. [System Monitor](#system-monitor)
4. [Windows Automation](#windows-automation)

---

## Console Automation

**Файл**: `plugins/console_automation.py`

Модуль для запуску команд, обробки виводу та управління процесами.

### Основні класи

#### `CommandResult`
Результат виконання команди.

```python
result = run_cmd('echo "Hello"')
print(result.stdout)        # Стандартний вивід
print(result.stderr)        # Помилки
print(result.return_code)   # Код повернення
print(result.success)       # Успіх?
print(result.execution_time) # Час виконання
```

#### `ConsoleAutomation`
Основний клас для роботи з консоллю.

### Методи

#### `run_command()`
Запустити команду синхронно.

```python
automation = ConsoleAutomation()

# Базова команда
result = automation.run_command('dir')

# З timeout'ом
result = automation.run_command('python script.py', timeout=30)

# З PowerShell
result = automation.run_command(
    'Get-Process | ConvertTo-Json',
    shell='powershell'
)
```

#### `run_async()`
Запустити команду асинхронно.

```python
def on_output(line):
    print(f"OUT: {line}")

process = automation.run_async(
    'Get-Process',
    on_output=on_output,
    shell='powershell'
)
process.wait()
```

#### `parse_lines()`
Розділити вивід на рядки.

```python
result = automation.run_command('tasklist')
lines = automation.parse_lines(result)
for line in lines:
    print(line)
```

#### `parse_json_output()`
Спарсити JSON з виводу.

```python
result = automation.run_command('powershell "Get-Process | ConvertTo-Json"')
data = automation.parse_json_output(result)
```

#### `parse_table()`
Спарсити таблицю з виводу.

```python
result = automation.run_command('wmic process list brief')
rows = automation.parse_table(result)
for row in rows:
    print(row['Name'], row['ProcessId'])
```

#### `extract_regex()`
Витягнути значення за regex.

```python
result = automation.run_command('ipconfig')
ips = automation.extract_regex(result, r'\d+\.\d+\.\d+\.\d+')
```

### Утиліти функції

```python
# Швидкі функції
result = run_cmd('dir')                    # Запустити команду
result = run_powershell('Get-Process')     # PowerShell
result = run_python('print("Hello")')      # Python
```

---

## PowerShell Executor

**Файл**: `plugins/powershell_executor.py`

Спеціалізований модуль для PowerShell з підтримкою об'єктів та pipeline.

### Основні класи

#### `PSResult`
Результат PowerShell команди.

```python
result = ps_run('Get-Process | ConvertTo-Json')
print(result.objects)      # Спарсені об'єкти
print(result.success)      # Успіх?
print(result.execution_time) # Час виконання
```

#### `PowerShellExecutor`
Основний виконавець.

```python
executor = PowerShellExecutor()
result = executor.run('Get-Process', use_cache=True)
```

### Методи

#### `run()`
Запустити PowerShell команду.

```python
executor = PowerShellExecutor()
result = executor.run('Get-Process')
print(result.objects)  # Об'єкти (JSON)
```

#### `run_script_file()`
Запустити .ps1 файл.

```python
result = executor.run_script_file('script.ps1', parameters={'Name': 'cmd'})
```

#### `get_processes()`
Отримати список процесів.

```python
processes = executor.get_processes(name_filter='explorer')
for proc in processes:
    print(proc['Name'], proc['Id'])
```

#### `stop_process()`
Зупинити процес.

```python
result = executor.stop_process('notepad', force=True)
if result.success:
    print("Процес зупинено")
```

#### `pipeline()`
Запустити pipeline команди.

```python
result = executor.pipeline(
    'Get-Process',
    'Where-Object {$_.WorkingSet -gt 50MB}',
    'Sort-Object WorkingSet -Descending',
    'Select-Object -First 5 Name'
)
```

#### `get_files()`
Отримати список файлів.

```python
files = executor.get_files('C:\\Users', filter_expr='*.txt', recurse=True)
```

#### `registry_read()`
Прочитати з реєстру.

```python
value = executor.get_registry_value(
    'HKEY_CURRENT_USER\\Software\\Microsoft',
    'ValueName'
)
```

### Утиліти функції

```python
result = ps_run('Get-Process')              # Запустити
processes = ps_get_processes()              # Отримати процеси
ps_stop_process('notepad')                  # Зупинити
```

---

## System Monitor

**Файл**: `plugins/system_monitor.py`

Моніторинг системних ресурсів та процесів.

### Основні класи

#### `SystemMetrics`
Метрики системи.

```python
metrics = monitor.get_system_metrics()
print(metrics.cpu_percent)      # CPU %
print(metrics.memory_percent)   # RAM %
print(metrics.disk_percent)     # Disk %
```

#### `ProcessInfo`
Інформація про процес.

```python
processes = monitor.get_processes(sort_by='memory_percent', limit=10)
for proc in processes:
    print(f"{proc.name}: {proc.memory_percent}%")
```

#### `SystemMonitor`
Основний монітор.

```python
monitor = SystemMonitor(alert_threshold={
    'cpu': 80,
    'memory': 85,
    'disk': 90
})
```

### Методи

#### `get_cpu_info()`
Інформація про CPU.

```python
cpu = monitor.get_cpu_info()
print(cpu['percent'])              # Поточний CPU %
print(cpu['percent_per_core'])     # CPU % для кожного ядра
print(cpu['frequency_current'])    # Поточна частота
```

#### `get_memory_info()`
Інформація про пам'ять.

```python
mem = monitor.get_memory_info()
print(mem['total'])      # Всього
print(mem['available'])  # Доступна
print(mem['percent'])    # Відсоток використання
```

#### `get_disk_info()`
Інформація про диск.

```python
disk = monitor.get_disk_info('C:\\')
print(disk['total'])     # Всього
print(disk['used'])      # Використано
print(disk['percent'])   # Відсоток
```

#### `get_network_info()`
Інформація про мережу.

```python
net = monitor.get_network_info()
for iface, info in net['interfaces'].items():
    print(f"{iface}: {info['is_up']}")
```

#### `get_processes()`
Отримати топ процесів.

```python
# За пам'яттю
procs = monitor.get_processes(sort_by='memory_percent', limit=10)

# За CPU
procs = monitor.get_processes(sort_by='cpu_percent', limit=5)
```

#### `find_process()`
Знайти процес по імені.

```python
proc = monitor.find_process('explorer.exe')
if proc:
    print(f"{proc.name}: {proc.pid}")
```

#### `kill_process()`
Завершити процес.

```python
success = monitor.kill_process(1234)
```

#### `monitor_continuous()`
Безперервний моніторинг.

```python
def on_metric(metrics):
    print(metrics)

def on_alert(alert):
    print(f"ALERT: {alert['message']}")

monitor.monitor_continuous(
    interval=5,         # Кожні 5 секунд
    duration=60,        # Протягом 60 секунд
    on_metric=on_metric,
    on_alert=on_alert
)
```

### Утиліти функції

```python
metrics = get_system_metrics()          # Отримати метрики
procs = get_top_processes(limit=10)    # Топ процесів
kill_process_by_name('notepad')        # Завершити по імені
```

---

## Windows Automation

**Файл**: `plugins/windows_automation.py`

Автоматизація Windows-специфічних операцій.

### Основні методи

#### Управління сервісами

```python
from plugins.windows_automation import WindowsAutomation

# Отримати список сервісів
services = WindowsAutomation.get_services(name_filter='Windows')

# Отримати статус
status = WindowsAutomation.get_service_status('wuauserv')

# Запустити/Зупинити
WindowsAutomation.start_service('wuauserv')
WindowsAutomation.stop_service('wuauserv')

# Перезапустити
WindowsAutomation.restart_service('wuauserv')
```

#### Робота з реєстром

```python
# Прочитати значення
value = WindowsAutomation.registry_read(
    'HKEY_LOCAL_MACHINE\\Software\\Microsoft',
    'ValueName'
)

# Записати значення
WindowsAutomation.registry_write(
    'HKEY_CURRENT_USER\\Software\\MyApp',
    'Setting',
    'Value'
)

# Видалити значення
WindowsAutomation.registry_delete(
    'HKEY_CURRENT_USER\\Software\\MyApp',
    'Setting'
)
```

#### Task Scheduler

```python
# Створити завдання
WindowsAutomation.create_task(
    name='MyTask',
    trigger='OnStartup',
    action='echo "Hello"'
)

# Отримати список завдань
tasks = WindowsAutomation.get_tasks()

# Видалити завдання
WindowsAutomation.delete_task('MyTask')
```

#### Інформація про систему

```python
# Інформація про комп'ютер
sys_info = WindowsAutomation.get_system_info()

# Інформація про Windows
win_info = WindowsAutomation.get_windows_info()

# Список вікон
windows = WindowsAutomation.get_windows()
```

#### Контроль живлення

```python
# Вимкнути
WindowsAutomation.shutdown()

# Перезавантажити
WindowsAutomation.restart()

# Сон
WindowsAutomation.sleep()
```

---

## Приклади використання

Див. файл `examples_automation.py` для 14 практичних прикладів.

### Швидкий старт

```python
# Console Automation
from plugins.console_automation import run_cmd, run_powershell

result = run_powershell('Get-Process explorer')
print(result.stdout)

# PowerShell Executor
from plugins.powershell_executor import ps_run, ps_get_processes

processes = ps_get_processes()
for proc in processes[:5]:
    print(proc)

# System Monitor
from plugins.system_monitor import get_system_metrics, get_top_processes

metrics = get_system_metrics()
print(metrics)

top = get_top_processes(limit=5)
for proc in top:
    print(f"{proc.name}: {proc.memory_percent}%")

# Windows Automation
from plugins.windows_automation import WindowsAutomation

sys_info = WindowsAutomation.get_system_info()
print(sys_info)
```

---

## Залежності

```bash
pip install psutil
```

Для повної функціональності Windows Automation:
```bash
pip install pygetwindow  # Опціонально для роботи з вікнами
```

---

## Ліцензія

Всі модулі під ліцензією MIT. Вільне використання в будь-яких проектах.
