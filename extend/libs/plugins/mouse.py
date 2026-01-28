# Mouse plugin for AML language
# Contains functions for mouse automation

try:
    import pyautogui
except ImportError:
    print("PyAutoGUI is not installed. Please install it using 'pip install pyautogui'")
    pyautogui = None

def move_mouse(x, y):
    """
    Move mouse to specified coordinates
    """
    if pyautogui:
        pyautogui.moveTo(x, y)
    else:
        print("PyAutoGUI is not available. Cannot move mouse.")

def move_to(x, y):
    """
    Move mouse to specified coordinates
    """
    if pyautogui:
        pyautogui.moveTo(x, y)
    else:
        print("PyAutoGUI is not available. Cannot move mouse.")


def click_mouse(x=None, y=None, button='left'):
    """
    Click mouse at current position or specified coordinates
    """
    if pyautogui:
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button)
        else:
            pyautogui.click(button=button)
    else:
        print("PyAutoGUI is not available. Cannot click mouse.")

def double_click(x=None, y=None, button='left'):
    """
    Double click mouse at current position or specified coordinates
    """
    if pyautogui:
        if x is not None and y is not None:
            pyautogui.doubleClick(x, y, button=button)
        else:
            pyautogui.doubleClick(button=button)
    else:
        print("PyAutoGUI is not available. Cannot double click mouse.")

def right_click(x=None, y=None):
    """
    Right click mouse at current position or specified coordinates
    """
    if pyautogui:
        if x is not None and y is not None:
            pyautogui.rightClick(x, y)
        else:
            pyautogui.rightClick()
    else:
        print("PyAutoGUI is not available. Cannot right click mouse.")

def get_mouse_position():
    """
    Get current mouse position
    """
    if pyautogui:
        return pyautogui.position()
    else:
        print("PyAutoGUI is not available. Cannot get mouse position.")
        return (0, 0)
class MouseController:
    def __init__(self):
        pass
    def move(self, x, y):
        move_mouse(x, y)