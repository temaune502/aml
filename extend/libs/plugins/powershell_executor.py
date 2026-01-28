"""
PowerShell Executor модуль - Спеціалізований виконавець для PowerShell

Модуль забезпечує повну інтеграцію з PowerShell для запуску скриптів,
pipeline команд, роботи з объектами PowerShell та асинхронного виконання.

Функції:
    - Запуск PowerShell скриптів
    - Pipeline команди (Get-Process | Where-Object)
    - Робота з PowerShell об'єктами
    - Асинхронне виконання зі streaming виводом
    - Динамічна генерація скриптів
    - Кешування результатів
"""

import subprocess
import json
import re
import tempfile
import os
from typing import Optional, List, Dict, Any, Callable, Union
from dataclasses import dataclass
from pathlib import Path
import time


@dataclass
class PSResult:
    """Результат виконання PowerShell команди"""
    command: str
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    objects: List[Dict[str, Any]]  # Об'єкти PowerShell
    
    def __str__(self) -> str:
        """Представлення результату"""
        status = "✓" if self.success else "✗"
        return f"{status} PowerShell | {len(self.objects)} objects | {self.execution_time:.2f}s"
    
    def to_json(self) -> str:
        """Конвертувати в JSON"""
        return json.dumps({
            'success': self.success,
            'command': self.command,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'return_code': self.return_code,
            'execution_time': self.execution_time,
            'objects_count': len(self.objects),
            'objects': self.objects
        }, indent=2, ensure_ascii=False)


class PowerShellExecutor:
    """Виконавець PowerShell команд"""
    
    def __init__(self, execution_policy: str = 'Bypass'):
        """
        Ініціалізація
        
        Args:
            execution_policy: Policy для PowerShell (Bypass, Unrestricted, RemoteSigned)
        """
        self.execution_policy = execution_policy
        self.cache: Dict[str, PSResult] = {}
        self.history: List[PSResult] = []
    
    # ============================================================================
    # БАЗОВІ ОПЕРАЦІЇ
    # ============================================================================
    
    def run(
        self,
        command: str,
        use_cache: bool = False,
        convert_json: bool = True,
        timeout: Optional[float] = None
    ) -> PSResult:
        """
        Запустити PowerShell команду
        
        Args:
            command: PowerShell команда
            use_cache: Використовувати кеш
            convert_json: Конвертувати вивід в JSON
            timeout: Timeout в секундах
        
        Returns:
            PSResult: Результат виконання
        """
        # Перевірити кеш
        if use_cache and command in self.cache:
            return self.cache[command]
        
        start_time = time.time()
        
        try:
            # Побудувати PowerShell команду
            ps_cmd = self._build_ps_command(command, convert_json)
            
            # Запустити
            process = subprocess.Popen(
                ['powershell', '-ExecutionPolicy', self.execution_policy, '-Command', ps_cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                stderr = f"[TIMEOUT] Process killed after {timeout}s\n{stderr or ''}"
            
            execution_time = time.time() - start_time
            success = process.returncode == 0
            
            # Спробувати спарсити JSON з виводу
            objects = []
            if success and convert_json:
                objects = self._parse_json_output(stdout)
            
            result = PSResult(
                command=command,
                success=success,
                stdout=stdout,
                stderr=stderr,
                return_code=process.returncode,
                execution_time=execution_time,
                objects=objects
            )
            
            self.history.append(result)
            
            if use_cache:
                self.cache[command] = result
            
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            result = PSResult(
                command=command,
                success=False,
                stdout='',
                stderr=str(e),
                return_code=-1,
                execution_time=execution_time,
                objects=[]
            )
            self.history.append(result)
            return result
    
    def run_script_file(
        self,
        script_path: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> PSResult:
        """
        Запустити PowerShell скрипт з файлу
        
        Args:
            script_path: Шлях до .ps1 файлу
            parameters: Параметри для скрипту
            timeout: Timeout в секундах
        
        Returns:
            PSResult: Результат
        """
        if not os.path.exists(script_path):
            return PSResult(
                command=f"&'{script_path}'",
                success=False,
                stdout='',
                stderr=f"Файл не знайдено: {script_path}",
                return_code=-1,
                execution_time=0,
                objects=[]
            )
        
        # Побудувати команду з параметрами
        cmd = f"& '{script_path}'"
        if parameters:
            param_str = ' '.join([f'-{k} "{v}"' for k, v in parameters.items()])
            cmd += f' {param_str}'
        
        return self.run(cmd, timeout=timeout)
    
    def run_script_inline(
        self,
        script: str,
        timeout: Optional[float] = None
    ) -> PSResult:
        """
        Запустити inline PowerShell скрипт
        
        Args:
            script: PowerShell скрипт
            timeout: Timeout в секундах
        
        Returns:
            PSResult: Результат
        """
        # Екранувати спеціальні символи
        escaped_script = script.replace('"', '""')
        return self.run(f'{escaped_script}', timeout=timeout)
    
    # ============================================================================
    # PIPELINE ОПЕРАЦІЇ
    # ============================================================================
    
    def pipeline(self, *commands: str) -> PSResult:
        """
        Запустити pipeline команди
        
        Args:
            commands: Послідовність команд
        
        Returns:
            PSResult: Результат
        """
        pipeline_cmd = ' | '.join(commands)
        return self.run(pipeline_cmd, convert_json=True)
    
    def get_objects(
        self,
        object_type: str,
        filter_expr: Optional[str] = None,
        sort_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> PSResult:
        """
        Отримати об'єкти PowerShell
        
        Args:
            object_type: Тип об'єкту (Process, Service, Item)
            filter_expr: Вираз фільтру
            sort_by: Поле для сортування
            limit: Ліміт результатів
        
        Returns:
            PSResult: Результат з об'єктами
        """
        cmd = f'Get-{object_type}'
        
        if filter_expr:
            cmd += f' | Where-Object {{{filter_expr}}}'
        
        if sort_by:
            cmd += f' | Sort-Object {sort_by}'
        
        if limit:
            cmd += f' | Select-Object -First {limit}'
        
        # Конвертувати в JSON для ліпшої обробки
        cmd += ' | ConvertTo-Json -Depth 3'
        
        return self.run(cmd, convert_json=False)
    
    # ============================================================================
    # РОБОТИ З ПРОЦЕСАМИ
    # ============================================================================
    
    def get_processes(self, name_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Отримати список процесів
        
        Args:
            name_filter: Фільтр по імені процесу
        
        Returns:
            List: Список процесів
        """
        cmd = 'Get-Process'
        if name_filter:
            cmd += f" -Name '*{name_filter}*' -ErrorAction SilentlyContinue"
        cmd += ' | ConvertTo-Json -Depth 2'
        
        result = self.run(cmd, convert_json=False)
        if result.success:
            try:
                data = json.loads(result.stdout)
                return data if isinstance(data, list) else [data]
            except:
                return []
        return []
    
    def stop_process(self, process_name: str, force: bool = False) -> PSResult:
        """
        Зупинити процес
        
        Args:
            process_name: Ім'я процесу
            force: Примусова зупинка
        
        Returns:
            PSResult: Результат
        """
        force_flag = ' -Force' if force else ''
        cmd = f"Stop-Process -Name '{process_name}'{force_flag} -ErrorAction SilentlyContinue"
        return self.run(cmd)
    
    # ============================================================================
    # РОБОТИ З ФАЙЛОВОЮ СИСТЕМОЮ
    # ============================================================================
    
    def get_files(
        self,
        path: str,
        filter_expr: Optional[str] = None,
        recurse: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Отримати список файлів
        
        Args:
            path: Шлях до папки
            filter_expr: Фільтр (*.txt)
            recurse: Рекурсивно
        
        Returns:
            List: Список файлів
        """
        recurse_flag = ' -Recurse' if recurse else ''
        filter_flag = f' -Filter "{filter_expr}"' if filter_expr else ''
        
        cmd = f'Get-ChildItem -Path "{path}"{filter_flag}{recurse_flag} | ConvertTo-Json -Depth 2'
        result = self.run(cmd, convert_json=False)
        
        if result.success:
            try:
                data = json.loads(result.stdout)
                return data if isinstance(data, list) else [data]
            except:
                return []
        return []
    
    def create_file(self, path: str, content: str = '') -> PSResult:
        """
        Створити файл
        
        Args:
            path: Шлях до файлу
            content: Вміст файлу
        
        Returns:
            PSResult: Результат
        """
        # Екранувати лапки
        safe_content = content.replace('"', '`"')
        cmd = f'"{safe_content}" | Out-File -FilePath "{path}" -Encoding UTF8'
        return self.run(cmd)
    
    def read_file(self, path: str, encoding: str = 'UTF8') -> str:
        """
        Прочитати файл
        
        Args:
            path: Шлях до файлу
            encoding: Кодування
        
        Returns:
            str: Вміст файлу
        """
        cmd = f'Get-Content -Path "{path}" -Encoding {encoding} -Raw'
        result = self.run(cmd)
        return result.stdout if result.success else ''
    
    # ============================================================================
    # РОБОТИ З РЕЄСТРОМ
    # ============================================================================
    
    def get_registry_value(self, path: str, name: str) -> Optional[str]:
        """
        Отримати значення з реєстру
        
        Args:
            path: Шлях в реєстрі
            name: Ім'я значення
        
        Returns:
            str: Значення
        """
        cmd = f'(Get-ItemProperty -Path "{path}" -Name "{name}" -ErrorAction SilentlyContinue)."{name}"'
        result = self.run(cmd)
        return result.stdout.strip() if result.success else None
    
    def set_registry_value(self, path: str, name: str, value: str, type_name: str = 'String') -> PSResult:
        """
        Встановити значення в реєстрі
        
        Args:
            path: Шлях в реєстрі
            name: Ім'я значення
            value: Значення
            type_name: Тип (String, DWORD, etc)
        
        Returns:
            PSResult: Результат
        """
        cmd = f'Set-ItemProperty -Path "{path}" -Name "{name}" -Value "{value}" -Type {type_name}'
        return self.run(cmd)
    
    # ============================================================================
    # УТИЛІТИ
    # ============================================================================
    
    def _build_ps_command(self, command: str, convert_json: bool = True) -> str:
        """Побудувати PowerShell команду з додатковими параметрами"""
        if convert_json and not ' | ConvertTo-Json' in command:
            return command + ' | ConvertTo-Json -Depth 5 -Compress'
        return command
    
    def _parse_json_output(self, output: str) -> List[Dict[str, Any]]:
        """Спарсити JSON з виводу"""
        try:
            data = json.loads(output)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            return []
        except:
            return []
    
    def clear_cache(self) -> None:
        """Очистити кеш"""
        self.cache.clear()
    
    def get_history(self, limit: int = 10) -> List[PSResult]:
        """
        Отримати історію команд
        
        Args:
            limit: Максимальна кількість
        
        Returns:
            List: Історія
        """
        return self.history[-limit:]
    
    def save_history(self, filepath: str) -> None:
        """
        Зберегти історію в JSON
        
        Args:
            filepath: Шлях до файлу
        """
        data = [
            {
                'command': item.command,
                'success': item.success,
                'return_code': item.return_code,
                'execution_time': item.execution_time
            }
            for item in self.history
        ]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================================
# УТИЛІТИ ФУНКЦІЇ
# ============================================================================

def ps_run(command: str, timeout: Optional[float] = None) -> PSResult:
    """
    Швидко запустити PowerShell команду
    
    Args:
        command: PowerShell команда
        timeout: Timeout в секундах
    
    Returns:
        PSResult: Результат
    """
    executor = PowerShellExecutor()
    return executor.run(command, timeout=timeout)


def ps_get_processes() -> List[Dict[str, Any]]:
    """
    Отримати список активних процесів
    
    Returns:
        List: Список процесів
    """
    executor = PowerShellExecutor()
    return executor.get_processes()


def ps_stop_process(name: str, force: bool = False) -> bool:
    """
    Зупинити процес
    
    Args:
        name: Ім'я процесу
        force: Примусова зупинка
    
    Returns:
        bool: Успіх
    """
    executor = PowerShellExecutor()
    result = executor.stop_process(name, force)
    return result.success
