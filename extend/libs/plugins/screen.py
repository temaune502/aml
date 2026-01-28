"""
Screen модуль для роботи з екраном

Модуль забезпечує роботу зі скріншотами, пошук зображень, виділення областей,
аналіз вмісту екрану та моніторинг змін.

Функції:
    - Порівняння скріншотів
    - Пошук зображення на екрані
    - Виділення областей
    - Аналіз змін на екрані
    - Поділ екрану на сектори
"""

import os
from PIL import Image, ImageGrab, ImageChops, ImageDraw
from typing import Tuple, List, Optional, Dict
import numpy as np
from pathlib import Path
import time
import hashlib


def get_screen_size() -> Tuple[int, int]:
    """
    Отримати розмір екрану
    
    Returns:
        Tuple: (ширина, висота) в пікселях
    """
    try:
        import ctypes
        width = ctypes.windll.user32.GetSystemMetrics(0)
        height = ctypes.windll.user32.GetSystemMetrics(1)
        return (width, height)
    except:
        img = ImageGrab.grab()
        return img.size


def screenshot_region(x1: int, y1: int, x2: int, y2: int) -> Image.Image:
    """
    Зробити скріншот прямокутної області
    
    Args:
        x1, y1: Верхній лівий кут
        x2, y2: Нижній правий кут
    
    Returns:
        Image: PIL Image об'єкт
    """
    return ImageGrab.grab(bbox=(x1, y1, x2, y2))


def save_screenshot(filepath: str,
                    region: Optional[Tuple[int, int, int, int]] = None) -> bool:
    """
    Зберегти скріншот у файл
    
    Args:
        filepath: Шлях для збереження
        region: Область (x1, y1, x2, y2) або None для всього екрану
    
    Returns:
        bool: True якщо успішно
    """
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        if region:
            img = screenshot_region(*region)
        else:
            img = ImageGrab.grab()
        
        img.save(filepath)
        return True
    except Exception as e:
        print(f"Помилка збереження скріншота: {e}")
        return False


def load_image(filepath: str) -> Optional[Image.Image]:
    """
    Завантажити зображення з файлу
    
    Args:
        filepath: Шлях до файлу
    
    Returns:
        Image: PIL Image об'єкт або None
    """
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл не знайдено: {filepath}")
        return Image.open(filepath)
    except Exception as e:
        print(f"Помилка завантаження зображення: {e}")
        return None


def compare_images(image1: Image.Image,
                   image2: Image.Image,
                   threshold: float = 0.95) -> Tuple[bool, float]:
    """
    Порівняти два зображення
    
    Args:
        image1: Перше зображення
        image2: Друге зображення
        threshold: Поріг схожості (0.0-1.0)
    
    Returns:
        Tuple: (схожі, коефіцієнт_схожості)
    """
    try:
        if image1.size != image2.size:
            image2 = image2.resize(image1.size, Image.Resampling.LANCZOS)
        
        diff = ImageChops.difference(image1, image2)
        
        # Обчислити відсоток відмінність
        pixels = np.array(diff)
        max_diff = 255.0
        similarity = 1.0 - (np.sum(pixels) / (pixels.size * max_diff))
        
        return (similarity >= threshold, similarity)
    except Exception as e:
        print(f"Помилка порівняння зображень: {e}")
        return (False, 0.0)


def find_image_on_screen(template_path: str,
                        confidence: float = 0.8,
                        region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
    """
    Знайти шаблон зображення на екрані
    
    Args:
        template_path: Шлях до файлу шаблону
        confidence: Поріг впевненості (0.0-1.0)
        region: Область пошуку (x1, y1, x2, y2) або None
    
    Returns:
        Tuple: Центр знайденого зображення (x, y) або None
    """
    try:
        import cv2
        
        template = cv2.imread(template_path)
        if template is None:
            raise FileNotFoundError(f"Шаблон не знайдено: {template_path}")
        
        if region:
            screenshot = screenshot_region(*region)
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        else:
            screenshot = cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            if region:
                center_x += region[0]
                center_y += region[1]
            
            return (center_x, center_y)
        
        return None
    except ImportError:
        print("Помилка: opencv-python не встановлено. Встановіть: pip install opencv-python")
        return None
    except Exception as e:
        print(f"Помилка пошуку зображення: {e}")
        return None


def find_image_all(template_path: str,
                   confidence: float = 0.8,
                   region: Optional[Tuple[int, int, int, int]] = None) -> List[Tuple[int, int]]:
    """
    Знайти всі входження шаблону на екрані
    
    Args:
        template_path: Шлях до файлу шаблону
        confidence: Поріг впевненості
        region: Область пошуку
    
    Returns:
        List[Tuple]: Список центрів знайдених зображень
    """
    try:
        import cv2
        
        template = cv2.imread(template_path)
        if template is None:
            raise FileNotFoundError(f"Шаблон не знайдено: {template_path}")
        
        if region:
            screenshot = screenshot_region(*region)
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        else:
            screenshot = cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= confidence)
        
        h, w = template.shape[:2]
        matches = []
        
        for y, x in zip(locations[0], locations[1]):
            center_x = x + w // 2
            center_y = y + h // 2
            
            if region:
                center_x += region[0]
                center_y += region[1]
            
            matches.append((center_x, center_y))
        
        return matches
    except ImportError:
        print("Помилка: opencv-python не встановлено")
        return []
    except Exception as e:
        print(f"Помилка пошуку всіх входжень: {e}")
        return []


def get_image_hash(image: Image.Image) -> str:
    """
    Отримати хеш зображення для швидкого порівняння
    
    Args:
        image: PIL Image об'єкт
    
    Returns:
        str: Хеш зображення
    """
    try:
        img_bytes = image.tobytes()
        return hashlib.md5(img_bytes).hexdigest()
    except Exception as e:
        print(f"Помилка хешування зображення: {e}")
        return ""


def detect_changes(screenshot1: Image.Image,
                   screenshot2: Image.Image,
                   threshold: int = 30) -> Tuple[bool, float, Image.Image]:
    """
    Виявити зміни між двома скріншотами
    
    Args:
        screenshot1: Перший скріншот
        screenshot2: Другий скріншот
        threshold: Поріг чутливості (0-255)
    
    Returns:
        Tuple: (є_зміни, відсоток_змін, зображення_різниці)
    """
    try:
        if screenshot1.size != screenshot2.size:
            screenshot2 = screenshot2.resize(screenshot1.size, Image.Resampling.LANCZOS)
        
        diff = ImageChops.difference(screenshot1, screenshot2)
        
        # Конвертування до чорно-білого для аналізу
        bw_diff = diff.convert('L')
        pixels = np.array(bw_diff)
        
        # Знайти пікселі, які змінилися
        changed_pixels = np.sum(pixels > threshold)
        total_pixels = pixels.size
        change_percentage = (changed_pixels / total_pixels) * 100
        
        has_changes = change_percentage > 0.1
        
        # Створити зображення з виділеними змінами
        change_img = Image.new('RGB', screenshot1.size, 'white')
        for y in range(pixels.shape[0]):
            for x in range(pixels.shape[1]):
                if pixels[y, x] > threshold:
                    change_img.putpixel((x, y), 'red')
        
        return (has_changes, change_percentage, change_img)
    except Exception as e:
        print(f"Помилка виявлення змін: {e}")
        return (False, 0.0, None)


def split_screen_grid(cols: int = 2, rows: int = 2) -> Dict[str, Tuple[int, int, int, int]]:
    """
    Розділити екран на сітку областей
    
    Args:
        cols: Кількість стовпців
        rows: Кількість рядків
    
    Returns:
        Dict: Словник з назвами регіонів та їх координатами
    """
    width, height = get_screen_size()
    cell_width = width // cols
    cell_height = height // rows
    
    regions = {}
    for row in range(rows):
        for col in range(cols):
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            
            name = f"cell_{row}_{col}"
            regions[name] = (x1, y1, x2, y2)
    
    return regions


def get_dominant_color(region: Optional[Tuple[int, int, int, int]] = None) -> Tuple[int, int, int]:
    """
    Отримати домінуючий колір області
    
    Args:
        region: Область (x1, y1, x2, y2) або None для всього екрану
    
    Returns:
        Tuple: (R, G, B) колір
    """
    try:
        if region:
            img = screenshot_region(*region)
        else:
            img = ImageGrab.grab()
        
        # Зменшити розмір для швидшого аналізу
        img = img.resize((150, 150))
        
        # Конвертувати до RGB якщо потрібно
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = img.getdata()
        r_total = g_total = b_total = 0
        
        for r, g, b in pixels:
            r_total += r
            g_total += g
            b_total += b
        
        pixel_count = len(pixels)
        return (
            r_total // pixel_count,
            g_total // pixel_count,
            b_total // pixel_count
        )
    except Exception as e:
        print(f"Помилка отримання домінуючого кольору: {e}")
        return (0, 0, 0)


def highlight_region(region: Tuple[int, int, int, int],
                     output_path: str,
                     color: Tuple[int, int, int] = (255, 0, 0),
                     width: int = 3) -> bool:
    """
    Зберегти скріншот з виділеною областю
    
    Args:
        region: Область для виділення (x1, y1, x2, y2)
        output_path: Шлях для збереження
        color: RGB колір для виділення
        width: Товщина лінії
    
    Returns:
        bool: True якщо успішно
    """
    try:
        img = ImageGrab.grab()
        draw = ImageDraw.Draw(img)
        draw.rectangle(region, outline=color, width=width)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        return True
    except Exception as e:
        print(f"Помилка виділення області: {e}")
        return False


def wait_for_screen_change(timeout: int = 30,
                           interval: float = 0.5,
                           threshold: int = 30) -> bool:
    """
    Чекати поки екран змінюється
    
    Args:
        timeout: Максимум секунд для очікування
        interval: Інтервал перевірки в секундах
        threshold: Поріг чутливості зміни
    
    Returns:
        bool: True якщо екран змінився, False якщо timeout
    """
    try:
        baseline = ImageGrab.grab()
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current = ImageGrab.grab()
            has_changes, _, _ = detect_changes(baseline, current, threshold)
            
            if has_changes:
                return True
            
            time.sleep(interval)
        
        return False
    except Exception as e:
        print(f"Помилка очікування зміни екрану: {e}")
        return False


def wait_for_image(template_path: str,
                   timeout: int = 30,
                   interval: float = 0.5,
                   confidence: float = 0.8) -> bool:
    """
    Чекати поки зображення з'явиться на екрані
    
    Args:
        template_path: Шлях до шаблону
        timeout: Максимум секунд
        interval: Інтервал перевірки
        confidence: Поріг впевненості
    
    Returns:
        bool: True якщо знайдено
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if find_image_on_screen(template_path, confidence) is not None:
            return True
        time.sleep(interval)
    
    return False
