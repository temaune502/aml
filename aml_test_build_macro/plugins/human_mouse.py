import time
import math
import random
import ctypes
import platform

# --- Win32 API setup ---
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

user32 = None
if platform.system() == "Windows":
    user32 = ctypes.windll.user32

def get_mouse_pos():
    """Returns the current mouse cursor position (x, y)."""
    if not user32: return (0, 0)
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)

def set_mouse_pos(x, y):
    """Sets the mouse cursor position to (x, y)."""
    if user32:
        user32.SetCursorPos(int(x), int(y))
        return True
    return False

def mouse_event(flags, x=0, y=0, data=0):
    """Triggers a mouse event via user32.mouse_event."""
    if user32:
        user32.mouse_event(flags, int(x), int(y), data, 0)

# --- Path Optimization Helpers ---

def min_jerk(t: float) -> float: 
    """Minimum jerk trajectory profile (S-curve).""" 
    return 10*t**3 - 15*t**4 + 6*t**5 

def clamp(value, limit): 
    """Clamps value within [-limit, limit]."""
    return max(-limit, min(limit, value)) 

def smoothstep(t): 
    """Smooth interpolation from 0 to 1."""
    return t * t * (3 - 2 * t) 
    
def compress_path(path, min_dist=1): 
    """ 
    Removes redundant points:
    - duplicates
    - micro-movements < min_dist px
    """ 
    if not path: 
        return [] 

    compressed = [path[0]] 
    last_x, last_y = path[0] 

    for x, y in path[1:]: 
        if abs(x - last_x) >= min_dist or abs(y - last_y) >= min_dist: 
            compressed.append((x, y)) 
            last_x, last_y = x, y 
    return compressed 

# --- Human Movement Logic ---

class HumanMouse:
    """
    Simulates human-like mouse movements. 
    Variant 1 (Main): Vector-based with dynamic noise.
    Variant 2 (Advanced): Mathematical path generation with minimum jerk and filtered noise.
    """
    
    def __init__(self, speed_level=3, jitter_intensity=1.0):
        self.speed_level = max(1, min(10, speed_level))
        self.jitter_intensity = jitter_intensity

    def move_to(self, x, y, speed_override=None, steady=False):
        """
        Main movement method: Vector-based with dynamic drift.
        Efficient and realistic for most tasks.
        """
        sx, sy = get_mouse_pos()
        tx, ty = int(x), int(y)
        dx, dy = tx - sx, ty - sy
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 1: return

        current_speed = speed_override if speed_override is not None else self.speed_level
        steps = int(max(15, dist / 8) * (current_speed / 2.0) * random.uniform(0.9, 1.1))
        
        angle = math.atan2(dy, dx)
        perp_angle = angle + (math.pi / 2) * random.choice([-1, 1])
        max_drift = (dist * 0.12) * random.uniform(0.5, 1.5)
        if steady: max_drift *= 0.2

        drift_frequency = random.uniform(0.8, 1.5)
        drift_phase = random.uniform(0, math.pi)

        for i in range(steps + 1):
            t = i / steps
            envelope = math.sin(t * math.pi) 
            progress = (1 - math.cos(t * math.pi)) / 2
            
            curr_x = sx + progress * dx + math.cos(perp_angle) * (math.sin(t * math.pi * drift_frequency + drift_phase) * max_drift * envelope)
            curr_y = sy + progress * dy + math.sin(perp_angle) * (math.sin(t * math.pi * drift_frequency + drift_phase) * max_drift * envelope)
            
            if not steady:
                jitter_scale = self.jitter_intensity * (0.3 + 0.7 * envelope)
                curr_x += random.uniform(-1.0, 1.0) * jitter_scale
                curr_y += random.uniform(-1.0, 1.0) * jitter_scale
            
            set_mouse_pos(curr_x, curr_y)
            base_wait = 0.0008 * current_speed
            time.sleep(base_wait * (1.0 + (1.0 - envelope) * 0.8) * random.uniform(0.85, 1.15))

    def move_advanced(self, x, y, speed=3):
        """
        Advanced movement method: Generates a full path first using 
        minimum jerk profile and noise filtering, then executes it.
        """
        start = get_mouse_pos()
        end = (int(x), int(y))
        path = self._generate_advanced_path(start, end)
        
        # Execution timing for pre-calculated path
        # Total time depends on distance and speed
        dist = math.hypot(end[0]-start[0], end[1]-start[1])
        total_time = (dist / 1000.0) * speed * random.uniform(0.8, 1.2)
        if len(path) > 1:
            step_delay = total_time / len(path)
            for px, py in path:
                set_mouse_pos(px, py)
                time.sleep(step_delay * random.uniform(0.5, 1.5))

    def _generate_advanced_path(self, start, end):
        """Internal: Generates complex human-like path coordinates."""
        x0, y0 = start 
        x1, y1 = end 
        dx, dy = x1 - x0, y1 - y0 
        dist = math.hypot(dx, dy) 
        if dist == 0: return [start] 

        steps = int(60 + dist * 0.35) 
        ux, uy = dx / dist, dy / dist 
        base_nx, base_ny = -uy, ux 
        
        path = [] 
        noise = 0.0 
        filtered_x, filtered_y = float(x0), float(y0) 
        alpha, smooth_alpha = 0.85, 0.25 
        max_dev = dist * 0.05 
        angle = random.uniform(-0.12, 0.12) 
        angle_drift = random.uniform(-0.008, 0.008) 
    
        for i in range(steps): 
            t = i / (steps - 1) 
            s = min_jerk(t) 
            bx, by = x0 + dx * s, y0 + dy * s 
            
            gain = smoothstep(min(t / 0.25, 1.0)) 
            sigma = dist * 0.012 * (1 - t) 
            noise = alpha * noise + random.gauss(0, sigma) 
            noise *= gain 
            
            angle += angle_drift 
            nx = base_nx * math.cos(angle) - base_ny * math.sin(angle) 
            ny = base_nx * math.sin(angle) + base_ny * math.cos(angle) 
            
            correction = min(math.hypot(x1 - bx, y1 - by) / dist, 1.0) 
            offset = clamp(noise * correction, max_dev) 
            
            tx, ty = bx + offset * nx, by + offset * ny 
            filtered_x += smooth_alpha * (tx - filtered_x) 
            filtered_y += smooth_alpha * (ty - filtered_y) 
            
            ix, iy = int(round(filtered_x)), int(round(filtered_y)) 
            path.append((ix, iy)) 
            if random.random() < 0.03: path.append((ix, iy)) 
    
        return compress_path(path, min_dist=1)

    def click(self, x=None, y=None, button='left', clicks=1, interval=0.1):
        if x is not None and y is not None: self.move_to(x, y)
        for i in range(clicks):
            time.sleep(random.uniform(0.04, 0.12))
            down_flag = MOUSEEVENTF_LEFTDOWN if button == 'left' else MOUSEEVENTF_RIGHTDOWN
            up_flag = MOUSEEVENTF_LEFTUP if button == 'left' else MOUSEEVENTF_RIGHTUP
            mouse_event(down_flag)
            time.sleep(random.uniform(0.07, 0.18))
            mouse_event(up_flag)
            if i < clicks - 1: time.sleep(interval * random.uniform(0.7, 1.3))
        time.sleep(random.uniform(0.12, 0.25))

    def drag_to(self, x, y, speed=5):
        mouse_event(MOUSEEVENTF_LEFTDOWN)
        time.sleep(random.uniform(0.2, 0.4))
        self.move_to(x, y, speed_override=speed, steady=True)
        time.sleep(random.uniform(0.15, 0.3))
        mouse_event(MOUSEEVENTF_LEFTUP)

# --- AML Interface ---
_inst = HumanMouse()

def move_human(x, y, speed=3):
    """AML-facing: Standard human-like move (Fast & Efficient)."""
    _inst.move_to(x, y, speed_override=speed)

def move_human_advanced(x, y, speed=3):
    """AML-facing: Advanced human-like move (Complex Path Calculation)."""
    _inst.move_advanced(x, y, speed=speed)

def click_human(x=None, y=None, button='left', clicks=1):
    _inst.click(x, y, button=button, clicks=clicks)

def drag_human(x, y, speed=5):
    _inst.drag_to(x, y, speed=speed)

if __name__ == "__main__":
    print("Testing HumanMouse Variants...")
    time.sleep(2)
    sx, sy = get_mouse_pos()
    
    print("1. Standard move_to...")
    move_human(sx + 200, sy + 200)
    time.sleep(1)
    
    print("2. Advanced move_human_advanced...")
    move_human_advanced(sx, sy)
    print("Test complete.")
