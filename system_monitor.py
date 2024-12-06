import psutil
import platform
from datetime import datetime
import threading
import time

class SystemMonitor:
    def __init__(self):
        self.callback = None
        self.running = False
        self.monitor_thread = None

    def start_monitoring(self, callback):
        self.callback = callback
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_loop(self):
        while self.running:
            stats = self.get_system_stats()
            if self.callback:
                self.callback(stats)
            time.sleep(1)  # Update every second

    def get_system_stats(self):
        stats = {}
        
        # CPU Information
        stats['cpu'] = {
            'usage_percent': psutil.cpu_percent(interval=None),
            'count': psutil.cpu_count(),
            'frequency': psutil.cpu_freq().current if hasattr(psutil.cpu_freq(), 'current') else 0
        }

        # Memory Information
        memory = psutil.virtual_memory()
        stats['memory'] = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent
        }

        # Disk Information
        disk = psutil.disk_usage('/')
        stats['disk'] = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }

        # System Information
        stats['system'] = {
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor()
        }

        return stats

    def format_bytes(self, bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} TB"
