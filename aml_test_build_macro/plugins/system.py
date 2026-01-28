import os
import subprocess
import shutil
import time

def sleep(seconds):
    """Призупинити виконання на вказану кількість секунд."""
    time.sleep(float(seconds))

def run(command, timeout=None, cwd=None):
    """
    Виконати консольну команду й повернути словник {output, error, code}.
    На Windows запускається через PowerShell.
    """
    try:
        if os.name == 'nt':
            ps_cmd = [
                'powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                '-Command', command
            ]
            result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return {
            'output': result.stdout,
            'error': result.stderr,
            'code': result.returncode
        }
    except subprocess.TimeoutExpired as e:
        return {
            'output': e.stdout or '',
            'error': (e.stderr or '') + '\nTimed out',
            'code': -1
        }
    except Exception as e:
        raise RuntimeError(f"Error running command '{command}': {str(e)}")

def run_shell(command, timeout=None, cwd=None):
    """
    Виконати команду через системний shell (shell=True).
    Корисно для простих команд і пайпінгу.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return {
            'output': result.stdout,
            'error': result.stderr,
            'code': result.returncode
        }
    except subprocess.TimeoutExpired as e:
        return {
            'output': e.stdout or '',
            'error': (e.stderr or '') + '\nTimed out',
            'code': -1
        }
    except Exception as e:
        raise RuntimeError(f"Error running shell command '{command}': {str(e)}")

def run_cmd(command, timeout=None, cwd=None):
    """Виконати команду саме через CMD (Windows)."""
    if os.name != 'nt':
        return run_shell(command, timeout, cwd)
    
    cmd = ['cmd.exe', '/c', command]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return {
            'output': result.stdout,
            'error': result.stderr,
            'code': result.returncode
        }
    except Exception as e:
        raise RuntimeError(f"Error running cmd command: {str(e)}")

def run_ps(command, timeout=None, cwd=None):
    """Виконати команду саме через PowerShell (Windows)."""
    if os.name != 'nt':
        return run_shell(command, timeout, cwd)
        
    ps_cmd = [
        'powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-Command', command
    ]
    try:
        result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return {
            'output': result.stdout,
            'error': result.stderr,
            'code': result.returncode
        }
    except Exception as e:
        raise RuntimeError(f"Error running powershell command: {str(e)}")

def get_os_name():
    """Повернути назву операційної системи ('nt' або 'posix')."""
    return os.name

def env_get_all():
    """Отримати всі змінні середовища у вигляді словника."""
    return dict(os.environ)

def env_delete(name):
    """Видалити змінну середовища."""
    if name in os.environ:
        del os.environ[name]
        return True
    return False

def get_cwd():
    """Отримати поточну робочу директорію."""
    return os.getcwd()

def set_cwd(path):
    """Змінити поточну робочу директорію."""
    os.chdir(path)
    return os.getcwd()

def which(program):
    """Знайти шлях до виконуваного файлу у PATH (як 'which')."""
    return shutil.which(program)

def env_get(name):
    """Отримати значення змінної середовища."""
    return os.environ.get(name)

def env_set(name, value):
    """Встановити значення змінної середовища для поточного процесу."""
    os.environ[str(name)] = str(value)
    return True