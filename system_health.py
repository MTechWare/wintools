import psutil
import threading
import time

class SystemHealth:
    def __init__(self, update_callback):
        self.update_callback = update_callback
        self.running = False
        self.monitor_thread = None
        self.last_disk_io = None

    def start_monitoring(self):
        """Start the system monitoring thread"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop the system monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                stats = self.get_system_stats()
                if stats and self.update_callback:
                    self.update_callback(stats)
            except Exception as e:
                print(f"Error in monitor loop: {e}")
            time.sleep(2)  # Update every 2 seconds

    def get_system_stats(self):
        """Get current system statistics"""
        try:
            # CPU Usage and Info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            cpu_frequency = cpu_freq.current if cpu_freq else 0
            
            # Memory Usage
            memory = psutil.virtual_memory()
            
            # Disk Usage (use C: drive for Windows)
            disk = psutil.disk_usage('C:\\')
            
            # Get disk I/O activity
            disk_io = psutil.disk_io_counters()
            if self.last_disk_io is None:
                disk_activity = 0
            else:
                # Calculate disk activity based on read/write bytes difference
                read_diff = disk_io.read_bytes - self.last_disk_io.read_bytes
                write_diff = disk_io.write_bytes - self.last_disk_io.write_bytes
                total_diff = read_diff + write_diff
                # Convert to percentage (0-100)
                disk_activity = min(100, (total_diff / (1024 * 1024)) / 2)  # Divide by 2MB for percentage
            
            self.last_disk_io = disk_io
            
            return {
                'cpu_percent': cpu_percent,
                'cpu_cores': cpu_count,
                'cpu_frequency': cpu_frequency,
                'memory_percent': memory.percent,
                'memory_used': memory.used,
                'memory_total': memory.total,
                'disk_percent': disk_activity,  # Using actual disk activity
                'disk_used': disk.used,
                'disk_total': disk.total,
                'disk_free': disk.free
            }
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return None
