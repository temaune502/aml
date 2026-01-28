import os
import shutil

def read_file(path):
    """Прочитати вміст файлу як рядок."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Error reading file '{path}': {str(e)}")

def write_file(path, content):
    """Записати рядок у файл (перезапис)."""
    try:
        # Створити директорію, якщо її нема
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise RuntimeError(f"Error writing to file '{path}': {str(e)}")

def append_file(path, content):
    """Дописати рядок у кінець файлу."""
    try:
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise RuntimeError(f"Error appending to file '{path}': {str(e)}")

def read_lines(path):
    """Прочитати файл як список рядків."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    except Exception as e:
        raise RuntimeError(f"Error reading lines from '{path}': {str(e)}")

def write_lines(path, lines):
    """Записати список рядків у файл."""
    try:
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(str(line) + "\n")
    except Exception as e:
        raise RuntimeError(f"Error writing lines to '{path}': {str(e)}")

def file_exists(path):
    """Перевірити існування файлу або директорії."""
    return os.path.exists(path)

def is_file(path):
    """Чи є шлях файлом."""
    return os.path.isfile(path)

def dir_exists(path):
    """Чи є шлях директорією."""
    return os.path.isdir(path)

def make_dir(path):
    """Створити директорію (включно з батьківськими)."""
    try:
        os.makedirs(path, exist_ok=True)
        return path
    except Exception as e:
        raise RuntimeError(f"Error creating directory '{path}': {str(e)}")

def remove_dir(path, recursive=True):
    """Видалити директорію. Якщо recursive=True — з вмістом."""
    try:
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)
        return True
    except Exception as e:
        raise RuntimeError(f"Error removing directory '{path}': {str(e)}")

def list_dir(path):
    """Отримати список файлів/папок у директорії."""
    try:
        return os.listdir(path)
    except Exception as e:
        raise RuntimeError(f"Error listing directory '{path}': {str(e)}")

def delete_file(path):
    """Видалити файл."""
    try:
        os.remove(path)
        return True
    except Exception as e:
        raise RuntimeError(f"Error deleting file '{path}': {str(e)}")

def copy_file(src, dst):
    """Копіювати файл з атрибутами."""
    try:
        dir_path = os.path.dirname(dst)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        shutil.copy2(src, dst)
        return dst
    except Exception as e:
        raise RuntimeError(f"Error copying file '{src}' to '{dst}': {str(e)}")

def move_file(src, dst):
    """Перемістити/перейменувати файл або директорію."""
    try:
        dir_path = os.path.dirname(dst)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        return shutil.move(src, dst)
    except Exception as e:
        raise RuntimeError(f"Error moving '{src}' to '{dst}': {str(e)}")

def get_cwd():
    """Поточна робоча директорія."""
    return os.getcwd()

def change_dir(path):
    """Змінити поточну робочу директорію."""
    try:
        os.chdir(path)
        return os.getcwd()
    except Exception as e:
        raise RuntimeError(f"Error changing directory to '{path}': {str(e)}")

def path_join(a, b):
    """Об’єднати шлях a і b."""
    return os.path.join(a, b)

def get_basename(path):
    """Повертає базове ім'я файлу."""
    return os.path.basename(path)

def get_dirname(path):
    """Повертає ім'я директорії файлу."""
    return os.path.dirname(path)

def get_extname(path):
    """Повертає розширення файлу (включно з крапкою)."""
    return os.path.splitext(path)[1]

def get_abspath(path):
    """Повертає абсолютний шлях."""
    return os.path.abspath(path)

def file_size(path):
    """Розмір файлу в байтах."""
    try:
        return os.path.getsize(path)
    except Exception as e:
        raise RuntimeError(f"Error getting size for '{path}': {str(e)}")