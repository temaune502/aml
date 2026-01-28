"""
Console Automation модуль - Автоматизація консолі та виконання команд

Модуль забезпечує інтеграцію з системною консоллю для запуску команд,
обробки виводу, керування процесами та парсингу результатів.

Функції:
    - Запуск команд (CMD, PowerShell, Python)
    - Обробка виводу (stdout, stderr, return code)
    - Парсинг результатів команд
    - Управління процесами (kill, pause, resume)
    - Запуск з контролем часу виконання
    - Real-time обробка виводу
"""

import subprocess
import shlex
import os
import signal
import threading
import time
from typing import Optional, List, Dict, Tuple, Callable, Any
from dataclasses import dataclass
from pathlib import Path
import json
import re


@dataclass
class CommandResult:
    """Результат виконання команди"""
    command: str
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    success: bool
    
    def __str__(self) -> str:
        """Представлення результату"""
        status = "✓ SUCCESS" if self.success else "✗ FAILED"
        return f"{status} | Code: {self.return_code} | Time: {self.execution_time:.2f}s\n{self.stdout}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертувати в словник"""
        return {
            'command': self.command,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'return_code': self.return_code,
            'execution_time': self.execution_time,
            'success': self.success
        }


class ConsoleAutomation:
    """Класс для автоматизації консолі"""
    
    def __init__(self):
        """Ініціалізація"""
        self.processes: Dict[int, subprocess.Popen] = {}
        self.history: List[CommandResult] = []
        self.shell = 'powershell' if os.name == 'nt' else 'bash'
    
    # ============================================================================
    # БАЗОВІ ОПЕРАЦІЇ ЗАПУСКУ
    # ============================================================================
    
    def run_command(
        self,
        command: str,
        shell: Optional[str] = None,
        timeout: Optional[float] = None,
        capture_output: bool = True,
        text: bool = True,
        cwd: Optional[str] = None
    ) -> CommandResult:
        """
        Запустити команду та отримати результат
        
        Args:
            command: Команда для виконання
            shell: Тип shell ('cmd', 'powershell', 'bash')
            timeout: Максимальний час виконання в секундах
            capture_output: Захоплювати stdout/stderr
            text: Конвертувати вивід в текст
            cwd: Робоча директорія
        
        Returns:
            CommandResult: Результат виконання
        """
        start_time = time.time()
        shell_type = shell or self.shell
        
        try:
            # Вибрати правильну команду для shell'а
            if shell_type == 'powershell':
                cmd = ['powershell', '-Command', command]
            elif shell_type == 'cmd':
                cmd = ['cmd', '/c', command]
            else:  # bash
                cmd = ['/bin/bash', '-c', command]
            
            # Запустити процес
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                text=text,
                cwd=cwd
            )
            
            self.processes[process.pid] = process
            
            # Очікувати завершення з timeout'ом
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                stderr = f"[TIMEOUT] Process killed after {timeout}s\n{stderr or ''}"
            
            execution_time = time.time() - start_time
            success = process.returncode == 0
            
            result = CommandResult(
                command=command,
                stdout=stdout or '',
                stderr=stderr or '',
                return_code=process.returncode,
                execution_time=execution_time,
                success=success
            )
            
            self.history.append(result)
            
            if process.pid in self.processes:
                del self.processes[process.pid]
            
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            result = CommandResult(
                command=command,
                stdout='',
                stderr=str(e),
                return_code=-1,
                execution_time=execution_time,
                success=False
            )
            self.history.append(result)
            return result
    
    def run_async(
        self,
        command: str,
        on_output: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        shell: Optional[str] = None
    ) -> subprocess.Popen:
        """
        Запустити команду асинхронно
        
        Args:
            command: Команда для виконання
            on_output: Callback для обробки stdout
            on_error: Callback для обробки stderr
            shell: Тип shell
        
        Returns:
            subprocess.Popen: Процес
        """
        shell_type = shell or self.shell
        
        if shell_type == 'powershell':
            cmd = ['powershell', '-Command', command]
        elif shell_type == 'cmd':
            cmd = ['cmd', '/c', command]
        else:
            cmd = ['/bin/bash', '-c', command]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes[process.pid] = process
        
        # Читати вивід у окремих потоках
        if on_output:
            threading.Thread(
                target=self._read_stream,
                args=(process.stdout, on_output),
                daemon=True
            ).start()
        
        if on_error:
            threading.Thread(
                target=self._read_stream,
                args=(process.stderr, on_error),
                daemon=True
            ).start()
        
        return process
    
    @staticmethod
    def _read_stream(stream, callback: Callable[[str], None]) -> None:
        """Читати потік та викликати callback"""
        for line in iter(stream.readline, ''):
            if line:
                callback(line.rstrip())
    
    # ============================================================================
    # УПРАВЛІННЯ ПРОЦЕСАМИ
    # ============================================================================
    
    def kill_process(self, pid: int) -> bool:
        """
        Завершити процес
        
        Args:
            pid: ID процесу
        
        Returns:
            bool: Успішність операції
        """
        if pid in self.processes:
            try:
                self.processes[pid].kill()
                del self.processes[pid]
                return True
            except:
                return False
        return False
    
    def get_process_info(self, pid: int) -> Dict[str, Any]:
        """
        Отримати інформацію про процес
        
        Args:
            pid: ID процесу
        
        Returns:
            Dict: Інформація про процес
        """
        if pid not in self.processes:
            return {}
        
        process = self.processes[pid]
        return {
            'pid': pid,
            'returncode': process.returncode,
            'is_alive': process.poll() is None
        }
    
    def list_processes(self) -> List[Dict[str, Any]]:
        """
        Отримати список активних процесів
        
        Returns:
            List: Список процесів
        """
        result = []
        for pid, process in list(self.processes.items()):
            if process.poll() is None:
                result.append({
                    'pid': pid,
                    'is_alive': True
                })
            else:
                del self.processes[pid]
        return result
    
    # ============================================================================
    # ПАРСИНГ РЕЗУЛЬТАТІВ
    # ============================================================================
    
    def parse_json_output(self, result: CommandResult) -> Optional[Dict]:
        """
        Спробувати спарсити JSON з виводу
        
        Args:
            result: Результат команди
        
        Returns:
            Dict: Спарсений JSON
        """
        try:
            return json.loads(result.stdout)
        except:
            return None
    
    def parse_lines(self, result: CommandResult) -> List[str]:
        """
        Розділити вивід на рядки
        
        Args:
            result: Результат команди
        
        Returns:
            List: Список рядків
        """
        return result.stdout.strip().split('\n') if result.stdout else []
    
    def parse_csv(self, result: CommandResult, delimiter: str = ',') -> List[List[str]]:
        """
        Спарсити CSV з виводу
        
        Args:
            result: Результат команди
            delimiter: Розділювач колон
        
        Returns:
            List: Рядки CSV
        """
        lines = self.parse_lines(result)
        return [line.split(delimiter) for line in lines]
    
    def parse_table(self, result: CommandResult) -> List[Dict[str, str]]:
        """
        Спарсити таблицю з виводу (перший рядок - заголовки)
        
        Args:
            result: Результат команди
        
        Returns:
            List: Список словників
        """
        lines = self.parse_lines(result)
        if len(lines) < 2:
            return []
        
        # Перший рядок - заголовки
        headers = lines[0].split()
        rows = []
        
        for line in lines[1:]:
            if line.strip():
                values = line.split()
                if len(values) >= len(headers):
                    rows.append(dict(zip(headers, values)))
        
        return rows
    
    def extract_regex(self, result: CommandResult, pattern: str) -> List[str]:
        """
        Витягнути значення за regex паттерном
        
        Args:
            result: Результат команди
            pattern: Regex паттерн
        
        Returns:
            List: Знайдені значення
        """
        return re.findall(pattern, result.stdout, re.MULTILINE)
    
    # ============================================================================
    # УТИЛІТИ
    # ============================================================================
    
    def get_command_history(self, limit: int = 10) -> List[CommandResult]:
        """
        Отримати історію команд
        
        Args:
            limit: Максимальна кількість команд
        
        Returns:
            List: Список результатів
        """
        return self.history[-limit:]
    
    def clear_history(self) -> None:
        """Очистити історію"""
        self.history.clear()
    
    def save_history(self, filepath: str) -> None:
        """
        Зберегти історію в JSON
        
        Args:
            filepath: Шлях до файлу
        """
        data = [cmd.to_dict() for cmd in self.history]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_history(self, filepath: str) -> None:
        """
        Завантажити історію з JSON
        
        Args:
            filepath: Шлях до файлу
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.history = [CommandResult(**item) for item in data]
        except:
            pass


# ============================================================================
# УТИЛІТИ ФУНКЦІЇ
# ============================================================================

def run_cmd(command: str, timeout: Optional[float] = None) -> CommandResult:
    """
    Швидко запустити команду
    
    Args:
        command: Команда
        timeout: Timeout в секундах
    
    Returns:
        CommandResult: Результат
    """
    automation = ConsoleAutomation()
    return automation.run_command(command, timeout=timeout)


def run_powershell(command: str, timeout: Optional[float] = None) -> CommandResult:
    """
    Запустити PowerShell команду
    
    Args:
        command: Команда
        timeout: Timeout в секундах
    
    Returns:
        CommandResult: Результат
    """
    automation = ConsoleAutomation()
    return automation.run_command(command, shell='powershell', timeout=timeout)


def run_python(code: str, timeout: Optional[float] = None) -> CommandResult:
    """
    Запустити Python код
    
    Args:
        code: Python код
        timeout: Timeout в секундах
    
    Returns:
        CommandResult: Результат
    """
    automation = ConsoleAutomation()
    return automation.run_command(f'python -c "{code}"', timeout=timeout)
