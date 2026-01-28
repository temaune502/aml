"""
Keyboard plugin for AML language
Implements keyboard automation using 'pynput' instead of 'pyautogui'.
"""

try:
    from pynput import keyboard as pynput_keyboard
    from pynput.keyboard import Controller, Key
    _controller = Controller()
except Exception as e:
    print("pynput is not installed. Install with 'pip install pynput' ")
    pynput_keyboard = None
    _controller = None
    Key = None

SPECIAL_KEYS = {
    'enter': 'enter',
    'return': 'enter',
    'shift': 'shift',
    'ctrl': 'ctrl',
    'control': 'ctrl',
    'alt': 'alt',
    'tab': 'tab',
    'space': 'space',
    'esc': 'esc',
    'escape': 'esc',
    'backspace': 'backspace',
    'delete': 'delete',
    'home': 'home',
    'end': 'end',
    'pageup': 'page_up',
    'pagedown': 'page_down',
    'left': 'left',
    'right': 'right',
    'up': 'up',
    'down': 'down'
}

def _key_from_string(key_str):
    """
    Map string like 'a', 'enter', 'ctrl' to pynput Key/KeyCode
    """
    if _controller is None:
        return None
    if not isinstance(key_str, str):
        key_str = str(key_str)
    k = key_str.strip()
    lower = k.lower()
    if Key is None:
        return None
    if lower in SPECIAL_KEYS:
        attr = SPECIAL_KEYS[lower]
        return getattr(Key, attr)
    if len(k) == 1:
        # Single character
        return pynput_keyboard.KeyCode.from_char(k)
    # Try function keys like 'f1', 'f12'
    if lower.startswith('f') and lower[1:].isdigit():
        return getattr(Key, lower, pynput_keyboard.KeyCode.from_char(k))
    # Fallback: use first character
    return pynput_keyboard.KeyCode.from_char(k[0])

def press_key(key):
    """
    Press a key on the keyboard
    """
    if _controller is None:
        print("pynput is not available. Cannot press key.")
        return
    k = _key_from_string(key)
    if k is None:
        print(f"Unknown key: {key}")
        return
    _controller.press(k)
    _controller.release(k)

def hold_key(key):
    """
    Hold a key down
    """
    if _controller is None:
        print("pynput is not available. Cannot hold key.")
        return
    k = _key_from_string(key)
    if k is None:
        print(f"Unknown key: {key}")
        return
    _controller.press(k)

def release_key(key):
    """
    Release a key
    """
    if _controller is None:
        print("pynput is not available. Cannot release key.")
        return
    k = _key_from_string(key)
    if k is None:
        print(f"Unknown key: {key}")
        return
    _controller.release(k)

def type_text(text):
    """
    Type text
    """
    if _controller is None:
        print("pynput is not available. Cannot type text.")
        return
    _controller.type(str(text))

def hotkey(*keys):
    """
    Press a hotkey combination (e.g. ctrl+shift+a)
    """
    if _controller is None:
        print("pynput is not available. Cannot press hotkey.")
        return
    mapped = [_key_from_string(k) for k in keys]
    if any(k is None for k in mapped):
        print(f"Unknown key(s) in: {keys}")
        return
    # Hold all keys then release in reverse order
    for k in mapped:
        _controller.press(k)
    for k in reversed(mapped):
        _controller.release(k)

def input_key():
    """
    Wait for a key press and return the key as string
    """
    if pynput_keyboard is None:
        print("pynput is not available. Cannot input key.")
        return None
    pressed = {'val': None}
    def on_press(k):
        pressed['val'] = k
        return False  # stop listener
    with pynput_keyboard.Listener(on_press=on_press) as listener:
        listener.join()
    k = pressed['val']
    if isinstance(k, pynput_keyboard.KeyCode):
        return k.char
    elif isinstance(k, pynput_keyboard.Key):
        return str(k).replace('Key.', '')
    return str(k)
