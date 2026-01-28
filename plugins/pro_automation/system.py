import time
import ctypes
import subprocess
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


# --- New Features ---

def set_brightness(level):
    """Sets monitor brightness (0-100) using both DXVA2 and WMI as fallback"""
    level = max(0, min(100, int(level)))
    success = False
    
    # Try DXVA2 first (Native)
    if dxva2 and user32:
        try:
            def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
                count = wintypes.DWORD()
                if dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(hMonitor, ctypes.byref(count)):
                    physical_monitors = (PHYSICAL_MONITOR * count.value)()
                    if dxva2.GetPhysicalMonitorsFromHMONITOR(hMonitor, count.value, physical_monitors):
                        for i in range(count.value):
                            dxva2.SetMonitorBrightness(physical_monitors[i].hPhysicalMonitor, level)
                        dxva2.DestroyPhysicalMonitors(count.value, physical_monitors)
                return True

            MONITORENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
            user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(callback), 0)
            success = True
        except Exception:
            pass

    # Fallback to WMI (especially for laptops)
    try:
        cmd = f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
        subprocess.run(cmd, shell=True, capture_output=True, timeout=2)
        success = True
    except Exception:
        pass
        
    return success

def get_brightness():
    """Gets current monitor brightness using DXVA2 or WMI fallback"""
    # Try DXVA2 first
    if dxva2 and user32:
        try:
            brightness_list = []
            def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
                count = wintypes.DWORD()
                if dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(hMonitor, ctypes.byref(count)):
                    physical_monitors = (PHYSICAL_MONITOR * count.value)()
                    if dxva2.GetPhysicalMonitorsFromHMONITOR(hMonitor, count.value, physical_monitors):
                        for i in range(count.value):
                            min_b, cur_b, max_b = wintypes.DWORD(), wintypes.DWORD(), wintypes.DWORD()
                            if dxva2.GetMonitorBrightness(physical_monitors[i].hPhysicalMonitor, ctypes.byref(min_b), ctypes.byref(cur_b), ctypes.byref(max_b)):
                                brightness_list.append(int(cur_b.value))
                        dxva2.DestroyPhysicalMonitors(count.value, physical_monitors)
                return True

            MONITORENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
            user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(callback), 0)
            if brightness_list:
                return brightness_list[0]
        except Exception:
            pass

    # Try WMI fallback
    try:
        cmd = "powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=2)
        if result.stdout.strip():
            return int(result.stdout.strip())
    except Exception:
        pass
        
    return -1

def set_volume(level):
    """Sets system volume (0-100) using direct sound endpoint API via ctypes"""
    if not user32: return False
    try:
        level = max(0, min(100, int(level)))
        # VK_VOLUME_MUTE = 0xAD, VK_VOLUME_DOWN = 0xAE, VK_VOLUME_UP = 0xAF
        VK_VOLUME_MUTE = 0xAD
        VK_VOLUME_DOWN = 0xAE
        VK_VOLUME_UP = 0xAF
        
        # 1. Reset to 0
        for _ in range(50):
            user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
            user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0) # KEYEVENTF_KEYUP = 2
            
        # 2. Set to level
        steps = int(level / 2)
        for _ in range(steps):
            user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
            user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
            
        return True
    except Exception as e:
        print(f"Error setting volume: {e}")
        return False

def get_volume():
    """Gets current system volume (0-100) using Core Audio API (WASAPI) via ctypes"""
    try:
        # Core Audio Constants & GUIDs
        CLSCTX_ALL = 0x17
        CLSCTX_INPROC_SERVER = 0x1
        CLSID_MMDeviceEnumerator = "{BCDE0395-E52F-467C-8E3D-C4579291692E}"
        IID_IMMDeviceEnumerator = "{A95664D2-9614-4F35-A746-DE8DB63617E6}"
        IID_IAudioEndpointVolume = "{5CDF2C82-841E-4546-9722-0CF74078229A}"
        HRESULT = ctypes.c_long

        class _GUID(ctypes.Structure):
            _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                       ("Data3", wintypes.WORD), ("Data4", wintypes.BYTE * 8)]
            
        def str_to_guid(s):
            import re
            m = re.match(r"\{?([\dA-F]{8})-([\dA-F]{4})-([\dA-F]{4})-([\dA-F]{2})([\dA-F]{2})-([\dA-F]{12})\}?", s, re.I)
            if not m: return None
            d = m.groups()
            g = _GUID()
            g.Data1, g.Data2, g.Data3 = int(d[0], 16), int(d[1], 16), int(d[2], 16)
            g.Data4[0], g.Data4[1] = int(d[3], 16), int(d[4], 16)
            for i in range(6): g.Data4[i+2] = int(d[5][i*2:i*2+2], 16)
            return g

        class IUnknown(ctypes.Structure):
            _fields_ = [("lpVtbl", ctypes.POINTER(ctypes.c_void_p))]

        # Initialize COM
        ctypes.windll.ole32.CoInitialize(None)
        
        try:
            # 1. Create MMDeviceEnumerator
            clsid_enum = str_to_guid(CLSID_MMDeviceEnumerator)
            iid_enum = str_to_guid(IID_IMMDeviceEnumerator)
            enumerator = ctypes.POINTER(IUnknown)()
            res = ctypes.windll.ole32.CoCreateInstance(
                ctypes.byref(clsid_enum), None, CLSCTX_INPROC_SERVER,
                ctypes.byref(iid_enum), ctypes.byref(enumerator)
            )
            if res != 0: return -1

            # 2. Get Default Audio Endpoint (vtable index 4)
            get_def_proto = ctypes.WINFUNCTYPE(HRESULT, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
            get_def = get_def_proto(enumerator.contents.lpVtbl[4])
            device = ctypes.c_void_p()
            if get_def(enumerator, 0, 0, ctypes.byref(device)) != 0: return -1

            # 3. Activate IAudioEndpointVolume (vtable index 3)
            class IMMDevice(ctypes.Structure): _fields_ = [("lpVtbl", ctypes.POINTER(ctypes.c_void_p))]
            device_ptr = ctypes.cast(device, ctypes.POINTER(IMMDevice))
            activate_proto = ctypes.WINFUNCTYPE(HRESULT, ctypes.c_void_p, ctypes.POINTER(_GUID), wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
            activate = activate_proto(device_ptr.contents.lpVtbl[3])
            
            iid_vol = str_to_guid(IID_IAudioEndpointVolume)
            vol_interface = ctypes.c_void_p()
            if activate(device, ctypes.byref(iid_vol), CLSCTX_ALL, None, ctypes.byref(vol_interface)) != 0: return -1

            # 4. Get Master Volume Level Scalar (vtable index 9)
            class IAudioEndpointVolume(ctypes.Structure): _fields_ = [("lpVtbl", ctypes.POINTER(ctypes.c_void_p))]
            vol_ptr = ctypes.cast(vol_interface, ctypes.POINTER(IAudioEndpointVolume))
            get_scal_proto = ctypes.WINFUNCTYPE(HRESULT, ctypes.c_void_p, ctypes.POINTER(ctypes.c_float))
            get_scal = get_scal_proto(vol_ptr.contents.lpVtbl[9])
            
            current_vol = ctypes.c_float()
            if get_scal(vol_interface, ctypes.byref(current_vol)) == 0:
                return int(current_vol.value * 100)
        finally:
            ctypes.windll.ole32.CoUninitialize()
    except Exception:
        pass
        
    return -1

def monitor_on():
    """Turns the monitor on"""
    if user32:
        user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, -1)
        return True
    return False

def monitor_off():
    """Turns the monitor off"""
    if user32:
        user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2)
        return True
    return False

def set_keyboard_layout(lang_id):
    """
    Sets keyboard layout for the active window and system.
    lang_id can be 'en', 'uk', or a hex string like '00000409'
    """
    layouts = {
        'en': '00000409',
        'uk': '00000422',
        'ru': '00000419'
    }
    hex_id = layouts.get(lang_id.lower(), lang_id)
    
    if not user32: return False
    
    try:
        # Load the layout
        layout = user32.LoadKeyboardLayoutW(hex_id, 1) # 1 is KLF_ACTIVATE
        if not layout: return False
        
        # 1. Change for current thread
        user32.ActivateKeyboardLayout(layout, 0)
        
        # 2. Change for the foreground window
        hwnd = user32.GetForegroundWindow()
        if hwnd:
            # We must use PostMessage with WM_INPUTLANGCHANGEREQUEST
            # Using 0 as wParam and the layout handle as lParam
            user32.PostMessageW(hwnd, WM_INPUTLANGCHANGEREQUEST, 0, layout)
            
        # 3. Also try broadcasting to all windows (some apps respond to this)
        user32.PostMessageW(HWND_BROADCAST, WM_INPUTLANGCHANGEREQUEST, 0, layout)
        
        # 4. Optional: Force layout change via SystemParametersInfo if needed, 
        # but usually LoadKeyboardLayout with KLF_ACTIVATE is enough for system-wide.
        
        return True
    except Exception:
        return False

def get_keyboard_layout():
    """Gets the current keyboard layout ID"""
    if not user32: return ""
    # Get current thread's layout
    layout_id = user32.GetKeyboardLayout(0)
    return hex(layout_id & 0xFFFF)
