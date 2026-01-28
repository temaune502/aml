# Console module for AML language
# Contains functions for console input/output

def print_line(*args):
    """
    Print a message to the console with a newline
    """
    print(" ".join(args))

def print_no_newline(message=""):
    """
    Print a message to the console without a newline
    """
    print(message, end="")

def input_text(prompt=""):
    """
    Get input from the user with an optional prompt
    """
    return input(prompt)

def input_number(prompt=""):
    """
    Get numeric input from the user with an optional prompt
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

def clear_screen():
    """
    Clear the console screen
    """
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored(message, color="white"):
    """
    Print colored text to the console
    Available colors: black, red, green, yellow, blue, magenta, cyan, white
    """
    colors = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m"
    }
    
    color_code = colors.get(color.lower(), colors["white"])
    print(f"{color_code}{message}{colors['reset']}")