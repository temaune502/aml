import ctypes
import time
import math
import random

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from pynput import keyboard as pynput_keyboard
    from pynput.keyboard import Controller, Key
    _controller = Controller()
except Exception:
    pynput_keyboard = None
    _controller = None
    Key = None

from .common import user32, gdi32, POINT, MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, \
                    MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP, MOUSEEVENTF_WHEEL

def get_screen_size():
    """Returns the screen size as a (width, height) tuple."""
    if pyautogui:
        return pyautogui.size()
    if user32:
        return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
    return (0, 0)

def get_mouse_pos():
    if not user32: return (0, 0)
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)

def set_mouse_pos(x, y):
    return user32.SetCursorPos(int(x), int(y)) if user32 else False

def clamp_to_screen(x, y):
    """Clamp coordinates to the screen bounds."""
    w, h = get_screen_size()
    if w == 0 or h == 0:
        return (x, y)
    cx = max(0, min(int(x), int(w) - 1))
    cy = max(0, min(int(y), int(h) - 1))
    return (cx, cy)

def mouse_move_to(x, y, smooth=False, duration=0.5, steps=20):
    if not smooth:
        return set_mouse_pos(x, y)
    
    start_x, start_y = get_mouse_pos()
    dx = x - start_x
    dy = y - start_y

    if dx == 0 and dy == 0:
        return True

    step_duration = duration / steps

    for i in range(1, steps + 1):
        progress = i / steps
        # Ease-out curve for more natural movement
        ease_progress = 1 - (1 - progress)**3

        next_x = start_x + dx * ease_progress
        next_y = start_y + dy * ease_progress

        set_mouse_pos(next_x, next_y)
        time.sleep(step_duration)
    return True

def move_mouse_relative_smooth(dx, dy, duration=0.5, steps=20):
    """Moves the mouse relative to its current position by (dx, dy) with a smooth motion."""
    start_x, start_y = get_mouse_pos()
    return mouse_move_to(start_x + dx, start_y + dy, smooth=True, duration=duration, steps=steps)

def move_mouse_to_ratio(rx, ry, duration=0.5, steps=20):
    """Move smoothly to a position given as ratio of screen size (0..1)."""
    w, h = get_screen_size()
    if w == 0 or h == 0: return False
    return mouse_move_to(int(float(rx) * w), int(float(ry) * h), smooth=True, duration=duration, steps=steps)

def move_mouse_bezier_to(x, y, duration=0.8, steps=40, c1=None, c2=None, jitter=0):
    """
    Move cursor along a cubic Bezier curve from current position to (x,y).
    """
    sx, sy = get_mouse_pos()
    ex, ey = x, y

    dx = ex - sx
    dy = ey - sy

    if c1 is None:
        c1 = (sx + 0.3 * dx, sy + 0.3 * dy)
    if c2 is None:
        c2 = (sx + 0.7 * dx, sy + 0.7 * dy)

    if jitter and jitter > 0:
        c1 = (c1[0] + random.uniform(-jitter, jitter), c1[1] + random.uniform(-jitter, jitter))
        c2 = (c2[0] + random.uniform(-jitter, jitter), c2[1] + random.uniform(-jitter, jitter))

    def bezier(p0, p1, p2, p3, t):
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
        set_mouse_pos(nx, ny)
        time.sleep(step_duration)
    return True

def click(button="left", x=None, y=None, count=1, interval=0.05, smooth=False, duration=0.2, steps=15):
    if not user32: return False
    
    if x is not None and y is not None:
        if smooth:
            mouse_move_to(x, y, smooth=True, duration=duration, steps=steps)
        else:
            set_mouse_pos(x, y)

    for _ in range(int(count)):
        if button == "left":
            user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif button == "right":
            user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        time.sleep(interval)
    return True

def double_click(x=None, y=None, button='left', smooth=False, duration=0.2, steps=15):
    return click(button=button, x=x, y=y, count=2, interval=0.05, smooth=smooth, duration=duration, steps=steps)

def mouse_down(button='left'):
    if not user32: return False
    if button == 'left':
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    elif button == 'right':
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    return True

def mouse_up(button='left'):
    if not user32: return False
    if button == 'left':
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif button == 'right':
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    return True

def drag_to_smooth(x, y, duration=0.5, steps=20, button='left'):
    mouse_down(button)
    mouse_move_to(x, y, smooth=True, duration=duration, steps=steps)
    mouse_up(button)
    return True

def mouse_scroll(amount, direction='vertical'):
    if not user32: return False
    if direction == 'vertical':
        user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, int(amount) * 120, 0)
    return True

def scroll_smooth(clicks, duration=0.5, steps=10, direction='vertical'):
    if steps <= 0: steps = 1
    per = clicks / steps
    for _ in range(steps):
        mouse_scroll(per, direction)
        time.sleep(duration / steps)
    return True

def key_down(vk):
    if user32: user32.keybd_event(int(vk), 0, 0, 0)

def key_up(vk):
    if user32: user32.keybd_event(int(vk), 0, 2, 0)

def key_press(vk):
    key_down(vk)
    key_up(vk)

def hotkey(*vks):
    for vk in vks: key_down(vk)
    for vk in reversed(vks): key_up(vk)

def type_text(text, interval=0.01):
    if _controller:
        for char in str(text):
            _controller.press(char)
            _controller.release(char)
            time.sleep(interval)
    else:
        for char in str(text):
            vk = ord(char.upper())
            key_press(vk)
            time.sleep(interval)

def type_text_human(text, min_interval=0.01, max_interval=0.05):
    for char in str(text):
        type_text(char, 0)
        time.sleep(random.uniform(min_interval, max_interval))

def wait_for_key(target_key=None, timeout=None):
    if pynput_keyboard is None: return None
    pressed = {'val': None}
    tk = str(target_key).lower() if target_key is not None else None

    def on_press(k):
        val = None
        try:
            if isinstance(k, pynput_keyboard.KeyCode): val = k.char
            elif isinstance(k, pynput_keyboard.Key): val = str(k).replace('Key.', '')
        except Exception: val = str(k)
        pressed['val'] = val
        if tk is None or (val and val.lower() == tk): return False
        return True

    listener = pynput_keyboard.Listener(on_press=on_press)
    listener.start()
    start = time.time()
    while listener.running:
        if pressed['val'] is not None and (tk is None or pressed['val'].lower() == tk): break
        if timeout is not None and (time.time() - start) > float(timeout):
            listener.stop()
            return None
        time.sleep(0.01)
    listener.stop()
    return pressed['val']

def get_pixel_color(x, y):
    if not user32 or not gdi32: return (0, 0, 0)
    hdc = user32.GetDC(0)
    pixel = gdi32.GetPixel(hdc, int(x), int(y))
    user32.ReleaseDC(0, hdc)
    return (pixel & 0xff, (pixel >> 8) & 0xff, (pixel >> 16) & 0xff)
