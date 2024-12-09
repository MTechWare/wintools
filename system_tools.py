import os
import subprocess
import winreg
import shutil
import psutil

class SystemTools:
    @staticmethod
    def empty_recycle_bin():
        try:
            subprocess.run(['powershell.exe', '-Command', 'Clear-RecycleBin', '-Force'], 
                         capture_output=True, 
                         check=True)
            return True, "Recycle bin emptied successfully"
        except subprocess.CalledProcessError:
            return False, "Failed to empty recycle bin"

    @staticmethod
    def open_task_manager():
        try:
            subprocess.Popen('taskmgr.exe')
            return True, "Task Manager launched"
        except Exception as e:
            return False, f"Failed to launch Task Manager: {str(e)}"

    @staticmethod
    def open_control_panel():
        try:
            subprocess.Popen('control.exe')
            return True, "Control Panel launched"
        except Exception as e:
            return False, f"Failed to launch Control Panel: {str(e)}"

    @staticmethod
    def open_system_settings():
        try:
            subprocess.Popen('ms-settings:')
            return True, "Settings launched"
        except Exception as e:
            return False, f"Failed to launch Settings: {str(e)}"

    @staticmethod
    def open_device_manager():
        try:
            subprocess.Popen('devmgmt.msc')
            return True, "Device Manager launched"
        except Exception as e:
            return False, f"Failed to launch Device Manager: {str(e)}"

    @staticmethod
    def open_disk_cleanup():
        try:
            subprocess.Popen('cleanmgr.exe')
            return True, "Disk Cleanup launched"
        except Exception as e:
            return False, f"Failed to launch Disk Cleanup: {str(e)}"

    @staticmethod
    def open_services():
        try:
            subprocess.Popen('services.msc')
            return True, "Services launched"
        except Exception as e:
            return False, f"Failed to launch Services: {str(e)}"

    @staticmethod
    def get_disk_cleanup_size():
        try:
            # Get temp folder size
            temp_size = 0
            try:
                temp_dir = os.environ.get('TEMP')
                if temp_dir and os.path.exists(temp_dir):
                    temp_size = sum(os.path.getsize(os.path.join(temp_dir, f)) 
                                for f in os.listdir(temp_dir) 
                                if os.path.isfile(os.path.join(temp_dir, f)))
            except (PermissionError, OSError) as e:
                print(f"Warning: Could not access temp directory: {e}")

            # Get recycle bin size
            recycle_size = 0
            # Get available drives
            drives = [d.device for d in psutil.disk_partitions() if 'fixed' in d.opts.lower()]
            
            for drive in drives:
                try:
                    bin_path = os.path.join(drive, '$Recycle.Bin')
                    if os.path.exists(bin_path):
                        for dirpath, _, filenames in os.walk(bin_path, onerror=None):
                            for filename in filenames:
                                try:
                                    file_path = os.path.join(dirpath, filename)
                                    if os.path.exists(file_path):  # Check if file still exists
                                        recycle_size += os.path.getsize(file_path)
                                except (PermissionError, OSError):
                                    continue
                except (PermissionError, OSError):
                    continue

            return True, {
                'temp_size': temp_size,
                'recycle_bin_size': recycle_size,
                'total_size': temp_size + recycle_size
            }
        except Exception as e:
            return False, f"Failed to calculate cleanup size: {str(e)}"
