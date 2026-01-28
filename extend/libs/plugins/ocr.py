"""
OCR модуль для розпізнавання тексту з екрану

Модуль забезпечує розпізнавання тексту з екрану та зображень за допомогою
Tesseract OCR та обробку зображень за допомогою PIL/Pillow.

Функції:
    - Читання тексту з екрану
    - Читання тексту з файлу зображення
    - Розпізнавання областей на екрані
    - Аналіз кольорів пікселів
    - Пошук тексту на екрані
"""

import os
import sys
from PIL import Image, ImageGrab, ImageDraw, ImageFilter
from typing import Tuple, List, Dict, Optional
import pytesseract
from pathlib import Path
import time

# Спроба встановити шлях до tesseract
try:
    if os.name == 'nt':  # Windows
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.pytesseract_cmd = path
                break
except Exception:
    pass


def screenshot(region: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
    """
    Зробити скріншот частини або всього екрану
    
    Args:
        region: Кортеж (x1, y1, x2, y2) для частини екрану або None для всього
    
    Returns:
        Image: PIL Image об'єкт зі скріншотом
    """
    if region:
        return ImageGrab.grab(bbox=region)
    return ImageGrab.grab()


def read_text_from_screen(region: Optional[Tuple[int, int, int, int]] = None,
                          lang: str = 'ukr',
                          config: str = '') -> str:
    """
    Прочитати текст з екрану за допомогою OCR
    
    Args:
        region: Область екрану (x1, y1, x2, y2) або None для всього
        lang: Мова ('ukr' для української, 'eng' для англійської)
        config: Додаткова конфігурація tesseract
    
    Returns:
        str: Розпізнаний текст
    """
    try:
        img = screenshot(region)
        text = pytesseract.image_to_string(img, lang=lang, config=config)
        return text.strip()
    except Exception as e:
        print(f"Помилка OCR: {e}")
        return ""


def read_text_from_image(image_path: str,
                         lang: str = 'ukr',
                         config: str = '') -> str:
    """
    Прочитати текст з файлу зображення
    
    Args:
        image_path: Шлях до файлу зображення
        lang: Мова для розпізнавання
        config: Конфігурація tesseract
    
    Returns:
        str: Розпізнаний текст
    """
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Файл не знайдено: {image_path}")
        
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=lang, config=config)
        return text.strip()
    except Exception as e:
        print(f"Помилка читання з зображення: {e}")
        return ""


def get_text_boxes(region: Optional[Tuple[int, int, int, int]] = None,
                   lang: str = 'ukr') -> List[Dict]:
    """
    Отримати координати текстових блоків на екрані
    
    Args:
        region: Область екрану або None
        lang: Мова для розпізнавання
    
    Returns:
        List[Dict]: Список словників з ключами:
                   - 'text': текст
                   - 'x': x координата
                   - 'y': y координата
                   - 'w': ширина
                   - 'h': висота
                   - 'conf': впевненість (0-100)
    """
    try:
        img = screenshot(region)
        data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
        
        boxes = []
        for i, text in enumerate(data['text']):
            if text.strip():
                boxes.append({
                    'text': text,
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'w': data['width'][i],
                    'h': data['height'][i],
                    'conf': data['conf'][i]
                })
        return boxes
    except Exception as e:
        print(f"Помилка отримання текстових блоків: {e}")
        return []


def find_text_on_screen(text: str,
                        region: Optional[Tuple[int, int, int, int]] = None,
                        lang: str = 'ukr') -> Optional[Tuple[int, int, int, int]]:
    """
    Знайти текст на екрані та повернути його координати
    
    Args:
        text: Текст для пошуку
        region: Область пошуку або None
        lang: Мова для розпізнавання
    
    Returns:
        Tuple: (x, y, w, h) координати знайденого тексту або None
    """
    boxes = get_text_boxes(region, lang)
    
    for box in boxes:
        if text.lower() in box['text'].lower():
            return (box['x'], box['y'], box['w'], box['h'])
    
    return None


def get_pixel_color(x: int, y: int) -> Tuple[int, int, int]:
    """
    Отримати RGB колір пікселя на координатах
    
    Args:
        x: X координата
        y: Y координата
    
    Returns:
        Tuple: (R, G, B) значення (0-255)
    """
    try:
        img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
        pixel = img.load()
        return pixel[0, 0][:3]
    except Exception as e:
        print(f"Помилка отримання кольору: {e}")
        return (0, 0, 0)


def find_color_on_screen(color: Tuple[int, int, int],
                         threshold: int = 10,
                         region: Optional[Tuple[int, int, int, int]] = None) -> List[Tuple[int, int]]:
    """
    Знайти всі пікселі певного кольору на екрані
    
    Args:
        color: RGB колір (R, G, B)
        threshold: Поріг відмінності кольорів (0-255)
        region: Область пошуку або None
    
    Returns:
        List[Tuple]: Список координат (x, y) знайдених пікселів
    """
    try:
        img = screenshot(region)
        pixels = img.load()
        width, height = img.size
        
        matches = []
        r, g, b = color
        
        for y in range(height):
            for x in range(width):
                pixel = pixels[x, y]
                pr, pg, pb = pixel[:3]
                
                if (abs(pr - r) <= threshold and
                    abs(pg - g) <= threshold and
                    abs(pb - b) <= threshold):
                    
                    offset_x = region[0] if region else 0
                    offset_y = region[1] if region else 0
                    matches.append((x + offset_x, y + offset_y))
        
        return matches
    except Exception as e:
        print(f"Помилка пошуку кольору: {e}")
        return []


def preprocess_image(image_path: str,
                     enhance_contrast: bool = True,
                     enhance_sharpness: bool = True,
                     denoise: bool = True) -> Image.Image:
    """
    Попередня обробка зображення для поліпшення OCR
    
    Args:
        image_path: Шлях до зображення
        enhance_contrast: Посилити контраст
        enhance_sharpness: Посилити чіткість
        denoise: Зменшити шум
    
    Returns:
        Image: Оброблене зображення
    """
    try:
        img = Image.open(image_path)
        
        # Конвертування в RGB якщо потрібно
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if enhance_contrast:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
        
        if enhance_sharpness:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
        
        if denoise:
            img = img.filter(ImageFilter.MedianFilter(size=3))
        
        return img
    except Exception as e:
        print(f"Помилка обробки зображення: {e}")
        return None


def save_screenshot(filepath: str,
                    region: Optional[Tuple[int, int, int, int]] = None) -> bool:
    """
    Зберегти скріншот у файл
    
    Args:
        filepath: Шлях для збереження
        region: Область скріншота або None
    
    Returns:
        bool: True якщо успішно, False якщо помилка
    """
    try:
        img = screenshot(region)
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        img.save(filepath)
        return True
    except Exception as e:
        print(f"Помилка збереження скріншота: {e}")
        return False


def highlight_text_boxes(image_path: str,
                         output_path: str,
                         lang: str = 'ukr') -> bool:
    """
    Зберегти зображення з виділеними текстовими блоками
    
    Args:
        image_path: Шлях до вихідного зображення
        output_path: Шлях для збереження з виділеннями
        lang: Мова для розпізнавання
    
    Returns:
        bool: True якщо успішно
    """
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
        
        for i, text in enumerate(data['text']):
            if text.strip():
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                
                draw.rectangle([x, y, x+w, y+h], outline='red', width=2)
        
        img.save(output_path)
        return True
    except Exception as e:
        print(f"Помилка виділення текстових блоків: {e}")
        return False


def wait_for_text(text: str,
                  timeout: int = 30,
                  interval: float = 0.5,
                  lang: str = 'ukr') -> bool:
    """
    Чекати поки текст з'явиться на екрані
    
    Args:
        text: Текст для пошуку
        timeout: Максимум секунд для очікування
        interval: Інтервал перевірки в секундах
        lang: Мова для розпізнавання
    
    Returns:
        bool: True якщо знайдено, False якщо timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        screen_text = read_text_from_screen(lang=lang)
        if text.lower() in screen_text.lower():
            return True
        time.sleep(interval)
    
    return False


def extract_region_text(x1: int, y1: int, x2: int, y2: int,
                       lang: str = 'ukr') -> str:
    """
    Прочитати текст з прямокутної область екрану
    
    Args:
        x1, y1: Верхній лівий кут
        x2, y2: Нижній правий кут
        lang: Мова для розпізнавання
    
    Returns:
        str: Розпізнаний текст
    """
    return read_text_from_screen(region=(x1, y1, x2, y2), lang=lang)
