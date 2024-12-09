import winreg
import subprocess
import ctypes
import os
import logging
from typing import Dict, Any
import platform
import shutil

class SystemTweaks:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Enhanced Windows version detection
        self.win_version = float(platform.version().split('.')[0])
        self.win_build = int(platform.version().split('.')[2])
        self.is_win11 = self.win_version >= 10.0 and self.win_build >= 22000
        self.is_win10 = self.win_version >= 10.0 and self.win_build < 22000
        self._is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        
        # Initialize version-specific registry paths
        self.win11_paths = {
            'privacy': {
                'telemetry': r'Software\Microsoft\Windows\CurrentVersion\Privacy',
                'diagnostic': r'Software\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack',
                'feedback': r'Software\Microsoft\Windows\CurrentVersion\DiagTrack\Settings'
            },
            'performance': {
                'gaming': r'Software\Microsoft\Windows\CurrentVersion\GameDVR',
                'graphics': r'Software\Microsoft\Windows\Dwm',
                'system': r'System\CurrentControlSet\Control\Session Manager\Power'
            },
            'network': {
                'tcp': r'System\CurrentControlSet\Services\Tcpip\Parameters\Interfaces',
                'dns': r'System\CurrentControlSet\Services\Dnscache\Parameters',
                'netbt': r'System\CurrentControlSet\Services\NetBT\Parameters'
            }
        }
        
        self.win10_paths = {
            'privacy': {
                'telemetry': r'Software\Microsoft\Windows\CurrentVersion\Policies\DataCollection',
                'diagnostic': r'Software\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack',
                'feedback': r'Software\Microsoft\Siuf\Rules'
            },
            'performance': {
                'gaming': r'System\CurrentControlSet\Services\xbgm',
                'graphics': r'Software\Microsoft\Windows\DWM',
                'system': r'System\CurrentControlSet\Control\Session Manager\Memory Management'
            },
            'network': {
                'tcp': r'System\CurrentControlSet\Services\Tcpip\Parameters',
                'dns': r'System\CurrentControlSet\Services\Dnscache\Parameters',
                'netbt': r'System\CurrentControlSet\Services\NetBT\Parameters'
            }
        }

    def get_registry_path(self, category: str, subcategory: str) -> str:
        """Get the appropriate registry path based on Windows version."""
        paths = self.win11_paths if self.is_win11 else self.win10_paths
        return paths.get(category, {}).get(subcategory, '')

    def apply_tweak(self, reg_path: str, name: str, value: Any, value_type: int = winreg.REG_DWORD) -> bool:
        """Apply a registry tweak with error handling."""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, name, 0, value_type, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply tweak {name}: {str(e)}")
            return False

    def check_tweak(self, reg_path: str, name: str, expected_value: Any = 1) -> bool:
        """Check if a registry tweak is applied."""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, name)
                return value == expected_value
        except Exception as e:
            self.logger.error(f"Failed to check tweak {name}: {str(e)}")
            return False

    def is_admin(self) -> bool:
        """Check if the application is running with admin privileges."""
        return self._is_admin

def get_windows_version():
    try:
        version = platform.version().split('.')
        build = int(version[2])
        # Windows 11 starts from build 22000
        is_windows_11 = build >= 22000
        return {'is_windows_11': is_windows_11, 'build': build}
    except Exception:
        # Default to Windows 10 if version detection fails
        return {'is_windows_11': False, 'build': 0}

class PerformanceTweaks:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.windows_info = get_windows_version()
    
    def set_services_manual(self, services: list, auto: bool = False) -> bool:
        """
        Set specified Windows services to manual or automatic startup.
        
        Args:
            services (list): List of service names to modify
            auto (bool): If True, set to automatic. If False, set to manual.
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            mode = 'auto' if auto else 'demand'
            for service in services:
                try:
                    subprocess.run(['sc', 'config', service, f'start={mode}'], 
                                 check=True, capture_output=True, text=True)
                    self.logger.info(f"Successfully set {service} to {mode} startup")
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to modify {service}: {e.stderr}")
                    continue
            return True
        except Exception as e:
            self.logger.error(f"Error modifying services: {str(e)}")
            return False
            
    def check_set_services_manual(self, service_name: str) -> str:
        """
        Check the current startup type of a service.
        
        Args:
            service_name (str): Name of the service to check
            
        Returns:
            str: Current startup type of the service
        """
        try:
            result = subprocess.run(['sc', 'qc', service_name], 
                                  capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if 'START_TYPE' in line:
                    return line.strip()
            return "Unknown"
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to check service {service_name}: {e.stderr}")
            return "Error"

    def apply_tweak(self, reg_path: str, name: str, value: Any, value_type: int = winreg.REG_DWORD) -> bool:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, name, 0, value_type, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply tweak {name}: {str(e)}")
            return False
            
    def remove_tweak(self, reg_path: str, name: str) -> bool:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.DeleteValue(key, name)
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove tweak {name}: {str(e)}")
            return False

    def disable_system_restore(self, enable: bool = False) -> bool:
        try:
            # Disable System Restore
            subprocess.run(['vssadmin', 'Delete', 'Shadows', '/All', '/Quiet'], check=True)
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore"
            return self.apply_tweak(reg_path, "DisableSR", 1 if not enable else 0)
        except Exception as e:
            self.logger.error(f"Failed to modify system restore: {str(e)}")
            return False

    def optimize_visual_effects(self, optimize: bool = True) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
            value = 2 if optimize else 1  # 2 = Best Performance, 1 = Let Windows choose
            
            # Additional Windows 11 visual effects
            if self.windows_info['is_windows_11']:
                reg_path_11 = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
                # Disable Windows 11 specific animations
                self.apply_tweak(reg_path_11, "TaskbarAnimations", 0 if optimize else 1)
                self.apply_tweak(reg_path_11, "ListviewAlphaSelect", 0 if optimize else 1)
            
            return self.apply_tweak(reg_path, "VisualFXSetting", value)
        except Exception as e:
            self.logger.error(f"Failed to optimize visual effects: {str(e)}")
            return False

    def disable_search_indexing(self, disable: bool = True) -> bool:
        try:
            service_name = "WSearch"
            if disable:
                subprocess.run(['sc', 'config', service_name, 'start=disabled'], check=True)
                subprocess.run(['sc', 'stop', service_name], check=True)
            else:
                subprocess.run(['sc', 'config', service_name, 'start=delayed-auto'], check=True)
                subprocess.run(['sc', 'start', service_name], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify search indexing: {str(e)}")
            return False

    def optimize_ssd(self, optimize: bool = True) -> bool:
        try:
            # Disable Prefetch and Superfetch
            prefetch_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
            superfetch_path = r"SYSTEM\CurrentControlSet\Services\SysMain"
            
            if optimize:
                self.apply_tweak(prefetch_path, "EnablePrefetcher", 0)
                self.apply_tweak(prefetch_path, "EnableSuperfetch", 0)
                subprocess.run(['sc', 'config', 'SysMain', 'start=disabled'], check=True)
                subprocess.run(['sc', 'stop', 'SysMain'], check=True)
            else:
                self.apply_tweak(prefetch_path, "EnablePrefetcher", 3)
                self.apply_tweak(prefetch_path, "EnableSuperfetch", 3)
                subprocess.run(['sc', 'config', 'SysMain', 'start=auto'], check=True)
                subprocess.run(['sc', 'start', 'SysMain'], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to optimize SSD: {str(e)}")
            return False

    def disable_windows_animations(self, disable: bool = True) -> bool:
        try:
            reg_path = r"Control Panel\Desktop\WindowMetrics"
            animations_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            
            value = "0" if disable else "1"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "MinAnimate", 0, winreg.REG_SZ, value)
                
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, animations_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "TaskbarAnimations", 0, winreg.REG_DWORD, 0 if disable else 1)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify windows animations: {str(e)}")
            return False

    def optimize_cpu_priority(self, optimize: bool = True) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
            if optimize:
                self.apply_tweak(reg_path, "SystemResponsiveness", 0)
                self.apply_tweak(reg_path, "NetworkThrottlingIndex", 0xffffffff)
            else:
                self.apply_tweak(reg_path, "SystemResponsiveness", 20)
                self.apply_tweak(reg_path, "NetworkThrottlingIndex", 10)
            return True
        except Exception as e:
            self.logger.error(f"Failed to optimize CPU priority: {str(e)}")
            return False

    def disable_transparency(self, disable: bool = True) -> bool:
        try:
            reg_paths = [
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                r"Software\Microsoft\Windows\DWM"
            ]
            success = True
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                        winreg.SetValueEx(key, "EnableTransparency", 0, winreg.REG_DWORD, 0 if disable else 1)
                except Exception:
                    continue
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to modify transparency: {str(e)}")
            return False

    def disable_animations(self, disable: bool = True) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            success = True
            success &= self.apply_tweak(reg_path, "TaskbarAnimations", 0 if disable else 1)
            success &= self.apply_tweak(reg_path, "ListviewAlphaSelect", 0 if disable else 1)
            return success
        except Exception as e:
            self.logger.error(f"Failed to modify animations: {str(e)}")
            return False

    def optimize_processor_scheduling(self, optimize: bool = True) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\PriorityControl"
            return self.apply_tweak(reg_path, "Win32PrioritySeparation", 38 if optimize else 2)
        except Exception as e:
            self.logger.error(f"Failed to optimize processor scheduling: {str(e)}")
            return False

    def disable_background_apps(self, disable: bool = True) -> bool:
        try:
            reg_paths = [
                r"Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
                r"Software\Policies\Microsoft\Windows\AppPrivacy"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                        winreg.SetValueEx(key, "GlobalUserDisabled", 0, winreg.REG_DWORD, 1 if disable else 0)
                        winreg.SetValueEx(key, "LetAppsRunInBackground", 0, winreg.REG_DWORD, 2 if disable else 1)
                except Exception:
                    continue
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify background apps: {str(e)}")
            return False

    def disable_startup_delay(self, disable: bool = True) -> bool:
        try:
            reg_paths = [
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize",
                r"Software\Microsoft\Windows\CurrentVersion\Explorer"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                        winreg.SetValueEx(key, "StartupDelayInMSec", 0, winreg.REG_DWORD, 0 if disable else 1)
                except Exception:
                    continue
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify startup delay: {str(e)}")
            return False

    def clear_page_file(self, enable: bool = True) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
            return self.apply_tweak(reg_path, "ClearPageFileAtShutdown", 1 if enable else 0)
        except Exception as e:
            self.logger.error(f"Failed to modify page file settings: {str(e)}")
            return False

    def disable_visual_effects(self, disable: bool = True) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
            success = True
            # Set visual effects to best performance
            success &= self.apply_tweak(reg_path, "VisualFXSetting", 2 if disable else 1)
            
            # Disable additional visual effects
            if self.windows_info['is_windows_11']:
                reg_path_11 = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
                success &= self.apply_tweak(reg_path_11, "TaskbarAnimations", 0 if disable else 1)
                success &= self.apply_tweak(reg_path_11, "ListviewAlphaSelect", 0 if disable else 1)
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to modify visual effects: {str(e)}")
            return False

    def check_status(self) -> Dict[str, bool]:
        status = {}
        try:
            # Check System Restore
            try:
                reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "DisableSR")
                    status['system_restore'] = bool(value)
            except Exception:
                status['system_restore'] = False

            # Check Visual Effects
            try:
                reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "VisualFXSetting")
                    status['visual_effects'] = value == 2
            except Exception:
                status['visual_effects'] = False

            # Check Search Indexing
            try:
                result = subprocess.run(['sc', 'query', 'WSearch'], capture_output=True, text=True)
                status['search_indexing'] = 'STOPPED' in result.stdout
            except Exception:
                status['search_indexing'] = False

            # Check SSD Optimization
            try:
                reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "EnablePrefetcher")
                    status['ssd_optimization'] = value == 0
            except Exception:
                status['ssd_optimization'] = False

            # Check Windows Animations
            try:
                reg_path = r"Control Panel\Desktop\WindowMetrics"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "MinAnimate")
                    status['windows_animations'] = value == "0"
            except Exception:
                status['windows_animations'] = False

            # Check CPU Priority
            try:
                reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "SystemResponsiveness")
                    status['cpu_priority'] = value == 0
            except Exception:
                status['cpu_priority'] = False

            # Check Transparency
            try:
                reg_paths = [
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                    r"Software\Microsoft\Windows\DWM"
                ]
                
                for reg_path in reg_paths:
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                            value, _ = winreg.QueryValueEx(key, "EnableTransparency")
                            if value != 0:
                                status['transparency'] = False
                                break
                    except Exception:
                        continue
                else:
                    status['transparency'] = True
            except Exception:
                status['transparency'] = False

            # Check Animations
            try:
                reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                    animations, _ = winreg.QueryValueEx(key, "TaskbarAnimations")
                    alpha_select, _ = winreg.QueryValueEx(key, "ListviewAlphaSelect")
                    status['animations'] = animations == 0 and alpha_select == 0
            except Exception:
                status['animations'] = False

            # Check Processor Scheduling
            try:
                reg_path = r"SYSTEM\CurrentControlSet\Control\PriorityControl"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "Win32PrioritySeparation")
                    status['processor_scheduling'] = value == 38
            except Exception:
                status['processor_scheduling'] = False

            # Check Background Apps
            try:
                reg_paths = [
                    r"Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
                    r"Software\Policies\Microsoft\Windows\AppPrivacy"
                ]
                
                for reg_path in reg_paths:
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                            global_disabled, _ = winreg.QueryValueEx(key, "GlobalUserDisabled")
                            let_apps_run, _ = winreg.QueryValueEx(key, "LetAppsRunInBackground")
                            if global_disabled != 1 or let_apps_run != 2:
                                status['background_apps'] = False
                                break
                    except Exception:
                        continue
                else:
                    status['background_apps'] = True
            except Exception:
                status['background_apps'] = False

            # Check Startup Delay
            try:
                reg_paths = [
                    r"Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize",
                    r"Software\Microsoft\Windows\CurrentVersion\Explorer"
                ]
                
                for reg_path in reg_paths:
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                            value, _ = winreg.QueryValueEx(key, "StartupDelayInMSec")
                            if value != 0:
                                status['startup_delay'] = False
                                break
                    except Exception:
                        continue
                else:
                    status['startup_delay'] = True
            except Exception:
                status['startup_delay'] = False

            # Check Page File
            try:
                reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "ClearPageFileAtShutdown")
                    status['page_file'] = value == 1
            except Exception:
                status['page_file'] = False

        except Exception as e:
            self.logger.error(f"Failed to check performance tweaks status: {str(e)}")
            return {}

        return status

    def check_disable_visual_effects(self) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "VisualFXSetting")
                return value == 2  # 2 = Best Performance
        except Exception as e:
            self.logger.error(f"Failed to check visual effects status: {str(e)}")
            return False

    def check_disable_transparency(self) -> bool:
        try:
            reg_paths = [
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                r"Software\Microsoft\Windows\DWM"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                        value, _ = winreg.QueryValueEx(key, "EnableTransparency")
                        if value != 0:
                            return False
                except Exception:
                    continue
            return True
        except Exception as e:
            self.logger.error(f"Failed to check transparency status: {str(e)}")
            return False

    def check_disable_animations(self) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                animations, _ = winreg.QueryValueEx(key, "TaskbarAnimations")
                alpha_select, _ = winreg.QueryValueEx(key, "ListviewAlphaSelect")
                return animations == 0 and alpha_select == 0
        except Exception as e:
            self.logger.error(f"Failed to check animations status: {str(e)}")
            return False

    def check_optimize_processor_scheduling(self) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\PriorityControl"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "Win32PrioritySeparation")
                return value == 38
        except Exception as e:
            self.logger.error(f"Failed to check processor scheduling status: {str(e)}")
            return False

    def check_disable_background_apps(self) -> bool:
        try:
            reg_paths = [
                r"Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
                r"Software\Policies\Microsoft\Windows\AppPrivacy"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                        global_disabled, _ = winreg.QueryValueEx(key, "GlobalUserDisabled")
                        let_apps_run, _ = winreg.QueryValueEx(key, "LetAppsRunInBackground")
                        if global_disabled != 1 or let_apps_run != 2:
                            return False
                except Exception:
                    continue
            return True
        except Exception as e:
            self.logger.error(f"Failed to check background apps status: {str(e)}")
            return False

    def check_disable_startup_delay(self) -> bool:
        try:
            reg_paths = [
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize",
                r"Software\Microsoft\Windows\CurrentVersion\Explorer"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                        value, _ = winreg.QueryValueEx(key, "StartupDelayInMSec")
                        if value != 0:
                            return False
                except Exception:
                    continue
            return True
        except Exception as e:
            self.logger.error(f"Failed to check startup delay status: {str(e)}")
            return False

    def check_clear_page_file(self) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "ClearPageFileAtShutdown")
                return value == 1
        except Exception as e:
            self.logger.error(f"Failed to check page file status: {str(e)}")
            return False

    def check_optimize_ssd(self) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                prefetcher, _ = winreg.QueryValueEx(key, "EnablePrefetcher")
                superfetch, _ = winreg.QueryValueEx(key, "EnableSuperfetch")
                
                # Check if SysMain service is disabled
                result = subprocess.run(['sc', 'query', 'SysMain'], capture_output=True, text=True)
                service_disabled = 'STOPPED' in result.stdout
                
                return prefetcher == 0 and superfetch == 0 and service_disabled
        except Exception as e:
            self.logger.error(f"Failed to check SSD optimization status: {str(e)}")
            return False

    def check_disable_system_restore(self) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "DisableSR")
                return value == 1
        except Exception as e:
            self.logger.error(f"Failed to check system restore status: {str(e)}")
            return False

    def check_disable_search_indexing(self) -> bool:
        try:
            service_name = "WSearch"
            result = subprocess.run(['sc', 'query', service_name], capture_output=True, text=True)
            return "STOPPED" in result.stdout and "DISABLED" in result.stdout
        except Exception as e:
            self.logger.error(f"Failed to check search indexing status: {str(e)}")
            return False

    def check_disable_windows_animations(self) -> bool:
        try:
            reg_path = r"Control Panel\Desktop\WindowMetrics"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "MinAnimate")
                return value == "0"
        except Exception as e:
            self.logger.error(f"Failed to check windows animations status: {str(e)}")
            return False

    def check_optimize_cpu_priority(self) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "SystemResponsiveness")
                return value == 0
        except Exception as e:
            self.logger.error(f"Failed to check CPU priority status: {str(e)}")
            return False


class DesktopTweaks:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def apply_tweak(self, reg_path: str, name: str, value: Any, value_type: int = winreg.REG_DWORD) -> bool:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, name, 0, value_type, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply tweak {name}: {str(e)}")
            return False

    def show_file_extensions(self, show: bool = True) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            return self.apply_tweak(reg_path, "HideFileExt", 0 if show else 1)
        except Exception as e:
            self.logger.error(f"Failed to modify file extensions: {str(e)}")
            return False

    def show_hidden_files(self, show: bool = True) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            return self.apply_tweak(reg_path, "Hidden", 1 if show else 2)
        except Exception as e:
            self.logger.error(f"Failed to modify hidden files: {str(e)}")
            return False

    def disable_quick_access(self, disable: bool = True) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer"
            show_frequent = 0 if disable else 1
            show_recent = 0 if disable else 1
            self.apply_tweak(reg_path, "ShowFrequent", show_frequent)
            self.apply_tweak(reg_path, "ShowRecent", show_recent)
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify quick access: {str(e)}")
            return False

    def classic_context_menu(self, classic: bool = True) -> bool:
        try:
            reg_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            value = "" if classic else "%systemroot%\\system32\\shell32.dll"
            self.apply_tweak(reg_path, "", value, winreg.REG_SZ)
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify context menu: {str(e)}")
            return False

    def disable_search_highlights(self, disable: bool = True) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\SearchSettings"
            return self.apply_tweak(reg_path, "IsDynamicSearchBoxEnabled", 0 if disable else 1)
        except Exception as e:
            self.logger.error(f"Failed to modify search highlights: {str(e)}")
            return False

    def enable_dark_mode(self, enable: bool = True) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            system_theme = 0 if enable else 1
            apps_theme = 0 if enable else 1
            self.apply_tweak(reg_path, "SystemUsesLightTheme", system_theme)
            self.apply_tweak(reg_path, "AppsUseLightTheme", apps_theme)
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify dark mode: {str(e)}")
            return False

    def check_show_file_extensions(self) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "HideFileExt")
                return value == 0
        except Exception as e:
            self.logger.error(f"Failed to check file extensions status: {str(e)}")
            return False

    def check_show_hidden_files(self) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "Hidden")
                return value == 1
        except Exception as e:
            self.logger.error(f"Failed to check hidden files status: {str(e)}")
            return False

    def check_disable_quick_access(self) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                show_frequent, _ = winreg.QueryValueEx(key, "ShowFrequent")
                show_recent, _ = winreg.QueryValueEx(key, "ShowRecent")
                return show_frequent == 0 and show_recent == 0
        except Exception as e:
            self.logger.error(f"Failed to check quick access status: {str(e)}")
            return False

    def check_classic_context_menu(self) -> bool:
        try:
            reg_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "")
                    return value == ""
            except WindowsError:
                return False
        except Exception as e:
            self.logger.error(f"Failed to check context menu status: {str(e)}")
            return False

    def check_disable_search_highlights(self) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\SearchSettings"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "IsDynamicSearchBoxEnabled")
                return value == 0
        except Exception as e:
            self.logger.error(f"Failed to check search highlights status: {str(e)}")
            return False

    def check_enable_dark_mode(self) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                system_theme, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
                apps_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return system_theme == 0 and apps_theme == 0
        except Exception as e:
            self.logger.error(f"Failed to check dark mode status: {str(e)}")
            return False

    def check_status(self) -> Dict[str, bool]:
        status = {}
        try:
            # Check File Extensions
            try:
                reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "HideFileExt")
                    status['file_extensions'] = value == 0
            except Exception:
                status['file_extensions'] = False

            # Check Hidden Files
            try:
                reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "Hidden")
                    status['hidden_files'] = value == 1
            except Exception:
                status['hidden_files'] = False

            # Check Quick Access
            try:
                reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                    show_frequent, _ = winreg.QueryValueEx(key, "ShowFrequent")
                    show_recent, _ = winreg.QueryValueEx(key, "ShowRecent")
                    status['quick_access'] = show_frequent == 0 and show_recent == 0
            except Exception:
                status['quick_access'] = False

            # Check Context Menu
            try:
                reg_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                        value, _ = winreg.QueryValueEx(key, "")
                        status['context_menu'] = value == ""
                except WindowsError:
                    status['context_menu'] = False
            except Exception:
                status['context_menu'] = False

            # Check Search Highlights
            try:
                reg_path = r"Software\Microsoft\Windows\CurrentVersion\SearchSettings"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "IsDynamicSearchBoxEnabled")
                    status['search_highlights'] = value == 0
            except Exception:
                status['search_highlights'] = False

            # Check Dark Mode
            try:
                reg_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                    system_theme, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
                    apps_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    status['dark_mode'] = system_theme == 0 and apps_theme == 0
            except Exception:
                status['dark_mode'] = False

        except Exception as e:
            self.logger.error(f"Failed to check desktop tweaks status: {str(e)}")
            return {}

        return status


class PrivacyTweaks:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def apply_tweak(self, reg_path: str, name: str, value: Any, value_type: int = winreg.REG_DWORD) -> bool:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, name, 0, value_type, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply tweak {name}: {str(e)}")
            return False

    def disable_telemetry(self, disable: bool = True) -> bool:
        try:
            if disable:
                subprocess.run(['powershell', '-Command', 
                              "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' -Name 'AllowTelemetry' -Value 0"],
                             check=True)
                
                # Disable DiagTrack service
                subprocess.run(['sc', 'config', 'DiagTrack', 'start=disabled'], check=True)
                subprocess.run(['sc', 'stop', 'DiagTrack'], check=True)
            else:
                subprocess.run(['powershell', '-Command',
                              "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' -Name 'AllowTelemetry' -Value 3"],
                             check=True)
                
                # Re-enable DiagTrack service
                subprocess.run(['sc', 'config', 'DiagTrack', 'start=auto'], check=True)
                subprocess.run(['sc', 'start', 'DiagTrack'], check=True)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify telemetry settings: {str(e)}")
            return False

    def disable_advertising_id(self, disable: bool = True) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo"
            value = 0 if disable else 1
            
            self.apply_tweak(reg_path, "Enabled", value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify advertising ID: {str(e)}")
            return False

    def disable_app_suggestions(self, disable: bool = True) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
            settings = {
                "SystemPaneSuggestionsEnabled": 0 if disable else 1,
                "SubscribedContent-338388Enabled": 0 if disable else 1,
                "SubscribedContent-338389Enabled": 0 if disable else 1,
                "SubscribedContent-353696Enabled": 0 if disable else 1,
                "SoftLandingEnabled": 0 if disable else 1
            }
            
            for name, value in settings.items():
                self.apply_tweak(reg_path, name, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify app suggestions: {str(e)}")
            return False

    def disable_location_tracking(self, disable: bool = True) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Sensor\Overrides\{BFA794E4-F964-4FDB-90F6-51056BFE4B44}"
            location_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location"
            
            self.apply_tweak(reg_path, "SensorPermissionState", 0 if disable else 1)
            self.apply_tweak(location_path, "Value", "Deny" if disable else "Allow", winreg.REG_SZ)
            
            # Disable Location Service
            if disable:
                subprocess.run(['sc', 'config', 'lfsvc', 'start=disabled'], check=True)
                subprocess.run(['sc', 'stop', 'lfsvc'], check=True)
            else:
                subprocess.run(['sc', 'config', 'lfsvc', 'start=auto'], check=True)
                subprocess.run(['sc', 'start', 'lfsvc'], check=True)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify location tracking: {str(e)}")
            return False

    def disable_feedback(self, disable: bool = True) -> bool:
        try:
            reg_paths = [
                r"SOFTWARE\Microsoft\Siuf\Rules",
                r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                        winreg.SetValueEx(key, "NumberOfSIUFInPeriod", 0, winreg.REG_DWORD, 0 if disable else 1)
                except Exception:
                    continue
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify feedback: {str(e)}")
            return False

    def disable_cortana(self, disable: bool = True) -> bool:
        try:
            reg_paths = [
                r"SOFTWARE\Policies\Microsoft\Windows\Windows Search",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search"
            ]
            
            for path in reg_paths:
                self.apply_tweak(path, "AllowCortana", 0 if disable else 1)
                self.apply_tweak(path, "CortanaEnabled", 0 if disable else 1)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify Cortana settings: {str(e)}")
            return False

    def disable_activity_history(self, disable: bool = True) -> bool:
        try:
            reg_path = r"SOFTWARE\Policies\Microsoft\Windows\System"
            success = True
            success &= self.apply_tweak(reg_path, "EnableActivityFeed", 0 if disable else 1)
            success &= self.apply_tweak(reg_path, "PublishUserActivities", 0 if disable else 1)
            return success
        except Exception as e:
            self.logger.error(f"Failed to modify activity history: {str(e)}")
            return False

    def disable_location_tracking(self, disable: bool = True) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location"
            return self.apply_tweak(reg_path, "Value", "Deny" if disable else "Allow")
        except Exception as e:
            self.logger.error(f"Failed to modify location tracking: {str(e)}")
            return False

    def disable_advertising_id(self, disable: bool = True) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo"
            return self.apply_tweak(reg_path, "Enabled", 0 if disable else 1)
        except Exception as e:
            self.logger.error(f"Failed to modify advertising ID: {str(e)}")
            return False

    def disable_windows_tips(self, disable: bool = True) -> bool:
        try:
            reg_paths = [
                r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                r"Software\Policies\Microsoft\Windows\CloudContent"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                        winreg.SetValueEx(key, "SoftLandingEnabled", 0, winreg.REG_DWORD, 0 if disable else 1)
                        winreg.SetValueEx(key, "SubscribedContent-338389Enabled", 0, winreg.REG_DWORD, 0 if disable else 1)
                except Exception:
                    continue
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify windows tips: {str(e)}")
            return False

    def disable_timeline(self, disable: bool = True) -> bool:
        try:
            reg_path = r"SOFTWARE\Policies\Microsoft\Windows\System"
            return self.apply_tweak(reg_path, "EnableActivityFeed", 0 if disable else 1)
        except Exception as e:
            self.logger.error(f"Failed to modify Timeline: {str(e)}")
            return False

    def disable_cloud_clipboard(self, disable: bool = True) -> bool:
        try:
            reg_path = r"Software\Microsoft\Clipboard"
            return self.apply_tweak(reg_path, "EnableClipboardHistory", 0 if disable else 1)
        except Exception as e:
            self.logger.error(f"Failed to modify cloud clipboard: {str(e)}")
            return False

    def disable_diagnostic_data(self, disable: bool = True) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection"
            return self.apply_tweak(reg_path, "AllowTelemetry", 0 if disable else 1)
        except Exception as e:
            self.logger.error(f"Failed to modify diagnostic data: {str(e)}")
            return False

    def disable_feedback(self, disable: bool = True) -> bool:
        try:
            reg_paths = [
                r"SOFTWARE\Microsoft\Siuf\Rules",
                r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                        winreg.SetValueEx(key, "NumberOfSIUFInPeriod", 0, winreg.REG_DWORD, 0 if disable else 1)
                except Exception:
                    continue
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify feedback: {str(e)}")
            return False

    def check_status(self) -> Dict[str, bool]:
        status = {}
        try:
            status['telemetry'] = self.check_disable_telemetry()
            status['cortana'] = self.check_disable_cortana()
            status['activity_history'] = self.check_disable_activity_history()
            status['location_tracking'] = self.check_disable_location_tracking()
            status['advertising_id'] = self.check_disable_advertising_id()
            status['windows_tips'] = self.check_disable_windows_tips()
            status['timeline'] = self.check_disable_timeline()
            status['cloud_clipboard'] = self.check_disable_cloud_clipboard()
            status['diagnostic_data'] = self.check_disable_diagnostic_data()
            status['feedback'] = self.check_disable_feedback()
            return status
        except Exception as e:
            self.logger.error(f"Failed to check privacy tweaks status: {str(e)}")
            return {}

    def check_disable_telemetry(self) -> bool:
        try:
            reg_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection",
                r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Policies\DataCollection"
            ]
            
            for path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ) as key:
                        value, _ = winreg.QueryValueEx(key, "AllowTelemetry")
                        if value != 0:  # If any path has telemetry enabled
                            return False
                except WindowsError:
                    continue
            
            # Check DiagTrack service
            result = subprocess.run(['sc', 'query', 'DiagTrack'], capture_output=True, text=True)
            return "STOPPED" in result.stdout and "DISABLED" in result.stdout
        except Exception as e:
            self.logger.error(f"Failed to check telemetry status: {str(e)}")
            return False

    def check_disable_app_suggestions(self) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
            settings = [
                "SystemPaneSuggestionsEnabled",
                "SubscribedContent-338388Enabled",
                "SubscribedContent-338389Enabled",
                "SubscribedContent-353696Enabled",
                "SoftLandingEnabled"
            ]
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                for setting in settings:
                    value, _ = winreg.QueryValueEx(key, setting)
                    if value != 0:  # If any setting is enabled
                        return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to check app suggestions status: {str(e)}")
            return False

    def check_disable_cortana(self) -> bool:
        try:
            reg_paths = [
                r"SOFTWARE\Policies\Microsoft\Windows\Windows Search",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search"
            ]
            
            for path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ) as key:
                        cortana_allowed, _ = winreg.QueryValueEx(key, "AllowCortana")
                        cortana_enabled, _ = winreg.QueryValueEx(key, "CortanaEnabled")
                        if cortana_allowed != 0 or cortana_enabled != 0:
                            return False
                except WindowsError:
                    continue
            return True
        except Exception as e:
            self.logger.error(f"Failed to check Cortana status: {str(e)}")
            return False

    def check_disable_activity_history(self) -> bool:
        try:
            reg_path = r"SOFTWARE\Policies\Microsoft\Windows\System"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                feed_enabled, _ = winreg.QueryValueEx(key, "EnableActivityFeed")
                activities_enabled, _ = winreg.QueryValueEx(key, "PublishUserActivities")
                return feed_enabled == 0 and activities_enabled == 0
        except Exception as e:
            self.logger.error(f"Failed to check activity history status: {str(e)}")
            return False

    def check_disable_diagnostic_data(self) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "AllowTelemetry")
                return value == 0
        except Exception as e:
            self.logger.error(f"Failed to check diagnostic data status: {str(e)}")
            return False

    def check_disable_feedback(self) -> bool:
        try:
            reg_paths = [
                r"SOFTWARE\Microsoft\Siuf\Rules",
                r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                        siuf_period, _ = winreg.QueryValueEx(key, "NumberOfSIUFInPeriod")
                        if siuf_period != 0:
                            return False
                except Exception:
                    continue
            return True
        except Exception as e:
            self.logger.error(f"Failed to check feedback status: {str(e)}")
            return False

    def check_status(self) -> Dict[str, bool]:
        status = {}
        try:
            status['telemetry'] = self.check_disable_telemetry()
            status['app_suggestions'] = self.check_disable_app_suggestions()
            status['cortana'] = self.check_disable_cortana()
            status['activity_history'] = self.check_disable_activity_history()
            status['location_tracking'] = self.check_disable_location_tracking()
            status['advertising_id'] = self.check_disable_advertising_id()
            status['windows_tips'] = self.check_disable_windows_tips()
            status['timeline'] = self.check_disable_timeline()
            status['cloud_clipboard'] = self.check_disable_cloud_clipboard()
            status['diagnostic_data'] = self.check_disable_diagnostic_data()
            status['feedback'] = self.check_disable_feedback()
            return status
        except Exception as e:
            self.logger.error(f"Failed to check privacy tweaks status: {str(e)}")
            return {}

    def check_disable_location_tracking(self) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "Value")
                return value == "Deny"
        except Exception as e:
            self.logger.error(f"Failed to check location tracking status: {str(e)}")
            return False

    def check_disable_advertising_id(self) -> bool:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "Enabled")
                return value == 0
        except Exception as e:
            self.logger.error(f"Failed to check advertising ID status: {str(e)}")
            return False

    def check_disable_windows_tips(self) -> bool:
        try:
            reg_paths = [
                r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                r"Software\Policies\Microsoft\Windows\CloudContent"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                        value, _ = winreg.QueryValueEx(key, "SoftLandingEnabled")
                        if value != 0:
                            return False
                except Exception:
                    continue
            return True
        except Exception as e:
            self.logger.error(f"Failed to check Windows tips status: {str(e)}")
            return False

    def check_disable_timeline(self) -> bool:
        try:
            reg_path = r"SOFTWARE\Policies\Microsoft\Windows\System"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "EnableActivityFeed")
                return value == 0
        except Exception as e:
            self.logger.error(f"Failed to check timeline status: {str(e)}")
            return False

    def check_disable_cloud_clipboard(self) -> bool:
        try:
            reg_path = r"Software\Microsoft\Clipboard"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "EnableClipboardHistory")
                return value == 0
        except Exception as e:
            self.logger.error(f"Failed to check cloud clipboard status: {str(e)}")
            return False

class PowerTweaks:
    def __init__(self):
        self.system = SystemTweaks()
        self.logger = logging.getLogger(__name__)

    def set_high_performance(self, enable: bool = True) -> bool:
        try:
            # Set power plan to High Performance or Balanced
            plan = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" if enable else "381b4222-f694-41f0-9685-ff5bb260df2e"
            subprocess.run(['powercfg', '/setactive', plan], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to set power plan: {str(e)}")
            return False

    def disable_usb_power_saving(self, enable: bool = True) -> bool:
        try:
            success = True
            # Try both SYSTEM and SYSTEM\CurrentControlSet paths
            reg_paths = [
                r"SYSTEM\CurrentControlSet\Services\USB",
                r"SYSTEM\CurrentControlSet\Control\Class\{36FC9E60-C465-11CF-8056-444553540000}"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                        winreg.SetValueEx(key, "DisableSelectiveSuspend", 0, winreg.REG_DWORD, 1 if enable else 0)
                except Exception:
                    continue
            
            # Also disable USB selective suspend via power settings
            try:
                subprocess.run(['powercfg', '/setacvalueindex', 'scheme_current', 'sub_buttons', 'UsbSelectiveSuspend', '0' if enable else '1'], check=True)
                subprocess.run(['powercfg', '/setdcvalueindex', 'scheme_current', 'sub_buttons', 'UsbSelectiveSuspend', '0' if enable else '1'], check=True)
            except Exception:
                pass
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to modify USB power saving: {str(e)}")
            return False

    def disable_sleep(self, enable: bool = True) -> bool:
        try:
            # Disable sleep mode and hibernation
            subprocess.run(['powercfg', '/change', 'standby-timeout-ac', '0' if enable else '30'], check=True)
            subprocess.run(['powercfg', '/change', 'standby-timeout-dc', '0' if enable else '15'], check=True)
            subprocess.run(['powercfg', '/change', 'hibernate-timeout-ac', '0' if enable else '180'], check=True)
            subprocess.run(['powercfg', '/change', 'hibernate-timeout-dc', '0' if enable else '60'], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify sleep settings: {str(e)}")
            return False

    def check_high_performance(self) -> bool:
        try:
            result = subprocess.run(['powercfg', '/getactivescheme'], capture_output=True, text=True)
            return "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" in result.stdout
        except Exception as e:
            self.logger.error(f"Failed to check power plan status: {str(e)}")
            return False

    def check_usb_power_saving(self) -> bool:
        try:
            reg_paths = [
                r"SYSTEM\CurrentControlSet\Services\USB",
                r"SYSTEM\CurrentControlSet\Control\Class\{36FC9E60-C465-11CF-8056-444553540000}"
            ]
            
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                        value, _ = winreg.QueryValueEx(key, "DisableSelectiveSuspend")
                        if value == 1:
                            return True
                except Exception:
                    continue
            return False
        except Exception as e:
            self.logger.error(f"Failed to check USB power saving status: {str(e)}")
            return False

    def check_sleep(self) -> bool:
        try:
            # Check if sleep is disabled in power settings
            result = subprocess.run(['powercfg', '/query', 'scheme_current', 'sub_sleep'], capture_output=True, text=True)
            # Look for ACSettingIndex and DCSettingIndex with value 0 (disabled)
            ac_disabled = 'ACSettingIndex    0x00000000' in result.stdout
            dc_disabled = 'DCSettingIndex    0x00000000' in result.stdout
            return ac_disabled and dc_disabled
        except Exception as e:
            self.logger.error(f"Failed to check sleep settings: {str(e)}")
            return False

    def check_status(self) -> Dict[str, bool]:
        status = {}
        try:
            status['high_performance'] = self.check_high_performance()
            status['usb_power_saving'] = self.check_usb_power_saving()
            status['sleep'] = self.check_sleep()
            return status
        except Exception as e:
            self.logger.error(f"Failed to check power tweaks status: {str(e)}")
            return {}

    def check_set_high_performance(self) -> bool:
        """Check if high performance power plan is active."""
        try:
            result = subprocess.run(['powercfg', '/getactivescheme'], capture_output=True, text=True)
            # High Performance GUID: 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
            return '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c' in result.stdout
        except Exception as e:
            self.logger.error(f"Failed to check power scheme: {str(e)}")
            return False

    def check_disable_usb_power_saving(self) -> bool:
        """Check if USB selective suspend is disabled."""
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Services\USB"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "DisableSelectiveSuspend")
                return value == 1
        except Exception as e:
            self.logger.error(f"Failed to check USB power saving: {str(e)}")
            return False

    def check_disable_sleep(self) -> bool:
        """Check if sleep mode is disabled."""
        try:
            # Check if sleep is disabled in power settings
            result = subprocess.run(['powercfg', '/query', 'scheme_current', 'sub_sleep'], capture_output=True, text=True)
            # Look for ACSettingIndex and DCSettingIndex with value 0 (disabled)
            ac_disabled = 'ACSettingIndex    0x00000000' in result.stdout
            dc_disabled = 'DCSettingIndex    0x00000000' in result.stdout
            return ac_disabled and dc_disabled
        except Exception as e:
            self.logger.error(f"Failed to check sleep settings: {str(e)}")
            return False

    def check_status(self) -> Dict[str, bool]:
        status = {}
        try:
            status['high_performance'] = self.check_set_high_performance()
            status['usb_power_saving'] = self.check_disable_usb_power_saving()
            status['sleep'] = self.check_disable_sleep()
            return status
        except Exception as e:
            self.logger.error(f"Failed to check power tweaks status: {str(e)}")
            return {}

class GamingTweaks:
    def __init__(self):
        self.system = SystemTweaks()
        self.logger = logging.getLogger(__name__)

    def enable_game_mode(self, enable: bool = True) -> bool:
        try:
            success = True
            # Try both HKLM and HKCU paths
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\GameBar"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR")
            ]
            
            for hkey, reg_path in reg_paths:
                try:
                    with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                        winreg.SetValueEx(key, "AllowAutoGameMode", 0, winreg.REG_DWORD, 1 if enable else 0)
                        winreg.SetValueEx(key, "AutoGameModeEnabled", 0, winreg.REG_DWORD, 1 if enable else 0)
                except Exception:
                    continue
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to modify game mode: {str(e)}")
            return False

    def enable_hardware_acceleration(self, enable: bool = True) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "HwSchMode", 0, winreg.REG_DWORD, 2 if enable else 1)
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify GPU scheduling: {str(e)}")
            return False

    def disable_game_bar(self, enable: bool = True) -> bool:
        try:
            success = True
            # Try both HKLM and HKCU paths
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR"),
                (winreg.HKEY_CURRENT_USER, r"System\GameConfigStore")
            ]
            
            for hkey, reg_path in reg_paths:
                try:
                    with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                        winreg.SetValueEx(key, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0 if enable else 1)
                        if reg_path.endswith('GameConfigStore'):
                            winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0 if enable else 1)
                except Exception:
                    continue
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to modify game bar: {str(e)}")
            return False

    def check_game_mode(self) -> bool:
        try:
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\GameBar"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR")
            ]
            
            for hkey, reg_path in reg_paths:
                try:
                    with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_READ) as key:
                        auto_mode, _ = winreg.QueryValueEx(key, "AutoGameModeEnabled")
                        if auto_mode == 1:
                            return True
                except Exception:
                    continue
            return False
        except Exception as e:
            self.logger.error(f"Failed to check game mode status: {str(e)}")
            return False

    def check_hardware_acceleration(self) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "HwSchMode")
                return value == 2
        except Exception as e:
            self.logger.error(f"Failed to check GPU scheduling status: {str(e)}")
            return False

    def check_game_bar(self) -> bool:
        try:
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR"),
                (winreg.HKEY_CURRENT_USER, r"System\GameConfigStore")
            ]
            
            for hkey, reg_path in reg_paths:
                try:
                    with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_READ) as key:
                        if reg_path.endswith('GameConfigStore'):
                            value, _ = winreg.QueryValueEx(key, "GameDVR_Enabled")
                        else:
                            value, _ = winreg.QueryValueEx(key, "AppCaptureEnabled")
                        if value == 0:
                            return True
                except Exception:
                    continue
            return False
        except Exception as e:
            self.logger.error(f"Failed to check game bar status: {str(e)}")
            return False

    def check_status(self) -> Dict[str, bool]:
        status = {}
        try:
            status['game_mode'] = self.check_game_mode()
            status['hardware_acceleration'] = self.check_hardware_acceleration()
            status['game_bar'] = self.check_game_bar()
            return status
        except Exception as e:
            self.logger.error(f"Failed to check gaming tweaks status: {str(e)}")
            return {}

    def check_enable_game_mode(self) -> bool:
        """Check if Game Mode is enabled."""
        try:
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\GameBar"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR")
            ]
            
            for hkey, reg_path in reg_paths:
                try:
                    with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_READ) as key:
                        value, _ = winreg.QueryValueEx(key, "AllowAutoGameMode")
                        if value == 1:
                            return True
                except Exception:
                    continue
            return False
        except Exception as e:
            self.logger.error(f"Failed to check game mode: {str(e)}")
            return False

    def check_enable_hardware_acceleration(self) -> bool:
        """Check if hardware acceleration is enabled."""
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "HwSchMode")
                return value == 2
        except Exception as e:
            self.logger.error(f"Failed to check hardware acceleration: {str(e)}")
            return False

    def check_disable_game_bar(self) -> bool:
        """Check if Game Bar is disabled."""
        try:
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR"),
                (winreg.HKEY_CURRENT_USER, r"System\GameConfigStore")
            ]
            
            for hkey, reg_path in reg_paths:
                try:
                    with winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_READ) as key:
                        if reg_path.endswith('GameConfigStore'):
                            value, _ = winreg.QueryValueEx(key, "GameDVR_Enabled")
                        else:
                            value, _ = winreg.QueryValueEx(key, "AppCaptureEnabled")
                        if value == 0:
                            return True
                except Exception:
                    continue
            return False
        except Exception as e:
            self.logger.error(f"Failed to check game bar status: {str(e)}")
            return False

    def check_status(self) -> Dict[str, bool]:
        status = {}
        try:
            status['game_mode'] = self.check_enable_game_mode()
            status['hardware_acceleration'] = self.check_enable_hardware_acceleration()
            status['game_bar'] = self.check_disable_game_bar()
            return status
        except Exception as e:
            self.logger.error(f"Failed to check gaming tweaks status: {str(e)}")
            return {}

class NetworkTweaks:
    def __init__(self):
        self.system = SystemTweaks()
        self.logger = logging.getLogger(__name__)

    def optimize_network(self, enable: bool = True) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            success = True
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                # Enable TCP Window Auto-Tuning
                winreg.SetValueEx(key, "EnableWsd", 0, winreg.REG_DWORD, 1 if enable else 0)
                # Optimize TCP/IP settings
                winreg.SetValueEx(key, "Tcp1323Opts", 0, winreg.REG_DWORD, 1 if enable else 0)
                winreg.SetValueEx(key, "TCPNoDelay", 0, winreg.REG_DWORD, 1 if enable else 0)
            
            # Disable network throttling
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0xffffffff if enable else 0x0000000a)
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to optimize network: {str(e)}")
            return False

    def optimize_dns(self, enable: bool = True) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Services\Dnscache\Parameters"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                # Enable DNS over HTTPS
                winreg.SetValueEx(key, "EnableAutoDoh", 0, winreg.REG_DWORD, 2 if enable else 0)
                # Optimize DNS cache
                winreg.SetValueEx(key, "MaxCacheTtl", 0, winreg.REG_DWORD, 86400 if enable else 7200)
            return True
        except Exception as e:
            self.logger.error(f"Failed to optimize DNS: {str(e)}")
            return False

    def check_network_optimization(self) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                wsd, _ = winreg.QueryValueEx(key, "EnableWsd")
                tcp_opts, _ = winreg.QueryValueEx(key, "Tcp1323Opts")
                tcp_delay, _ = winreg.QueryValueEx(key, "TCPNoDelay")
                return wsd == 1 and tcp_opts == 1 and tcp_delay == 1
        except Exception as e:
            self.logger.error(f"Failed to check network optimization status: {str(e)}")
            return False

    def check_network_throttling(self) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "NetworkThrottlingIndex")
                return value == 0xffffffff
        except Exception as e:
            self.logger.error(f"Failed to check network throttling status: {str(e)}")
            return False

    def check_dns_optimization(self) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Services\Dnscache\Parameters"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                auto_doh, _ = winreg.QueryValueEx(key, "EnableAutoDoh")
                max_ttl, _ = winreg.QueryValueEx(key, "MaxCacheTtl")
                return auto_doh == 2 and max_ttl == 86400
        except Exception as e:
            self.logger.error(f"Failed to check DNS optimization status: {str(e)}")
            return False

    def check_optimize_network(self) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                wsd, _ = winreg.QueryValueEx(key, "EnableWsd")
                tcp_opts, _ = winreg.QueryValueEx(key, "Tcp1323Opts")
                tcp_delay, _ = winreg.QueryValueEx(key, "TCPNoDelay")
                return wsd == 1 and tcp_opts == 1 and tcp_delay == 1
        except Exception as e:
            self.logger.error(f"Failed to check network optimization status: {str(e)}")
            return False

    def check_optimize_dns(self) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Services\Dnscache\Parameters"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                auto_doh, _ = winreg.QueryValueEx(key, "EnableAutoDoh")
                max_ttl, _ = winreg.QueryValueEx(key, "MaxCacheTtl")
                return auto_doh == 2 and max_ttl == 86400
        except Exception as e:
            self.logger.error(f"Failed to check DNS optimization status: {str(e)}")
            return False

    def check_set_dns_servers(self) -> bool:
        """Check if custom DNS servers are set."""
        try:
            # Get network interfaces
            result = subprocess.run(['netsh', 'interface', 'ipv4', 'show', 'dns'], capture_output=True, text=True)
            
            # Look for common DNS servers (Google, Cloudflare, etc.)
            common_dns = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1']
            return any(dns in result.stdout for dns in common_dns)
        except Exception as e:
            self.logger.error(f"Failed to check DNS servers: {str(e)}")
            return False

    def check_status(self) -> Dict[str, bool]:
        status = {}
        try:
            status['network_optimization'] = self.check_optimize_network()
            status['dns_optimization'] = self.check_optimize_dns()
            status['dns_servers'] = self.check_set_dns_servers()
            return status
        except Exception as e:
            self.logger.error(f"Failed to check network tweaks status: {str(e)}")
            return {}

class MaintenanceTweaks:
    def __init__(self):
        self.system = SystemTweaks()
        self.logger = logging.getLogger(__name__)

    def clean_temp_files(self, enable: bool = True) -> bool:
        try:
            if enable:
                # Clean Windows temp files
                subprocess.run(['del', '/s', '/q', '%temp%'], shell=True, check=True)
                subprocess.run(['del', '/s', '/q', 'C:\\Windows\\Temp'], shell=True, check=True)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to clean temp files: {str(e)}")
            return False

    def optimize_windows_search(self, enable: bool = True) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows Search"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                # Set indexing to optimized mode
                winreg.SetValueEx(key, "SetupCompletedSuccessfully", 0, winreg.REG_DWORD, 1 if enable else 0)
                winreg.SetValueEx(key, "IndexerAutomaticMode", 0, winreg.REG_DWORD, 1 if enable else 0)
            return True
        except Exception as e:
            self.logger.error(f"Failed to optimize Windows Search: {str(e)}")
            return False

    def optimize_prefetch(self, enable: bool = True) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                # Enable prefetch (3 = Enable both application and boot prefetching)
                winreg.SetValueEx(key, "EnablePrefetcher", 0, winreg.REG_DWORD, 3 if enable else 0)
                winreg.SetValueEx(key, "EnableSuperfetch", 0, winreg.REG_DWORD, 3 if enable else 0)
            return True
        except Exception as e:
            self.logger.error(f"Failed to optimize prefetch: {str(e)}")
            return False

    def optimize_disk_cleanup(self, enable: bool = True) -> bool:
        try:
            if enable:
                # Run disk cleanup silently
                subprocess.run(['cleanmgr', '/sagerun:1'], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to run disk cleanup: {str(e)}")
            return False

    def optimize_system_restore(self, enable: bool = True) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                # Configure system restore (0 = Enabled with default settings)
                winreg.SetValueEx(key, "DisableSR", 0, winreg.REG_DWORD, 0 if enable else 1)
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure system restore: {str(e)}")
            return False

    def check_windows_search(self) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows Search"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "SetupCompletedSuccessfully")
                return value == 1
        except Exception as e:
            self.logger.error(f"Failed to check Windows Search status: {str(e)}")
            return False

    def check_prefetch(self) -> bool:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "EnablePrefetcher")
                return value == 3
        except Exception as e:
            self.logger.error(f"Failed to check prefetch status: {str(e)}")
            return False

    def check_disk_cleanup(self) -> bool:
        try:
            # Check if cleanup is needed by looking at free disk space
            c_drive = os.path.abspath("C:\\")
            total, used, free = shutil.disk_usage(c_drive)
            # Return True if free space is less than 10% of total
            return (free / total) > 0.1
        except Exception as e:
            self.logger.error(f"Failed to check disk cleanup status: {str(e)}")
            return False

    def check_system_restore(self) -> bool:
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "DisableSR")
                return value == 0
        except Exception as e:
            self.logger.error(f"Failed to check system restore status: {str(e)}")
            return False

    def check_clean_temp_files(self) -> bool:
        """Check if temporary files exist in common temp directories."""
        try:
            temp_paths = [
                os.environ.get('TEMP'),
                os.environ.get('TMP'),
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Temp')
            ]
            
            # Check if any of the temp directories have files
            for path in temp_paths:
                if path and os.path.exists(path):
                    # If directory is not empty, temp files exist
                    if os.listdir(path):
                        return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to check temp files: {str(e)}")
            return False

    def check_status(self) -> Dict[str, bool]:
        status = {}
        try:
            status['windows_search'] = self.check_windows_search()
            status['prefetch'] = self.check_prefetch()
            status['disk_cleanup'] = self.check_disk_cleanup()
            status['system_restore'] = self.check_system_restore()
            status['clean_temp_files'] = self.check_clean_temp_files()
            return status
        except Exception as e:
            self.logger.error(f"Failed to check maintenance tweaks status: {str(e)}")
            return {}

    def check_optimize_windows_search(self) -> bool:
        """Check if Windows Search service is optimized."""
        try:
            # Check Windows Search service status
            result = subprocess.run(['sc', 'query', 'WSearch'], capture_output=True, text=True)
            # Return True if service is stopped
            return 'STOPPED' in result.stdout
        except Exception as e:
            self.logger.error(f"Failed to check Windows Search optimization: {str(e)}")
            return False

    def check_optimize_prefetch(self) -> bool:
        """Check if prefetch is optimized."""
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                enable_prefetcher, _ = winreg.QueryValueEx(key, "EnablePrefetcher")
                enable_superfetch, _ = winreg.QueryValueEx(key, "EnableSuperfetch")
                return enable_prefetcher == 0 and enable_superfetch == 0
        except Exception as e:
            self.logger.error(f"Failed to check prefetch optimization: {str(e)}")
            return False

    def check_optimize_disk_cleanup(self) -> bool:
        """Check if disk cleanup is optimized."""
        try:
            # Check if common cleanup locations are empty
            cleanup_paths = [
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Temp'),
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Prefetch'),
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'SoftwareDistribution\\Download')
            ]
            
            for path in cleanup_paths:
                if os.path.exists(path) and os.listdir(path):
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to check disk cleanup optimization: {str(e)}")
            return False

    def check_optimize_system_restore(self) -> bool:
        """Check if system restore is optimized."""
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                disable_sr, _ = winreg.QueryValueEx(key, "DisableSR")
                return disable_sr == 1
        except Exception as e:
            self.logger.error(f"Failed to check system restore optimization: {str(e)}")
            return False