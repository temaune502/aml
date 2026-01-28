"""
System Monitor модуль - Моніторинг системних ресурсів та процесів

Модуль забезпечує отримання інформації про стан системи, включаючи
CPU, пам'ять, диск, мережу, процеси та сервіси Windows.

Функції:
    - Моніторинг CPU, RAM, диску
    - Інформація про мережеві з'єднання
    - Список активних процесів
    - Управління Windows сервісами
    - Алерти при перевищенні порогів
    - Логування метрик
"""

import psutil
import json
import time
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime


@dataclass
class SystemMetrics:
    """Метрики системи"""
    timestamp: str
    cpu_percent: float
    cpu_count: int
    cpu_freq: float
    memory_total: int
    memory_available: int
    memory_percent: float
    disk_total: int
    disk_used: int
    disk_percent: float
    swap_total: int
    swap_used: int
    swap_percent: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертувати в словник"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Конвертувати в JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def __str__(self) -> str:
        """Представлення"""
        return (
            f"CPU: {self.cpu_percent}% | "
            f"RAM: {self.memory_percent}% ({self._format_bytes(self.memory_available)}) | "
            f"DISK: {self.disk_percent}% ({self._format_bytes(self.disk_total - self.disk_used)} free)"
        )
    
    @staticmethod
    def _format_bytes(bytes_val: int) -> str:
        """Форматувати байти"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f}PB"


@dataclass
class ProcessInfo:
    """Інформація про процес"""
    pid: int
    name: str
    status: str
    create_time: float
    memory_percent: float
    cpu_percent: float
    num_threads: int
    cmdline: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертувати в словник"""
        return asdict(self)
    
    def __str__(self) -> str:
        """Представлення"""
        return f"{self.name} (PID: {self.pid}) | CPU: {self.cpu_percent}% | RAM: {self.memory_percent}%"


class SystemMonitor:
    """Монітор системних ресурсів"""
    
    def __init__(self, alert_threshold: Optional[Dict[str, float]] = None):
        """
        Ініціалізація
        
        Args:
            alert_threshold: Пороги для алертів
                Приклад: {'cpu': 80, 'memory': 85, 'disk': 90}
        """
        self.alert_threshold = alert_threshold or {
            'cpu': 80,
            'memory': 85,
            'disk': 90
        }
        self.metrics_history: List[SystemMetrics] = []
        self.alerts: List[Dict[str, Any]] = []
    
    # ============================================================================
    # ОСНОВНІ МЕТРИКИ
    # ============================================================================
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """
        Отримати інформацію про CPU
        
        Returns:
            Dict: Інформація про CPU
        """
        freq = psutil.cpu_freq()
        return {
            'count_physical': psutil.cpu_count(logical=False),
            'count_logical': psutil.cpu_count(logical=True),
            'percent': psutil.cpu_percent(interval=1),
            'percent_per_core': psutil.cpu_percent(interval=1, percpu=True),
            'frequency_current': freq.current if freq else None,
            'frequency_min': freq.min if freq else None,
            'frequency_max': freq.max if freq else None
        }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Отримати інформацію про пам'ять
        
        Returns:
            Dict: Інформація про пам'ять
        """
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_free': swap.free,
            'swap_percent': swap.percent
        }
    
    def get_disk_info(self, path: str = '/') -> Dict[str, Any]:
        """
        Отримати інформацію про диск
        
        Args:
            path: Шлях до диску (C:, D:, тощо)
        
        Returns:
            Dict: Інформація про диск
        """
        try:
            disk = psutil.disk_usage(path)
            return {
                'path': path,
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
        except:
            return {}
    
    def get_all_disks(self) -> List[Dict[str, Any]]:
        """
        Отримати інформацію про всі диски
        
        Returns:
            List: Інформація про диски
        """
        disks = []
        for partition in psutil.disk_partitions():
            try:
                disk_info = self.get_disk_info(partition.mountpoint)
                if disk_info:
                    disk_info['device'] = partition.device
                    disks.append(disk_info)
            except:
                pass
        return disks
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Отримати інформацію про мережу
        
        Returns:
            Dict: Інформація про мережу
        """
        try:
            if_addrs = psutil.net_if_addrs()
            if_stats = psutil.net_if_stats()
            net_io = psutil.net_io_counters()
            
            interfaces = {}
            for interface_name, interface_addrs in if_addrs.items():
                interfaces[interface_name] = {
                    'addresses': [
                        {
                            'family': str(addr.family),
                            'address': addr.address,
                            'netmask': addr.netmask,
                            'broadcast': addr.broadcast
                        }
                        for addr in interface_addrs
                    ],
                    'is_up': if_stats[interface_name].isup if interface_name in if_stats else None,
                    'speed': if_stats[interface_name].speed if interface_name in if_stats else None
                }
            
            return {
                'interfaces': interfaces,
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout
            }
        except:
            return {}
    
    # ============================================================================
    # МЕТРИКИ СИСТЕМИ
    # ============================================================================
    
    def get_system_metrics(self) -> SystemMetrics:
        """
        Отримати всі системні метрики
        
        Returns:
            SystemMetrics: Об'єкт з метриками
        """
        cpu_info = self.get_cpu_info()
        mem_info = self.get_memory_info()
        disk_info = self.get_disk_info('C:\\' if self.get_all_disks() else '/')
        
        metrics = SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_info['percent'],
            cpu_count=cpu_info['count_logical'],
            cpu_freq=cpu_info['frequency_current'] or 0,
            memory_total=mem_info['total'],
            memory_available=mem_info['available'],
            memory_percent=mem_info['percent'],
            disk_total=disk_info.get('total', 0),
            disk_used=disk_info.get('used', 0),
            disk_percent=disk_info.get('percent', 0),
            swap_total=mem_info['swap_total'],
            swap_used=mem_info['swap_used'],
            swap_percent=mem_info['swap_percent']
        )
        
        self.metrics_history.append(metrics)
        self._check_alerts(metrics)
        
        return metrics
    
    def _check_alerts(self, metrics: SystemMetrics) -> None:
        """Перевірити пороги алертів"""
        if metrics.cpu_percent > self.alert_threshold['cpu']:
            self.alerts.append({
                'timestamp': metrics.timestamp,
                'type': 'cpu',
                'value': metrics.cpu_percent,
                'threshold': self.alert_threshold['cpu'],
                'message': f"CPU высокий: {metrics.cpu_percent}%"
            })
        
        if metrics.memory_percent > self.alert_threshold['memory']:
            self.alerts.append({
                'timestamp': metrics.timestamp,
                'type': 'memory',
                'value': metrics.memory_percent,
                'threshold': self.alert_threshold['memory'],
                'message': f"Пам'ять висока: {metrics.memory_percent}%"
            })
        
        if metrics.disk_percent > self.alert_threshold['disk']:
            self.alerts.append({
                'timestamp': metrics.timestamp,
                'type': 'disk',
                'value': metrics.disk_percent,
                'threshold': self.alert_threshold['disk'],
                'message': f"Диск переповнений: {metrics.disk_percent}%"
            })
    
    # ============================================================================
    # ПРОЦЕСИ
    # ============================================================================
    
    def get_processes(
        self,
        sort_by: str = 'memory_percent',
        limit: int = 10
    ) -> List[ProcessInfo]:
        """
        Отримати топ процесів
        
        Args:
            sort_by: Поле для сортування (memory_percent, cpu_percent, name)
            limit: Максимальна кількість процесів
        
        Returns:
            List: Список процесів
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'create_time', 'memory_percent', 'cpu_percent', 'num_threads']):
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'status', 'create_time', 'memory_percent', 'cpu_percent', 'num_threads'])
                
                try:
                    cmdline = ' '.join(proc.cmdline())
                except:
                    cmdline = ''
                
                processes.append(ProcessInfo(
                    pid=pinfo['pid'],
                    name=pinfo['name'],
                    status=pinfo['status'],
                    create_time=pinfo['create_time'],
                    memory_percent=pinfo['memory_percent'] or 0,
                    cpu_percent=pinfo['cpu_percent'] or 0,
                    num_threads=pinfo['num_threads'],
                    cmdline=cmdline
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Сортувати та ліміт
        if sort_by == 'memory_percent':
            processes.sort(key=lambda x: x.memory_percent, reverse=True)
        elif sort_by == 'cpu_percent':
            processes.sort(key=lambda x: x.cpu_percent, reverse=True)
        elif sort_by == 'name':
            processes.sort(key=lambda x: x.name)
        
        return processes[:limit]
    
    def find_process(self, name: str) -> Optional[ProcessInfo]:
        """
        Знайти процес по імені
        
        Args:
            name: Ім'я процесу
        
        Returns:
            ProcessInfo: Інформація про процес
        """
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == name.lower():
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'status', 'create_time', 'memory_percent', 'cpu_percent', 'num_threads'])
                    return ProcessInfo(
                        pid=pinfo['pid'],
                        name=pinfo['name'],
                        status=pinfo['status'],
                        create_time=pinfo['create_time'],
                        memory_percent=pinfo['memory_percent'] or 0,
                        cpu_percent=pinfo['cpu_percent'] or 0,
                        num_threads=pinfo['num_threads'],
                        cmdline=''
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return None
    
    def kill_process(self, pid: int) -> bool:
        """
        Завершити процес
        
        Args:
            pid: ID процесу
        
        Returns:
            bool: Успіх
        """
        try:
            proc = psutil.Process(pid)
            proc.kill()
            return True
        except:
            return False
    
    # ============================================================================
    # УТИЛІТИ
    # ============================================================================
    
    def get_metrics_history(self, limit: int = 100) -> List[SystemMetrics]:
        """
        Отримати історію метрик
        
        Args:
            limit: Максимальна кількість записів
        
        Returns:
            List: Історія метрик
        """
        return self.metrics_history[-limit:]
    
    def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Отримати алерти
        
        Args:
            limit: Максимальна кількість алертів
        
        Returns:
            List: Список алертів
        """
        return self.alerts[-limit:]
    
    def clear_alerts(self) -> None:
        """Очистити алерти"""
        self.alerts.clear()
    
    def save_metrics(self, filepath: str, limit: int = 1000) -> None:
        """
        Зберегти метрики в JSON
        
        Args:
            filepath: Шлях до файлу
            limit: Максимальна кількість записів
        """
        data = [m.to_dict() for m in self.metrics_history[-limit:]]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def monitor_continuous(
        self,
        interval: float = 5,
        duration: Optional[float] = None,
        on_metric: Optional[Callable[[SystemMetrics], None]] = None,
        on_alert: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> None:
        """
        Безперервний моніторинг
        
        Args:
            interval: Інтервал збору метрик (секунди)
            duration: Тривалість моніторингу (None = нескінченно)
            on_metric: Callback для кожної метрики
            on_alert: Callback для алертів
        """
        start_time = time.time()
        previous_alert_count = len(self.alerts)
        
        try:
            while True:
                metrics = self.get_system_metrics()
                
                if on_metric:
                    on_metric(metrics)
                
                # Перевірити нові алерти
                if len(self.alerts) > previous_alert_count:
                    for alert in self.alerts[previous_alert_count:]:
                        if on_alert:
                            on_alert(alert)
                    previous_alert_count = len(self.alerts)
                
                if duration and (time.time() - start_time) >= duration:
                    break
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            pass


# ============================================================================
# УТИЛІТИ ФУНКЦІЇ
# ============================================================================

def get_system_metrics() -> SystemMetrics:
    """Отримати системні метрики"""
    monitor = SystemMonitor()
    return monitor.get_system_metrics()


def get_top_processes(limit: int = 10) -> List[ProcessInfo]:
    """
    Отримати топ процесів по пам'яті
    
    Args:
        limit: Максимальна кількість
    
    Returns:
        List: Процеси
    """
    monitor = SystemMonitor()
    return monitor.get_processes(sort_by='memory_percent', limit=limit)


def kill_process_by_name(name: str) -> bool:
    """
    Завершити процес по імені
    
    Args:
        name: Ім'я процесу
    
    Returns:
        bool: Успіх
    """
    monitor = SystemMonitor()
    proc = monitor.find_process(name)
    if proc:
        return monitor.kill_process(proc.pid)
    return False
