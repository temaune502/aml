# Enhanced automation plugin for AML
# Includes smooth mouse movements, hotkeys, and other useful functions.

import time
import math

try:
    import pyautogui
except ImportError:
    print("PyAutoGUI is not installed. Please install it using 'pip install pyautogui'")
    pyautogui = None

try:
    from pynput import keyboard as pynput_keyboard
    from pynput.keyboard import Controller, Key
    _controller = Controller()
except Exception as e:
    print("pynput is not installed. Install with 'pip install pynput'")
    pynput_keyboard = None
    _controller = None
    Key = None

# --- Mouse Functions ---

def get_screen_size():
    """Returns the screen size as a (width, height) tuple."""
    if pyautogui:
        return pyautogui.size()
    return (None, None)

def get_mouse_position():
    """Returns the current mouse position as an (x, y) tuple."""
    if pyautogui:
        return pyautogui.position()
    return (0, 0)

def move_mouse_smooth(x, y, duration=0.5, steps=20):
    """
    Moves the mouse to an absolute position (x, y) with a smooth, human-like motion.
    - duration: total time for the movement in seconds.
    - steps: number of intermediate steps.
    """
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return

    start_x, start_y = pyautogui.position()
    dx = x - start_x
    dy = y - start_y

    if dx == 0 and dy == 0:
        return

    step_duration = duration / steps

    for i in range(1, steps + 1):
        progress = i / steps
        # Ease-out curve for more natural movement
        ease_progress = 1 - (1 - progress)**3

        next_x = start_x + dx * ease_progress
        next_y = start_y + dy * ease_progress

        pyautogui.moveTo(next_x, next_y)
        time.sleep(step_duration)

def move_mouse_relative_smooth(dx, dy, duration=0.5, steps=20):
    """
    Moves the mouse relative to its current position by (dx, dy) with a smooth motion.
    """
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return

    start_x, start_y = pyautogui.position()
    target_x = start_x + dx
    target_y = start_y + dy
    move_mouse_smooth(target_x, target_y, duration, steps)

def drag_smooth(x, y, duration=0.5, button='left'):
    """
    Drags the mouse to (x, y) smoothly.
    """
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return
    pyautogui.dragTo(x, y, duration=duration, button=button)

def scroll(clicks, direction='vertical'):
    """
    Scrolls the mouse wheel.
    - clicks: The number of "clicks" to scroll. Positive for up/right, negative for down/left.
    - direction: 'vertical' or 'horizontal'.
    """
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return

    if direction == 'vertical':
        pyautogui.scroll(clicks)
    elif direction == 'horizontal':
        pyautogui.hscroll(clicks)
    else:
        print(f"Unknown scroll direction: {direction}")

# --- Keyboard Functions ---
# Re-using logic from plugins/keyboard.py for consistency.

SPECIAL_KEYS = {
    'enter': 'enter', 'return': 'enter', 'shift': 'shift', 'ctrl': 'ctrl',
    'control': 'ctrl', 'alt': 'alt', 'tab': 'tab', 'space': 'space',
    'esc': 'esc', 'escape': 'esc', 'backspace': 'backspace', 'delete': 'delete',
    'home': 'home', 'end': 'end', 'pageup': 'page_up', 'pagedown': 'page_down',
    'left': 'left', 'right': 'right', 'up': 'up', 'down': 'down'
}

def _key_from_string(key_str):
    """Maps a string like 'a', 'enter', 'ctrl' to a pynput Key/KeyCode."""
    if not _controller: return None
    if not isinstance(key_str, str): key_str = str(key_str)

    k = key_str.strip()
    lower = k.lower()

    if not Key: return None

    if lower in SPECIAL_KEYS:
        return getattr(Key, SPECIAL_KEYS[lower])

    if len(k) == 1:
        return pynput_keyboard.KeyCode.from_char(k)

    if lower.startswith('f') and lower[1:].isdigit():
        return getattr(Key, lower, pynput_keyboard.KeyCode.from_char(k))

    return pynput_keyboard.KeyCode.from_char(k[0])

def hotkey(*keys):
    """
    Presses a hotkey combination (e.g., 'ctrl', 'shift', 'a').
    Holds keys down and releases them in reverse order.
    """
    if not _controller:
        print("pynput is not available. Cannot press hotkey.")
        return

    mapped_keys = [_key_from_string(k) for k in keys]

    if any(k is None for k in mapped_keys):
        print(f"Unknown key(s) in hotkey combination: {keys}")
        return

    for k in mapped_keys:
        _controller.press(k)

    for k in reversed(mapped_keys):
        _controller.release(k)

def type_text(text, interval=0.01):
    """Types the given text with a small delay between keystrokes."""
    if not _controller:
        print("pynput is not available. Cannot type text.")
        return

    for char in str(text):
        _controller.press(char)
        _controller.release(char)
        time.sleep(interval)

# --- Extended Mouse Helpers ---

def clamp_to_screen(x, y):
    """Clamp coordinates to the screen bounds."""
    size = get_screen_size()
    if not size or size[0] is None:
        return (x, y)
    w, h = size
    cx = max(0, min(int(x), int(w) - 1))
    cy = max(0, min(int(y), int(h) - 1))
    return (cx, cy)

def move_mouse_to_ratio(rx, ry, duration=0.5, steps=20):
    """Move smoothly to a position given as ratio of screen size (0..1)."""
    size = get_screen_size()
    if not size or size[0] is None:
        print("PyAutoGUI is not available or screen size unknown.")
        return
    x = int(float(rx) * size[0])
    y = int(float(ry) * size[1])
    move_mouse_smooth(x, y, duration, steps)

def move_mouse_path(points, per_segment_duration=0.4, steps_per_segment=20):
    """
    Move smoothly along a list of points [(x1,y1), (x2,y2), ...].
    """
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return
    for (x, y) in points:
        x, y = clamp_to_screen(x, y)
        move_mouse_smooth(x, y, per_segment_duration, steps_per_segment)

def move_mouse_bezier_to(x, y, duration=0.8, steps=40, c1=None, c2=None, jitter=0):
    """
    Move cursor along a cubic Bezier curve from current position to (x,y).
    Optional control points c1, c2; if omitted, they are auto-generated.
    'jitter' adds random offset (px) to control points for human-like motion.
    """
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return
    sx, sy = pyautogui.position()
    ex, ey = x, y

    dx = ex - sx
    dy = ey - sy

    # Auto control points roughly along the path
    if c1 is None:
        c1 = (sx + 0.3 * dx, sy + 0.3 * dy)
    if c2 is None:
        c2 = (sx + 0.7 * dx, sy + 0.7 * dy)

    if jitter and jitter > 0:
        import random
        c1 = (c1[0] + random.uniform(-jitter, jitter), c1[1] + random.uniform(-jitter, jitter))
        c2 = (c2[0] + random.uniform(-jitter, jitter), c2[1] + random.uniform(-jitter, jitter))

    def bezier(p0, p1, p2, p3, t):
        # Cubic Bezier interpolation
        u = 1 - t
        return (
            u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
        )

    step_duration = duration / steps
    for i in range(1, steps + 1):
        t = i / steps
        nx, ny = bezier((sx, sy), c1, c2, (ex, ey), t)
        nx, ny = clamp_to_screen(nx, ny)
        pyautogui.moveTo(nx, ny)
        time.sleep(step_duration)

def mouse_down(button='left'):
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return
    pyautogui.mouseDown(button=button)

def mouse_up(button='left'):
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return
    pyautogui.mouseUp(button=button)

def click(button='left', x=None, y=None, count=1, interval=0.05, smooth=False, duration=0.2, steps=15):
    """Convenience click with optional smooth move to (x,y) before clicking."""
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return
    if smooth and x is not None and y is not None:
        move_mouse_smooth(x, y, duration, steps)
    for _ in range(int(count)):
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, button=button)
        else:
            pyautogui.click(button=button)
        time.sleep(interval)

def double_click(x=None, y=None, button='left', smooth=False, duration=0.2, steps=15):
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return
    if smooth and x is not None and y is not None:
        move_mouse_smooth(x, y, duration, steps)
    if x is not None and y is not None:
        pyautogui.doubleClick(x=x, y=y, button=button)
    else:
        pyautogui.doubleClick(button=button)

def right_click(x=None, y=None, smooth=False, duration=0.2, steps=15):
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return
    if smooth and x is not None and y is not None:
        move_mouse_smooth(x, y, duration, steps)
    if x is not None and y is not None:
        pyautogui.rightClick(x=x, y=y)
    else:
        pyautogui.rightClick()

def drag_to_smooth(x, y, duration=0.5, steps=20, button='left'):
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return
    mouse_down(button)
    move_mouse_smooth(x, y, duration, steps)
    mouse_up(button)

def drag_relative_smooth(dx, dy, duration=0.5, steps=20, button='left'):
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return
    sx, sy = get_mouse_position()
    drag_to_smooth(sx + dx, sy + dy, duration, steps, button)

def scroll_smooth(clicks, duration=0.5, steps=10, direction='vertical'):
    """Smooth scrolling by splitting into steps."""
    if not pyautogui:
        print("PyAutoGUI is not available.")
        return
    if steps <= 0:
        steps = 1
    per = int(clicks / steps) if isinstance(clicks, int) else clicks / steps
    for i in range(steps):
        if direction == 'vertical':
            pyautogui.scroll(per)
        elif direction == 'horizontal':
            pyautogui.hscroll(per)
        else:
            print(f"Unknown scroll direction: {direction}")
            break
        time.sleep(duration / steps)

# --- Extended Keyboard Helpers ---

def press_key(key):
    if not _controller:
        print("pynput is not available. Cannot press key.")
        return
    k = _key_from_string(key)
    if k is None:
        print(f"Unknown key: {key}")
        return
    _controller.press(k)
    _controller.release(k)

def hold_key(key):
    if not _controller:
        print("pynput is not available. Cannot hold key.")
        return
    k = _key_from_string(key)
    if k is None:
        print(f"Unknown key: {key}")
        return
    _controller.press(k)

def release_key(key):
    if not _controller:
        print("pynput is not available. Cannot release key.")
        return
    k = _key_from_string(key)
    if k is None:
        print(f"Unknown key: {key}")
        return
    _controller.release(k)

def type_text_human(text, min_interval=0.01, max_interval=0.05):
    """Type text with variable delays to simulate human typing."""
    if not _controller:
        print("pynput is not available. Cannot type text.")
        return
    import random
    for char in str(text):
        _controller.press(char)
        _controller.release(char)
        time.sleep(random.uniform(min_interval, max_interval))

def hotkey_sequence(sequences, interval=0.1):
    """Execute multiple hotkey combinations in order: [['ctrl','c'], ['ctrl','v']]."""
    if not isinstance(sequences, list):
        print("hotkey_sequence expects a list of key lists")
        return
    for seq in sequences:
        if not isinstance(seq, (list, tuple)):
            print(f"Invalid sequence: {seq}")
            continue
        hotkey(*seq)
        time.sleep(interval)

def wait_for_key(target_key=None, timeout=None):
    """
    Wait for a key press. If target_key is provided, waits until that key is pressed.
    Returns the pressed key string or None on timeout.
    """
    if pynput_keyboard is None:
        print("pynput is not available. Cannot wait for key.")
        return None
    pressed = {'val': None}

    tk = None
    if target_key is not None:
        tk = str(target_key).lower()

    def on_press(k):
        val = None
        try:
            if isinstance(k, pynput_keyboard.KeyCode):
                val = k.char
            elif isinstance(k, pynput_keyboard.Key):
                val = str(k).replace('Key.', '')
            else:
                val = str(k)
        except Exception:
            val = str(k)
        pressed['val'] = val
        if tk is None or (val and val.lower() == tk):
            return False  # stop listener
        # continue listening
        return True

    listener = pynput_keyboard.Listener(on_press=on_press)
    listener.start()

    start = time.time()
    while listener.running:
        if pressed['val'] is not None and (tk is None or pressed['val'].lower() == tk):
            break
        if timeout is not None and (time.time() - start) > float(timeout):
            listener.stop()
            return None
        time.sleep(0.01)
    listener.stop()
    return pressed['val']