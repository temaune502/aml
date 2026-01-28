import os
import subprocess
import shutil

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
def execute(command, timeout=None, cwd=None):
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