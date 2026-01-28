# Curves and trajectory math module
# Provides advanced movement patterns and curve interpolation for smooth, natural mouse movement

import math
import random


# --- Basic Curve Interpolation ---

def linear(t):
    """Linear interpolation (t: 0..1) -> 0..1"""
    return t

def ease_in_quad(t):
    """Quadratic easing in (slow start)"""
    return t * t

def ease_out_quad(t):
    """Quadratic easing out (slow end)"""
    return 1 - (1 - t) ** 2

def ease_in_out_quad(t):
    """Quadratic easing in-out"""
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2

def ease_in_cubic(t):
    """Cubic easing in"""
    return t ** 3

def ease_out_cubic(t):
    """Cubic easing out"""
    return 1 - (1 - t) ** 3

def ease_in_out_cubic(t):
    """Cubic easing in-out"""
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2

def ease_in_sin(t):
    """Sine easing in"""
    return 1 - math.cos((t * math.pi) / 2)

def ease_out_sin(t):
    """Sine easing out"""
    return math.sin((t * math.pi) / 2)

def ease_in_out_sin(t):
    """Sine easing in-out"""
    return -(math.cos(math.pi * t) - 1) / 2


# --- Path Interpolation ---

def lerp(p0, p1, t):
    """Linear interpolation between two points p0, p1 (0..1)"""
    return (
        p0[0] + (p1[0] - p0[0]) * t,
        p0[1] + (p1[1] - p0[1]) * t,
    )

def quadratic_bezier(p0, p1, p2, t):
    """Quadratic Bezier curve (3 control points)"""
    u = 1 - t
    return (
        u**2 * p0[0] + 2 * u * t * p1[0] + t**2 * p2[0],
        u**2 * p0[1] + 2 * u * t * p1[1] + t**2 * p2[1],
    )

def cubic_bezier(p0, p1, p2, p3, t):
    """Cubic Bezier curve (4 control points)"""
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
    )

def catmull_rom(p0, p1, p2, p3, t):
    """Catmull-Rom spline (smooth curve through p1, p2)"""
    t2 = t * t
    t3 = t2 * t
    return (
        0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
               + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
        0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
               + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3),
    )


# --- Path Generation from Points ---

def interpolate_path(points, steps_per_segment=10, curve_type='catmull'):
    """
    Interpolate a smooth path through a list of points.
    - points: list of (x, y) tuples
    - steps_per_segment: interpolation steps between consecutive points
    - curve_type: 'linear', 'quadratic', 'cubic', 'catmull'
    Returns: list of interpolated points
    """
    if len(points) < 2:
        return list(points)

    result = []

    if curve_type == 'linear':
        for i in range(len(points) - 1):
            p0, p1 = points[i], points[i + 1]
            for step in range(steps_per_segment):
                t = step / steps_per_segment
                result.append(lerp(p0, p1, t))
        result.append(points[-1])

    elif curve_type == 'quadratic':
        for i in range(len(points) - 2):
            p0, p1, p2 = points[i], points[i + 1], points[i + 2]
            for step in range(steps_per_segment):
                t = step / steps_per_segment
                result.append(quadratic_bezier(p0, p1, p2, t))
        result.append(points[-1])

    elif curve_type == 'cubic':
        if len(points) < 4:
            return interpolate_path(points, steps_per_segment, 'linear')
        for i in range(len(points) - 3):
            p0, p1, p2, p3 = points[i:i+4]
            for step in range(steps_per_segment):
                t = step / steps_per_segment
                result.append(cubic_bezier(p0, p1, p2, p3, t))
        result.append(points[-1])

    elif curve_type == 'catmull':
        if len(points) < 4:
            return interpolate_path(points, steps_per_segment, 'linear')
        # Extend points for boundary handling
        extended = [points[0]] + points + [points[-1]]
        for i in range(1, len(extended) - 2):
            p0, p1, p2, p3 = extended[i-1:i+3]
            for step in range(steps_per_segment):
                t = step / steps_per_segment
                result.append(catmull_rom(p0, p1, p2, p3, t))
        result.append(points[-1])

    else:
        return interpolate_path(points, steps_per_segment, 'linear')

    return result


# --- Pattern Generators ---

def sine_wave(start, end, amplitude=50, frequency=2, steps=100):
    """
    Generate a sine wave trajectory from start to end.
    - start, end: (x, y) tuples
    - amplitude: max deviation from straight line (pixels)
    - frequency: number of oscillations
    - steps: total points to generate
    Returns: list of points
    """
    points = []
    sx, sy = start
    ex, ey = end
    for i in range(steps):
        t = i / max(1, steps - 1)
        x = sx + (ex - sx) * t
        y = sy + (ey - sy) * t
        # Add perpendicular offset based on sine wave
        angle = math.atan2(ey - sy, ex - sx)
        offset = amplitude * math.sin(t * frequency * 2 * math.pi)
        x += offset * math.cos(angle + math.pi / 2)
        y += offset * math.sin(angle + math.pi / 2)
        points.append((x, y))
    return points

def spiral_path(center, start_radius=10, end_radius=100, turns=2, steps=100):
    """
    Generate an outward (or inward) spiral path.
    - center: (x, y) tuple
    - start_radius, end_radius: starting/ending distance from center
    - turns: number of complete rotations
    - steps: total points to generate
    Returns: list of points
    """
    points = []
    cx, cy = center
    for i in range(steps):
        t = i / max(1, steps - 1)
        radius = start_radius + (end_radius - start_radius) * t
        angle = t * turns * 2 * math.pi
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    return points

def circle_path(center, radius, steps=100, start_angle=0, end_angle=360):
    """
    Generate a circular arc path.
    - center: (x, y) tuple
    - radius: circle radius (pixels)
    - steps: total points
    - start_angle, end_angle: arc bounds (degrees)
    Returns: list of points
    """
    points = []
    cx, cy = center
    start_rad = math.radians(start_angle)
    end_rad = math.radians(end_angle)
    for i in range(steps):
        t = i / max(1, steps - 1)
        angle = start_rad + (end_rad - start_rad) * t
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    return points

def random_walk_path(start, step_size=10, steps=50, bounds=None):
    """
    Generate a random walk trajectory starting from start.
    - start: (x, y) tuple
    - step_size: max movement per step (pixels)
    - steps: number of steps
    - bounds: ((min_x, min_y), (max_x, max_y)) or None
    Returns: list of points
    """
    points = [start]
    x, y = start
    for _ in range(steps):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, step_size)
        x += dist * math.cos(angle)
        y += dist * math.sin(angle)
        if bounds:
            (min_x, min_y), (max_x, max_y) = bounds
            x = max(min_x, min(x, max_x))
            y = max(min_y, min(y, max_y))
        points.append((x, y))
    return points

def zigzag_path(start, end, amplitude=30, zigzags=5, steps=100):
    """
    Generate a zigzag trajectory from start to end.
    - start, end: (x, y) tuples
    - amplitude: max deviation from line
    - zigzags: number of zigzags
    - steps: total points
    Returns: list of points
    """
    points = []
    sx, sy = start
    ex, ey = end
    for i in range(steps):
        t = i / max(1, steps - 1)
        x = sx + (ex - sx) * t
        y = sy + (ey - sy) * t
        # Triangle wave (zigzag)
        zig_t = (t * zigzags) % 1.0
        offset = amplitude * (1 - 2 * abs(zig_t - 0.5))
        angle = math.atan2(ey - sy, ex - sx)
        x += offset * math.cos(angle + math.pi / 2)
        y += offset * math.sin(angle + math.pi / 2)
        points.append((x, y))
    return points

def gaussian_noise_path(start, end, sigma=20, steps=100):
    """
    Add Gaussian noise to a straight line path (natural human-like jitter).
    - start, end: (x, y) tuples
    - sigma: standard deviation of noise (pixels)
    - steps: total points
    Returns: list of points
    """
    points = []
    sx, sy = start
    ex, ey = end
    for i in range(steps):
        t = i / max(1, steps - 1)
        x = sx + (ex - sx) * t + random.gauss(0, sigma)
        y = sy + (ey - sy) * t + random.gauss(0, sigma)
        points.append((x, y))
    return points

def composite_path(start, end, primary_pattern='sine', secondary_noise=5, steps=100):
    """
    Combine a primary pattern with secondary noise for realistic movement.
    - start, end: (x, y) tuples
    - primary_pattern: 'sine', 'spiral', 'zigzag', 'random_walk'
    - secondary_noise: sigma for Gaussian jitter (0 = no noise)
    - steps: total points
    Returns: list of points
    """
    if primary_pattern == 'sine':
        base = sine_wave(start, end, amplitude=30, frequency=2, steps=steps)
    elif primary_pattern == 'zigzag':
        base = zigzag_path(start, end, amplitude=25, zigzags=4, steps=steps)
    elif primary_pattern == 'random_walk':
        base = random_walk_path(start, step_size=8, steps=steps-1)
        # Ensure we end at target
        base[-1] = end
    elif primary_pattern == 'spiral':
        cx, cy = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        dist = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        base = spiral_path(cx, start_radius=5, end_radius=dist/2, turns=1.5, steps=steps)
    else:
        base = gaussian_noise_path(start, end, sigma=secondary_noise, steps=steps)

    # Add secondary noise
    if secondary_noise > 0:
        noisy = []
        for x, y in base:
            nx = x + random.gauss(0, secondary_noise)
            ny = y + random.gauss(0, secondary_noise)
            noisy.append((nx, ny))
        return noisy
    return base


# --- Path Analysis ---

def path_length(points):
    """Calculate total path length (sum of segment distances)"""
    total = 0.0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        total += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return total

def path_velocity(points, time_steps):
    """Calculate velocity at each point along path (pixels per frame)"""
    distances = []
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        distances.append(dist / time_steps[i] if time_steps[i] > 0 else 0)
    return distances

def resample_path(points, total_distance):
    """
    Resample path to uniform speed (equal distance between points).
    - points: list of (x, y)
    - total_distance: target total path length
    Returns: resampled list of points
    """
    if len(points) < 2:
        return points
    
    # Calculate cumulative distances
    distances = [0]
    total_len = 0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        total_len += dist
        distances.append(total_len)

    if total_len == 0:
        return [points[0]]

    # Resample at uniform intervals
    num_samples = max(2, int(total_distance / (total_len / len(points))))
    resampled = []
    
    for i in range(num_samples):
        target_dist = (i / max(1, num_samples - 1)) * total_len
        # Find segment containing target distance
        for j in range(len(distances) - 1):
            if distances[j] <= target_dist <= distances[j + 1]:
                # Linear interpolation within segment
                if distances[j + 1] == distances[j]:
                    t = 0
                else:
                    t = (target_dist - distances[j]) / (distances[j + 1] - distances[j])
                x = points[j][0] + (points[j + 1][0] - points[j][0]) * t
                y = points[j][1] + (points[j + 1][1] - points[j][1]) * t
                resampled.append((x, y))
                break
    
    return resampled if resampled else [points[0], points[-1]]
