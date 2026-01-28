import ctypes
from ctypes import wintypes
import time
from .common import user32, SW_RESTORE, SW_MAXIMIZE, SW_MINIMIZE, WM_CLOSE

def find_windows(title_part=""):
    if not user32: return []
    hwnds = []
    def foreach_window(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            if title_part.lower() in title.lower():
                hwnds.append(hwnd)
        return True
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(foreach_window), 0)
    return hwnds

def wait_for_window(title_part, timeout_ms=5000):
    start = time.time()
    while (time.time() - start) * 1000 < timeout_ms:
        wins = find_windows(title_part)
        if wins: return wins[0]
        time.sleep(0.1)
    return 0

def get_window_title(hwnd):
    if not user32: return ""
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value

def get_foreground_window():
    return user32.GetForegroundWindow() if user32 else 0

def get_active_window_title():
    hwnd = get_foreground_window()
    return get_window_title(hwnd) if hwnd else ""

def activate_window(hwnd):
    if not user32: return False
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    return True

def move_window(hwnd, x, y, w, h):
    return user32.MoveWindow(hwnd, int(x), int(y), int(w), int(h), True) if user32 else False

def close_window(hwnd):
    if not user32: return False
    user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
    return True

def get_window_rect(hwnd):
    if not user32: return (0, 0, 0, 0)
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)

def maximize_window(hwnd):
    return user32.ShowWindow(hwnd, SW_MAXIMIZE) if user32 else False

def minimize_window(hwnd):
    return user32.ShowWindow(hwnd, SW_MINIMIZE) if user32 else False
