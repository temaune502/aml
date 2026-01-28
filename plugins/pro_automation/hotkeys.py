import threading
import time
import ctypes
from ctypes import wintypes
import aml_runtime_access
from .common import user32, MOD_CONTROL, MOD_ALT, MOD_SHIFT, MOD_WIN, WM_HOTKEY, \
                    VK_SPACE, VK_RETURN, VK_TAB, VK_ESCAPE

_hotkeys = {}
_hotkey_thread = None
_next_hotkey_id = 1
_hotkey_cmd_queue = []
_hotkey_cmd_lock = threading.Lock()

def _hotkey_loop():
    msg = wintypes.MSG()
    while True:
        # Check for new registration commands
        with _hotkey_cmd_lock:
            while _hotkey_cmd_queue:
                cmd = _hotkey_cmd_queue.pop(0)
                if cmd['type'] == 'register':
                    id, modifiers, vk = cmd['id'], cmd['modifiers'], cmd['vk']
                    if user32.RegisterHotKey(None, id, modifiers, vk):
                        pass
                    else:
                        print(f"Failed to register hotkey ID {id}")
                elif cmd['type'] == 'unregister':
                    user32.UnregisterHotKey(None, cmd['id'])
        
        # Peek message
        if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1): # 1 is PM_REMOVE
            if msg.message == WM_HOTKEY:
                id = msg.wParam
                if id in _hotkeys:
                    callback = _hotkeys[id]['callback']
                    interpreter = aml_runtime_access.get_interpreter()
                    if interpreter and callback:
                        try:
                            if hasattr(callback, 'call'):
                                callback.call(interpreter, [])
                            elif callable(callback):
                                callback()
                        except Exception as e:
                            print(f"Error in hotkey callback: {e}")
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        else:
            time.sleep(0.01)

def register_hotkey(hotkey_str, callback):
    global _hotkey_thread, _next_hotkey_id
    if not user32: return False
    
    parts = [p.strip().lower() for p in hotkey_str.split('+')]
    modifiers = 0
    vk = 0
    
    for p in parts:
        if p == 'ctrl' or p == 'control': modifiers |= MOD_CONTROL
        elif p == 'alt': modifiers |= MOD_ALT
        elif p == 'shift': modifiers |= MOD_SHIFT
        elif p == 'win': modifiers |= MOD_WIN
        else:
            if len(p) == 1:
                vk = ord(p.upper())
            elif p.startswith('f') and p[1:].isdigit():
                vk = 0x6F + int(p[1:])
            elif p == 'space': vk = VK_SPACE
            elif p == 'enter' or p == 'return': vk = VK_RETURN
            elif p == 'tab': vk = VK_TAB
            elif p == 'esc' or p == 'escape': vk = VK_ESCAPE
            
    if vk == 0:
        print(f"Invalid hotkey: {hotkey_str}")
        return False
        
    id = _next_hotkey_id
    _next_hotkey_id += 1
    _hotkeys[id] = {'modifiers': modifiers, 'vk': vk, 'callback': callback, 'str': hotkey_str}
    
    with _hotkey_cmd_lock:
        _hotkey_cmd_queue.append({'type': 'register', 'id': id, 'modifiers': modifiers, 'vk': vk})
        
    if _hotkey_thread is None:
        _hotkey_thread = threading.Thread(target=_hotkey_loop, daemon=True)
        _hotkey_thread.start()
        
    return id

def unregister_hotkey(id):
    if not user32: return False
    if id in _hotkeys:
        with _hotkey_cmd_lock:
            _hotkey_cmd_queue.append({'type': 'unregister', 'id': id})
        del _hotkeys[id]
        return True
    return False
