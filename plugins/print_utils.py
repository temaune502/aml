"""
Модуль для роботи з консоллю в AML.
"""
import os
import sys

def log(*args, sep=' ', end='\n'):
    """Вивести одне або кілька значень у консоль."""
    print(*args, sep=sep, end=end)
    sys.stdout.flush()

def print_line(*args):
    """Вивести рядок у консоль (аліас для log)."""
    log(*args)

def print_text(*args):
    """Вивести текст без переходу на новий рядок."""
    log(*args, end='')

def read(prompt=""):
    """Зчитати рядок тексту з консолі."""
    try:
        return input(prompt)
    except EOFError:
        return ""

def clear():
    """Очистити екран консолі."""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def set_title(title):
    """Встановити заголовок вікна консолі."""
    if os.name == 'nt':
        os.system(f'title {title}')
    else:
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()

def color_log(text, color="white"):
    """
    Вивести кольоровий текст у консоль.
    Підтримувані кольори: red, green, yellow, blue, magenta, cyan, white.
    """
    colors = {
        "red": "31",
        "green": "32",
        "yellow": "33",
        "blue": "34",
        "magenta": "35",
        "cyan": "36",
        "white": "37"
    }
    code = colors.get(color.lower(), "37")
    print(f"\033[{code}m{text}\033[0m")
    sys.stdout.flush()
