"""
Windows Automation модуль - Автоматизація Windows операцій

Модуль забезпечує керування Windows-специфічними операціями,
включаючи роботу з реєстром, сервісами, завданнями та вікнами.

Функції:
    - Управління Windows сервісами
    - Робота з реєстром (читання, запис, видалення)
    - Планування завдань (Task Scheduler)
    - Керування вікнами
    - Отримання інформації про систему
    - Контроль живлення системи
"""

import subprocess
import json
import winreg
import os
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class ServiceStatus(Enum):
    """Статуси сервісу"""
    RUNNING = "Running"
    STOPPED = "Stopped"
    PAUSED = "Paused"


class WindowsAutomation:
    """Клас для автоматизації Windows операцій"""
    
    # ============================================================================
    # РОБОТИ З СЕРВІСАМИ
    # ============================================================================
    
    @staticmethod
    def get_services(name_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Отримати список сервісів
        
        Args:
            name_filter: Фільтр по імені сервісу
        
        Returns:
            List: Список сервісів з інформацією
        """
        cmd = 'Get-Service'
        if name_filter:
            cmd += f" -Name '*{name_filter}*' -ErrorAction SilentlyContinue"
        cmd += ' | ConvertTo-Json -Depth 2'
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    return data if isinstance(data, list) else [data]
                except:
                    return []
        except:
            pass
        
        return []
    
    @staticmethod
    def get_service_status(name: str) -> Optional[ServiceStatus]:
        """
        Отримати статус сервісу
        
        Args:
            name: Ім'я сервісу
        
        Returns:
            ServiceStatus: Статус сервісу
        """
        services = WindowsAutomation.get_services(name)
        if services and services[0].get('Status'):
            status_str = services[0]['Status']
            try:
                return ServiceStatus(status_str)
            except:
                return None
        return None
    
    @staticmethod
    def start_service(name: str) -> bool:
        """
        Запустити сервіс
        
        Args:
            name: Ім'я сервісу
        
        Returns:
            bool: Успіх
        """
        cmd = f'Start-Service -Name "{name}" -ErrorAction SilentlyContinue'
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def stop_service(name: str) -> bool:
        """
        Зупинити сервіс
        
        Args:
            name: Ім'я сервісу
        
        Returns:
            bool: Успіх
        """
        cmd = f'Stop-Service -Name "{name}" -Force -ErrorAction SilentlyContinue'
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def restart_service(name: str) -> bool:
        """
        Перезапустити сервіс
        
        Args:
            name: Ім'я сервісу
        
        Returns:
            bool: Успіх
        """
        return WindowsAutomation.stop_service(name) and WindowsAutomation.start_service(name)
    
    # ============================================================================
    # РОБОТИ З РЕЄСТРОМ
    # ============================================================================
    
    @staticmethod
    def registry_read(path: str, value: str) -> Optional[Any]:
        """
        Прочитати значення з реєстру
        
        Args:
            path: Шлях в реєстрі (наприклад: HKEY_LOCAL_MACHINE\\Software\\Microsoft)
            value: Ім'я значення
        
        Returns:
            Any: Значення з реєстру
        """
        try:
            # Розпарсити шлях
            parts = path.split('\\')
            hkey_str = parts[0]
            subkey = '\\'.join(parts[1:])
            
            #映射 hkey
            hkey_map = {
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                'HKEY_USERS': winreg.HKEY_USERS,
                'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG,
            }
            
            hkey = hkey_map.get(hkey_str)
            if not hkey:
                return None
            
            with winreg.OpenKey(hkey, subkey, access=winreg.KEY_READ) as key:
                value_data, _ = winreg.QueryValueEx(key, value)
                return value_data
        except Exception as e:
            return None
    
    @staticmethod
    def registry_write(path: str, value: str, data: Any, type_name: str = 'String') -> bool:
        """
        Записати значення в реєстр
        
        Args:
            path: Шлях в реєстрі
            value: Ім'я значення
            data: Дані для запису
            type_name: Тип (String, DWORD, Binary)
        
        Returns:
            bool: Успіх
        """
        try:
            parts = path.split('\\')
            hkey_str = parts[0]
            subkey = '\\'.join(parts[1:])
            
            hkey_map = {
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                'HKEY_USERS': winreg.HKEY_USERS,
                'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG,
            }
            
            hkey = hkey_map.get(hkey_str)
            if not hkey:
                return False
            
            # Маппинг типів
            type_map = {
                'String': winreg.REG_SZ,
                'DWORD': winreg.REG_DWORD,
                'Binary': winreg.REG_BINARY,
                'ExpandString': winreg.REG_EXPAND_SZ,
                'MultiString': winreg.REG_MULTI_SZ,
            }
            
            reg_type = type_map.get(type_name, winreg.REG_SZ)
            
            with winreg.CreateKey(hkey, subkey) as key:
                winreg.SetValueEx(key, value, 0, reg_type, data)
                return True
        except:
            return False
    
    @staticmethod
    def registry_delete(path: str, value: Optional[str] = None) -> bool:
        """
        Видалити значення або ключ з реєстру
        
        Args:
            path: Шлях в реєстрі
            value: Ім'я значення (None = видалити весь ключ)
        
        Returns:
            bool: Успіх
        """
        try:
            parts = path.split('\\')
            hkey_str = parts[0]
            subkey = '\\'.join(parts[1:])
            
            hkey_map = {
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                'HKEY_USERS': winreg.HKEY_USERS,
                'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG,
            }
            
            hkey = hkey_map.get(hkey_str)
            if not hkey:
                return False
            
            if value:
                # Видалити значення
                with winreg.OpenKey(hkey, subkey, access=winreg.KEY_WRITE) as key:
                    winreg.DeleteValue(key, value)
            else:
                # Видалити ключ
                winreg.DeleteKey(hkey, subkey)
            
            return True
        except:
            return False
    
    # ============================================================================
    # КЕРУВАННЯ ЗАВДАННЯМИ
    # ============================================================================
    
    @staticmethod
    def create_task(
        name: str,
        trigger: str,
        action: str,
        enabled: bool = True,
        description: str = ''
    ) -> bool:
        """
        Створити заплановане завдання
        
        Args:
            name: Ім'я завдання
            trigger: Тригер (OnStartup, OnLogon, Daily, Hourly)
            action: Дія (повна команда)
            enabled: Чи включено завдання
            description: Опис завдання
        
        Returns:
            bool: Успіх
        """
        cmd = (
            f'$trigger = New-ScheduledTaskTrigger -{trigger}; '
            f'$action = New-ScheduledTaskAction -Execute "powershell.exe" '
            f'-Argument "-NoProfile -WindowStyle Hidden -Command {action}"; '
            f'Register-ScheduledTask -TaskName "{name}" -Trigger $trigger '
            f'-Action $action -Description "{description}" -Force'
        )
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def delete_task(name: str) -> bool:
        """
        Видалити заплановане завдання
        
        Args:
            name: Ім'я завдання
        
        Returns:
            bool: Успіх
        """
        cmd = f'Unregister-ScheduledTask -TaskName "{name}" -Confirm:$false'
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def get_tasks() -> List[Dict[str, str]]:
        """
        Отримати список запланованих завдань
        
        Returns:
            List: Список завдань
        """
        cmd = 'Get-ScheduledTask | ConvertTo-Json -Depth 2'
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    return data if isinstance(data, list) else [data]
                except:
                    return []
        except:
            pass
        
        return []
    
    # ============================================================================
    # КЕРУВАННЯ ВІКНАМИ
    # ============================================================================
    
    @staticmethod
    def get_windows() -> List[Dict[str, Any]]:
        """
        Отримати список відкритих вікон
        
        Returns:
            List: Вікна
        """
        try:
            import pygetwindow as gw
            windows = []
            for win in gw.getWindowsWithTitle(''):
                windows.append({
                    'title': win.title,
                    'x': win.left,
                    'y': win.top,
                    'width': win.width,
                    'height': win.height,
                    'is_active': win.isActive if hasattr(win, 'isActive') else False
                })
            return windows
        except:
            # Fallback до PowerShell
            cmd = 'Get-Process | Where-Object {$_.MainWindowTitle} | ConvertTo-Json -Depth 2'
            try:
                result = subprocess.run(
                    ['powershell', '-Command', cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    return data if isinstance(data, list) else [data]
            except:
                pass
            return []
    
    # ============================================================================
    # СИСТЕМНА ІНФОРМАЦІЯ
    # ============================================================================
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        Отримати інформацію про систему
        
        Returns:
            Dict: Інформація про систему
        """
        cmd = (
            'Get-WmiObject -Class Win32_ComputerSystem | '
            'Select-Object Name, Manufacturer, Model, @{N="RAM_GB";E={[math]::Round($_.TotalPhysicalMemory/1GB)}} | '
            'ConvertTo-Json'
        )
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except:
                    return {}
        except:
            pass
        
        return {}
    
    @staticmethod
    def get_windows_info() -> Dict[str, str]:
        """
        Отримати інформацію про Windows версію
        
        Returns:
            Dict: Інформація про Windows
        """
        cmd = (
            'Get-WmiObject -Class Win32_OperatingSystem | '
            'Select-Object Caption, Version, BuildNumber | ConvertTo-Json'
        )
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except:
                    return {}
        except:
            pass
        
        return {}
    
    # ============================================================================
    # КОНТРОЛЬ ЖИВЛЕННЯ
    # ============================================================================
    
    @staticmethod
    def shutdown(delay_seconds: int = 0, message: str = '') -> bool:
        """
        Вимкнути комп'ютер
        
        Args:
            delay_seconds: Затримка перед вимкненням
            message: Повідомлення для користувачів
        
        Returns:
            bool: Успіх
        """
        cmd = f'Stop-Computer -ComputerName localhost -Force'
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def restart(delay_seconds: int = 0) -> bool:
        """
        Перезавантажити комп'ютер
        
        Args:
            delay_seconds: Затримка перед перезавантаженням
        
        Returns:
            bool: Успіх
        """
        cmd = f'Restart-Computer -ComputerName localhost -Force'
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def sleep() -> bool:
        """
        Перевести комп'ютер у режим сну
        
        Returns:
            bool: Успіх
        """
        cmd = 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0'
        
        try:
            subprocess.run(cmd, shell=True, timeout=5)
            return True
        except:
            return False


# ============================================================================
# УТИЛІТИ ФУНКЦІЇ
# ============================================================================

def get_service_status(name: str) -> Optional[str]:
    """
    Отримати статус сервісу
    
    Args:
        name: Ім'я сервісу
    
    Returns:
        str: Статус (Running, Stopped, etc)
    """
    status = WindowsAutomation.get_service_status(name)
    return status.value if status else None


def start_service(name: str) -> bool:
    """Запустити сервіс"""
    return WindowsAutomation.start_service(name)


def stop_service(name: str) -> bool:
    """Зупинити сервіс"""
    return WindowsAutomation.stop_service(name)


def get_system_info() -> Dict[str, Any]:
    """Отримати інформацію про систему"""
    return WindowsAutomation.get_system_info()
