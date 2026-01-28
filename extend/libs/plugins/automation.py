# Enhanced automation plugin for AML
# Includes smooth mouse movements, hotkeys, and other useful functions.

import time
import math

# Import curves module for advanced trajectory patterns
try:
    from . import curves
except ImportError:
    curves = None

try:
    from pynput import keyboard as pynput_keyboard
    from pynput.keyboard import Controller, Key
    from pynput import mouse as pynput_mouse
    from pynput.mouse import Controller as MouseController, Button as MouseButton
    _controller = Controller()
    _mouse_controller = MouseController()
except Exception as e:
    print("pynput is not installed. Install with 'pip install pynput'")
    pynput_keyboard = None
    _controller = None
    Key = None
    pynput_mouse = None
    _mouse_controller = None
    MouseButton = None
    MouseController = None

# --- Mouse Functions ---

def get_screen_size():
    """Returns the screen size as a (width, height) tuple."""
    # Try platform-specific ways to get screen size. Prefer Windows API when available.
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        width = int(user32.GetSystemMetrics(0))
        height = int(user32.GetSystemMetrics(1))
        return (width, height)
    except Exception:
        # Fallback: if pynput mouse controller is available, try to use its position
        try:
            if _mouse_controller is not None:
                x, y = _mouse_controller.position
                return (int(x), int(y))
        except Exception:
            pass
    return (0, 0)


def tuple_to_list(obj):
    """Convert a tuple (possibly nested) into a regular list.

    - If obj is a tuple, returns a list with all elements converted recursively.
    - If obj is a list or set, converts contained tuples recursively and returns a list.
    - Otherwise returns obj unchanged.
    """
    if isinstance(obj, tuple):
        return [tuple_to_list(i) for i in obj]
    if isinstance(obj, set):
        # sets are unordered; convert to list
        return [tuple_to_list(i) for i in obj]
    if isinstance(obj, list):
        return [tuple_to_list(i) for i in obj]
    return obj


def get_mouse_position():
    """Returns the current mouse position as an (x, y) tuple."""
    if _mouse_controller is not None:
        try:
            pos = _mouse_controller.position
            return (int(pos[0]), int(pos[1]))
        except Exception:
            return (0, 0)
    return (0, 0)

def move_mouse_smooth(x, y, duration=0.5, steps=20):
    """
    Moves the mouse to an absolute position (x, y) with a smooth, human-like motion.
    - duration: total time for the movement in seconds.
    - steps: number of intermediate steps.
    """
    if _mouse_controller is None:
        print("Mouse controller is not available (pynput missing).")
        return

    try:
        sx, sy = _mouse_controller.position
        start_x, start_y = int(sx), int(sy)
    except Exception:
        start_x, start_y = 0, 0
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

        try:
            _mouse_controller.position = (int(next_x), int(next_y))
        except Exception:
            # Fallback: use move (relative) if absolute fails
            _mouse_controller.move(int(next_x) - start_x, int(next_y) - start_y)
        time.sleep(step_duration)

def move_mouse_relative_smooth(dx, dy, duration=0.5, steps=20):
    """
    Moves the mouse relative to its current position by (dx, dy) with a smooth motion.
    """
    if _mouse_controller is None:
        print("Mouse controller is not available (pynput missing).")
        return

    sx, sy = get_mouse_position()
    target_x = sx + dx
    target_y = sy + dy
    move_mouse_smooth(target_x, target_y, duration, steps)

def drag_smooth(x, y, duration=0.5, button='left'):
    """
    Drags the mouse to (x, y) smoothly.
    """
    if _mouse_controller is None or MouseButton is None:
        print("Mouse controller is not available (pynput missing).")
        return
    btn = getattr(MouseButton, str(button), MouseButton.left)
    _mouse_controller.press(btn)
    move_mouse_smooth(x, y, duration)
    _mouse_controller.release(btn)

def scroll(clicks, direction='vertical'):
    """
    Scrolls the mouse wheel.
    - clicks: The number of "clicks" to scroll. Positive for up/right, negative for down/left.
    - direction: 'vertical' or 'horizontal'.
    """
    if _mouse_controller is None:
        print("Mouse controller is not available (pynput missing).")
        return

    if direction == 'vertical':
        # pynput mouse.scroll(dx, dy): dx horizontal, dy vertical
        _mouse_controller.scroll(0, int(clicks))
    elif direction == 'horizontal':
        _mouse_controller.scroll(int(clicks), 0)
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
        print("Screen size is not available or unknown.")
        return
    x = int(float(rx) * size[0])
    y = int(float(ry) * size[1])
    move_mouse_smooth(x, y, duration, steps)

def move_mouse_path(points, per_segment_duration=0.4, steps_per_segment=20):
    """
    Move smoothly along a list of points [(x1,y1), (x2,y2), ...].
    """
    if _mouse_controller is None:
        print("Mouse controller is not available (pynput missing).")
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
    if _mouse_controller is None:
        print("Mouse controller is not available (pynput missing).")
        return
    sx, sy = get_mouse_position()
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
        try:
            _mouse_controller.position = (int(nx), int(ny))
        except Exception:
            _mouse_controller.move(int(nx) - sx, int(ny) - sy)
        time.sleep(step_duration)

def mouse_down(button='left'):
    if _mouse_controller is None or MouseButton is None:
        print("Mouse controller is not available (pynput missing).")
        return
    btn = getattr(MouseButton, str(button), MouseButton.left)
    _mouse_controller.press(btn)

def mouse_up(button='left'):
    if _mouse_controller is None or MouseButton is None:
        print("Mouse controller is not available (pynput missing).")
        return
    btn = getattr(MouseButton, str(button), MouseButton.left)
    _mouse_controller.release(btn)

def click(button='left', x=None, y=None, count=1, interval=0.05, smooth=False, duration=0.2, steps=15):
    """Convenience click with optional smooth move to (x,y) before clicking."""
    if _mouse_controller is None or MouseButton is None:
        print("Mouse controller is not available (pynput missing).")
        return
    btn = getattr(MouseButton, str(button), MouseButton.left)
    if smooth and x is not None and y is not None:
        move_mouse_smooth(x, y, duration, steps)
    for _ in range(int(count)):
        if x is not None and y is not None:
            try:
                _mouse_controller.position = (int(x), int(y))
            except Exception:
                pass
        _mouse_controller.press(btn)
        _mouse_controller.release(btn)
        time.sleep(interval)

def double_click(x=None, y=None, button='left', smooth=False, duration=0.2, steps=15):
    if _mouse_controller is None or MouseButton is None:
        print("Mouse controller is not available (pynput missing).")
        return
    if smooth and x is not None and y is not None:
        move_mouse_smooth(x, y, duration, steps)
    btn = getattr(MouseButton, str(button), MouseButton.left)
    if x is not None and y is not None:
        try:
            _mouse_controller.position = (int(x), int(y))
        except Exception:
            pass
    # two quick clicks
    _mouse_controller.press(btn)
    _mouse_controller.release(btn)
    time.sleep(0.05)
    _mouse_controller.press(btn)
    _mouse_controller.release(btn)

def right_click(x=None, y=None, smooth=False, duration=0.2, steps=15):
    if _mouse_controller is None or MouseButton is None:
        print("Mouse controller is not available (pynput missing).")
        return
    if smooth and x is not None and y is not None:
        move_mouse_smooth(x, y, duration, steps)
    btn = MouseButton.right
    if x is not None and y is not None:
        try:
            _mouse_controller.position = (int(x), int(y))
        except Exception:
            pass
    _mouse_controller.press(btn)
    _mouse_controller.release(btn)

def drag_to_smooth(x, y, duration=0.5, steps=20, button='left'):
    if _mouse_controller is None or MouseButton is None:
        print("Mouse controller is not available (pynput missing).")
        return
    mouse_down(button)
    move_mouse_smooth(x, y, duration, steps)
    mouse_up(button)

def drag_relative_smooth(dx, dy, duration=0.5, steps=20, button='left'):
    if _mouse_controller is None or MouseButton is None:
        print("Mouse controller is not available (pynput missing).")
        return
    sx, sy = get_mouse_position()
    drag_to_smooth(sx + dx, sy + dy, duration, steps, button)

def scroll_smooth(clicks, duration=0.5, steps=10, direction='vertical'):
    """Smooth scrolling by splitting into steps."""
    if _mouse_controller is None:
        print("Mouse controller is not available (pynput missing).")
        return
    if steps <= 0:
        steps = 1
    per = int(clicks / steps) if isinstance(clicks, int) else clicks / steps
    for i in range(steps):
        if direction == 'vertical':
            _mouse_controller.scroll(0, int(per))
        elif direction == 'horizontal':
            _mouse_controller.scroll(int(per), 0)
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


# --- Advanced Trajectory & Pattern Movement ---

def move_mouse_sine(start, end, amplitude=50, frequency=2, duration=0.5, button_hold=None):
    """
    Move mouse along a sine wave trajectory from start to end.
    - start, end: (x, y) tuples
    - amplitude: max deviation from straight line (pixels)
    - frequency: number of oscillations
    - duration: movement time (seconds)
    - button_hold: 'left', 'right', or None (for dragging while moving)
    """
    if curves is None or _mouse_controller is None:
        print("curves module or mouse controller not available.")
        return
    
    steps = max(20, int(duration * 100))
    path = curves.sine_wave(start, end, amplitude=amplitude, frequency=frequency, steps=steps)
    
    if button_hold:
        mouse_down(button_hold)
    
    step_duration = duration / len(path)
    for x, y in path:
        try:
            _mouse_controller.position = (int(x), int(y))
        except Exception:
            pass
        time.sleep(step_duration)
    
    if button_hold:
        mouse_up(button_hold)

def move_mouse_spiral(center, start_radius=10, end_radius=100, turns=2, duration=0.5):
    """
    Move mouse in a spiral pattern from center.
    - center: (x, y) tuple
    - start_radius, end_radius: starting/ending radius (pixels)
    - turns: number of rotations
    - duration: movement time (seconds)
    """
    if curves is None or _mouse_controller is None:
        print("curves module or mouse controller not available.")
        return
    
    steps = max(30, int(duration * 100))
    path = curves.spiral_path(center, start_radius=start_radius, end_radius=end_radius, turns=turns, steps=steps)
    
    step_duration = duration / len(path)
    for x, y in path:
        try:
            _mouse_controller.position = (int(x), int(y))
        except Exception:
            pass
        time.sleep(step_duration)

def move_mouse_circle(center, radius, steps_count=100, start_angle=0, end_angle=360, duration=0.5):
    """
    Move mouse in a circular arc.
    - center: (x, y) tuple
    - radius: circle radius (pixels)
    - steps_count: number of points along arc
    - start_angle, end_angle: arc bounds (degrees)
    - duration: movement time (seconds)
    """
    if curves is None or _mouse_controller is None:
        print("curves module or mouse controller not available.")
        return
    
    path = curves.circle_path(center, radius=radius, steps=steps_count, start_angle=start_angle, end_angle=end_angle)
    
    step_duration = duration / len(path) if path else 0.01
    for x, y in path:
        try:
            _mouse_controller.position = (int(x), int(y))
        except Exception:
            pass
        time.sleep(step_duration)

def move_mouse_zigzag(start, end, amplitude=30, zigzags=5, duration=0.5):
    """
    Move mouse in a zigzag pattern from start to end.
    - start, end: (x, y) tuples
    - amplitude: max deviation from line (pixels)
    - zigzags: number of zigzags
    - duration: movement time (seconds)
    """
    if curves is None or _mouse_controller is None:
        print("curves module or mouse controller not available.")
        return
    
    steps = max(40, int(duration * 100))
    path = curves.zigzag_path(start, end, amplitude=amplitude, zigzags=zigzags, steps=steps)
    
    step_duration = duration / len(path) if path else 0.01
    for x, y in path:
        try:
            _mouse_controller.position = (int(x), int(y))
        except Exception:
            pass
        time.sleep(step_duration)

def move_mouse_random_walk(start, end, step_size=10, duration=0.5):
    """
    Move mouse with random walk trajectory (natural, unpredictable movement).
    - start, end: (x, y) tuples
    - step_size: max movement per step (pixels)
    - duration: movement time (seconds)
    """
    if curves is None or _mouse_controller is None:
        print("curves module or mouse controller not available.")
        return
    
    # Generate random walk and adjust to end at target
    steps = max(30, int(duration * 100))
    path = curves.random_walk_path(start, step_size=step_size, steps=steps-1)
    path[-1] = end  # Ensure we end at target
    
    step_duration = duration / len(path) if path else 0.01
    for x, y in path:
        try:
            _mouse_controller.position = (int(x), int(y))
        except Exception:
            pass
        time.sleep(step_duration)

def move_mouse_noisy(start, end, sigma=20, duration=0.5):
    """
    Move mouse with Gaussian noise added (realistic human-like movement).
    - start, end: (x, y) tuples
    - sigma: noise standard deviation (pixels)
    - duration: movement time (seconds)
    """
    if curves is None or _mouse_controller is None:
        print("curves module or mouse controller not available.")
        return
    
    steps = max(50, int(duration * 100))
    path = curves.gaussian_noise_path(start, end, sigma=sigma, steps=steps)
    
    step_duration = duration / len(path) if path else 0.01
    for x, y in path:
        try:
            _mouse_controller.position = (int(x), int(y))
        except Exception:
            pass
        time.sleep(step_duration)

def move_mouse_interpolated(points, steps_per_segment=10, curve_type='catmull', duration=0.5):
    """
    Move mouse smoothly through a list of waypoints with smooth interpolation.
    - points: list of (x, y) tuples (waypoints)
    - steps_per_segment: interpolation steps between consecutive points
    - curve_type: 'linear', 'quadratic', 'cubic', 'catmull'
    - duration: total movement time (seconds)
    """
    if curves is None or _mouse_controller is None:
        print("curves module or mouse controller not available.")
        return
    
    path = curves.interpolate_path(points, steps_per_segment=steps_per_segment, curve_type=curve_type)
    
    step_duration = duration / len(path) if path else 0.01
    for x, y in path:
        try:
            _mouse_controller.position = (int(x), int(y))
        except Exception:
            pass
        time.sleep(step_duration)

def move_mouse_composite(start, end, pattern='sine', secondary_noise=5, duration=0.5):
    """
    Move mouse with composite pattern (primary + secondary noise for realism).
    - start, end: (x, y) tuples
    - pattern: 'sine', 'zigzag', 'random_walk', 'spiral'
    - secondary_noise: Gaussian noise sigma (0 = no noise)
    - duration: movement time (seconds)
    """
    if curves is None or _mouse_controller is None:
        print("curves module or mouse controller not available.")
        return
    
    steps = max(50, int(duration * 100))
    path = curves.composite_path(start, end, primary_pattern=pattern, secondary_noise=secondary_noise, steps=steps)
    
    step_duration = duration / len(path) if path else 0.01
    for x, y in path:
        try:
            _mouse_controller.position = (int(x), int(y))
        except Exception:
            pass
        time.sleep(step_duration)