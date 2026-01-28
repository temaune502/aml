import ctypes
from ctypes import wintypes
import platform

# Constants for Windows API
GWL_STYLE = -16
WS_VISIBLE = 0x10000000
SW_MINIMIZE = 6
SW_MAXIMIZE = 3
SW_RESTORE = 9

# Hotkey Modifiers
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
WM_HOTKEY = 0x0312

# Virtual Key Codes
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_BACK = 0x08
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12 # ALT
VK_PAUSE = 0x13
VK_CAPITAL = 0x14
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_PRIOR = 0x21 # PAGE UP
VK_NEXT = 0x22 # PAGE DOWN
VK_END = 0x23
VK_HOME = 0x24
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_INSERT = 0x2D
VK_DELETE = 0x2E
VK_LWIN = 0x5B
VK_RWIN = 0x5C

# Mouse event constants
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800

# Window Message Constants
WM_CLOSE = 0x0010
WM_SYSCOMMAND = 0x0112
SC_MONITORPOWER = 0xF170
HWND_BROADCAST = 0xFFFF

user32 = None
kernel32 = None
gdi32 = None
dxva2 = None

if platform.system() == "Windows":
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    gdi32 = ctypes.windll.gdi32
    try:
        dxva2 = ctypes.windll.dxva2
    except Exception:
        dxva2 = None

class PHYSICAL_MONITOR(ctypes.Structure):
    _fields_ = [("hPhysicalMonitor", wintypes.HANDLE),
                ("szPhysicalMonitorDescription", wintypes.WCHAR * 128)]

# New constants for system features
WM_INPUTLANGCHANGEREQUEST = 0x0050

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
