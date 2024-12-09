import subprocess
import requests
import json
import threading
import queue
import logging
import os
import time

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler
log_file = os.path.join('logs', 'mtech_wintool.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger if they haven't been added already
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

class PackageOperations:
    def __init__(self):
        self.packages_data = {}
        self.categories = {}
        self.installation_status = {}
        self.update_status_dict = {}
        self.status_queue = None
        self.install_queue = queue.Queue()
        self.install_thread = None
        self.installing = False
        # Create startupinfo to hide windows
        self.startupinfo = subprocess.STARTUPINFO()
        self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.startupinfo.wShowWindow = subprocess.SW_HIDE

    def load_packages_async(self, callback=None, status_queue=None):
        try:
            self.status_queue = status_queue
            if callback:
                callback("Loading package data...", show_progress=True)
            response = requests.get("https://raw.githubusercontent.com/ChrisTitusTech/winutil/refs/heads/main/config/applications.json")
            self.packages_data = response.json()
            
            # Create categories dictionary
            for name, data in self.packages_data.items():
                category = data.get('category', 'Uncategorized')
                if category not in self.categories:
                    self.categories[category] = []
                self.categories[category].append(name)
            
            # Get installed software and updates using winget
            if callback:
                callback("Checking installed packages and updates...", show_progress=True)
            installed_software = self.get_winget_installed_software()
            needs_update = self.get_winget_updates()
            
            # Check installation and update status
            batch_size = 20
            packages = list(self.packages_data.keys())
            for i in range(0, len(packages), batch_size):
                batch = packages[i:i + batch_size]
                for package_name in batch:
                    is_installed = self.check_software_installed(package_name, installed_software)
                    needs_updating = self.check_needs_update(package_name, needs_update) if is_installed else False
                    self.installation_status[package_name] = is_installed
                    self.update_status_dict[package_name] = needs_updating
                    
                    # Send update for each package through the status queue
                    if self.status_queue:
                        self.status_queue.put(("update_package", (package_name, is_installed, needs_updating)))
                    
                if callback:
                    progress = min(100, int((i + batch_size) / len(packages) * 100))
                    callback(f"Checking installed packages... {progress}%")
            
            # Signal to populate the list after all updates
            if self.status_queue:
                self.status_queue.put(("populate_initial", None))
            
            if callback:
                callback("Ready")
            
        except Exception as e:
            logger.error(f"Failed to load packages: {str(e)}", exc_info=True)
            if callback:
                callback(f"Failed to load packages: {str(e)}")

    def get_winget_installed_software(self):
        try:
            process = subprocess.run(
                ['winget', 'list'],
                capture_output=True,
                text=True,
                startupinfo=self.startupinfo
            )
            return process.stdout.lower()
        except Exception as e:
            logger.error(f"Failed to get installed software list: {str(e)}", exc_info=True)
            return ""

    def get_winget_updates(self):
        try:
            process = subprocess.run(
                ['winget', 'upgrade'],
                capture_output=True,
                text=True,
                startupinfo=self.startupinfo
            )
            
            # Convert output to lowercase for case-insensitive comparison
            output = process.stdout.lower()
            
            # Create a set of package IDs that need updates
            updates = set()
            
            # Process each line
            for line in output.split('\n'):
                if line.strip() and not line.startswith('name') and not line.startswith('-'):
                    # Split the line into parts and get the ID (usually second column)
                    parts = [p.strip() for p in line.split() if p.strip()]
                    if len(parts) >= 2:
                        updates.add(parts[0])  # Add name to updates set
                        if len(parts) >= 2:
                            updates.add(parts[1])  # Add ID to updates set
            
            return updates
        except Exception as e:
            logger.error(f"Failed to get winget updates: {str(e)}", exc_info=True)
            return set()

    def check_software_installed(self, package_name, installed_software=""):
        if package_name not in self.packages_data:
            logger.warning(f"Package {package_name} not found in packages data")
            return False
            
        try:
            package_data = self.packages_data[package_name]
            
            # Check winget ID first
            winget_id = package_data.get('winget')
            if not winget_id and isinstance(package_data.get('dl'), dict):
                winget_id = package_data['dl'].get('winget')
                
            # If we have a winget ID, check if it's in the cached list
            if winget_id and winget_id.lower() in installed_software:
                return True
                
            # If no winget ID or not found, check package name
            if package_name.lower() in installed_software:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking software status for {package_name}: {str(e)}", exc_info=True)
            return False

    def check_needs_update(self, package_name, update_list):
        if not package_name in self.packages_data:
            logger.warning(f"Package {package_name} not found in packages data")
            return False
            
        try:
            package_data = self.packages_data[package_name]
            
            # Get the correct package ID
            package_id = None
            if isinstance(package_data.get('dl'), dict) and 'winget' in package_data['dl']:
                package_id = package_data['dl']['winget']
            elif 'winget' in package_data:
                package_id = package_data['winget']

            if package_id and package_id.lower() in update_list:
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error checking update status for {package_name}: {str(e)}", exc_info=True)
            return False

    def process_install_queue(self):
        """Process the installation queue sequentially"""
        while True:
            try:
                if not self.install_queue.empty():
                    package_name, callback = self.install_queue.get()
                    self.installing = True
                    self._install_package(package_name, callback)
                    self.install_queue.task_done()
                else:
                    self.installing = False
                    time.sleep(0.1)  # Prevent CPU thrashing
            except Exception as e:
                logger.error(f"Error in install queue processor: {str(e)}", exc_info=True)
                self.installing = False
                time.sleep(1)  # Wait before retrying

    def install_package(self, package_name, callback=None):
        """Queue a package for installation"""
        if not self.install_thread or not self.install_thread.is_alive():
            self.install_thread = threading.Thread(target=self.process_install_queue, daemon=True)
            self.install_thread.start()
            
        self.install_queue.put((package_name, callback))

    def _verify_package_installed(self, package_id):
        """Verify if a package is actually installed by checking winget list"""
        try:
            process = subprocess.run(
                ['winget', 'list', '--id', package_id],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return package_id.lower() in process.stdout.lower()
        except Exception as e:
            logger.error(f"Error verifying package installation: {str(e)}")
            return False

    def _install_package(self, package_name, callback=None):
        """Internal method to actually install a package"""
        if package_name not in self.packages_data:
            logger.warning(f"Package {package_name} not found in packages data")
            if callback:
                callback(f"Package {package_name} not found")
            return

        package_data = self.packages_data[package_name]
        package_id = package_data.get('winget')
        if not package_id and isinstance(package_data.get('dl'), dict):
            package_id = package_data['dl'].get('winget')

        if not package_id:
            logger.warning(f"No winget ID found for package {package_name}")
            if callback:
                callback(f"No winget ID found for {package_name}")
            return

        try:
            if callback:
                callback(f"Installing {package_name}...")

            logger.info(f"Starting installation of {package_name} (WinGet ID: {package_id})")

            # First try non-elevated install
            cmd = [
                'winget',
                'install',
                '--id', package_id,
                '-e',
                '--accept-source-agreements',
                '--accept-package-agreements'
            ]

            logger.info(f"Attempting non-elevated install for {package_name}")
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # If non-elevated fails, try elevated install
            if process.returncode != 0:
                logger.info(f"Non-elevated install failed for {package_name}, attempting elevated install")
                
                # Create elevated PowerShell command with proper argument handling
                ps_cmd = [
                    'powershell.exe',
                    '-NoProfile',
                    '-ExecutionPolicy', 'Bypass',
                    '-Command',
                    f'$process = Start-Process -FilePath winget -ArgumentList "install", "{package_id}" -Verb RunAs -Wait -PassThru; exit $process.ExitCode'
                ]

                logger.info(f"Running elevated install for {package_name}")
                process = subprocess.run(
                    ps_cmd,
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

            # Check if installation was successful
            verify_cmd = ['winget', 'list', '--id', package_id]
            verify_process = subprocess.run(
                verify_cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if package_id.lower() in verify_process.stdout.lower():
                logger.info(f"Successfully installed {package_name}")
                self.installation_status[package_name] = True
                self.update_status_dict[package_name] = False
                if self.status_queue:
                    self.status_queue.put(("update_package", (package_name, True, False)))
                if callback:
                    callback(f"Successfully installed {package_name}")
            else:
                error_msg = process.stderr if process.stderr else "Unknown error"
                logger.error(f"Failed to install {package_name}: {error_msg}")
                if callback:
                    callback(f"Failed to install {package_name}")

        except Exception as e:
            logger.error(f"Error installing {package_name}: {str(e)}", exc_info=True)
            if callback:
                callback(f"Error installing {package_name}: {str(e)}")

    def uninstall_package(self, package_name, callback=None):
        if package_name not in self.packages_data:
            logger.warning(f"Package {package_name} not found in packages data")
            if callback:
                callback(f"Package {package_name} not found")
            return

        package_data = self.packages_data[package_name]
        package_id = package_data.get('winget')
        if not package_id and isinstance(package_data.get('dl'), dict):
            package_id = package_data['dl'].get('winget')

        if not package_id:
            logger.warning(f"No winget ID found for package {package_name}")
            if callback:
                callback(f"No winget ID found for {package_name}")
            return

        try:
            if callback:
                #callback(f"Uninstalling {package_name}...")
                callback(f" Uninstalling {package_name}...", show_progress=True)
            
            process = subprocess.run(
                ['winget', 'uninstall', '--id', package_id, '-e', '--accept-source-agreements'],
                capture_output=True,
                text=True,
                startupinfo=self.startupinfo
            )
            
            if process.returncode == 0:
                # Update status to Not Installed
                self.installation_status[package_name] = False
                self.update_status_dict[package_name] = False
                if self.status_queue:
                    # Send update to refresh UI
                    self.status_queue.put(("update_package", (package_name, False, False)))
                if callback:
                    callback(f"Successfully uninstalled {package_name}")
            else:
                if callback:
                    logger.error(f"Failed to uninstall {package_name}", 
                                            f"Error: {process.stderr}\nOutput: {process.stdout}")
                    callback(f"Failed to uninstall {package_name}")

        except Exception as e:
            logger.error(f"Error uninstalling {package_name}: {str(e)}", exc_info=True)
            if callback:
                logger.error(f"Error uninstalling {package_name}", 
                        f"{str(e)}")
                callback(f"Failed to uninstall {package_name}")

    def get_exact_package_id(self, package_name):
        try:
            # Search for the package to get its exact ID
            process = subprocess.run(
                ['winget', 'search', '--name', package_name, '--exact'],
                capture_output=True,
                text=True,
                startupinfo=self.startupinfo
            )
            
            if process.returncode == 0 and process.stdout:
                # Parse the output to get the ID
                lines = process.stdout.split('\n')
                if len(lines) > 2:  # Header + separator + content
                    # Get the ID from the first result
                    parts = [p for p in lines[2].split(' ') if p]
                    if len(parts) >= 2:
                        return parts[1]  # The ID is typically the second column
            return None
        except Exception as e:
            logger.error(f"Error getting exact package ID for {package_name}: {str(e)}", exc_info=True)
            return None

    def update_package(self, package_name, callback=None):
        if package_name not in self.packages_data:
            logger.warning(f"Package {package_name} not found in packages data")
            if callback:
                callback(f"Package {package_name} not found")
            return

        package_data = self.packages_data[package_name]
        
        # First try to get ID from our JSON data
        package_id = None
        if isinstance(package_data.get('dl'), dict) and package_data['dl'].get('winget'):
            package_id = package_data['dl']['winget']
        elif package_data.get('winget'):
            package_id = package_data['winget']

        if not package_id:
            logger.warning(f"No winget ID found in package data for {package_name}")
            if callback:
                callback(f"No winget ID found for {package_name}")
            return

        try:
            if callback:
                callback(f"Updating {package_name} (ID: {package_id})...", show_progress=True)
                
            # Try to update using the package ID
            process = subprocess.run(
                ['winget', 'upgrade', '--id', package_id, '--accept-source-agreements', '--accept-package-agreements'],
                capture_output=True,
                text=True,
                startupinfo=self.startupinfo
            )
            
            # If first attempt fails, try without --id flag
            if process.returncode != 0:
                process = subprocess.run(
                    ['winget', 'upgrade', package_id, '--accept-source-agreements', '--accept-package-agreements'],
                    capture_output=True,
                    text=True,
                    startupinfo=self.startupinfo
                )
            
            if process.returncode == 0:
                # Update both installation and update status
                self.installation_status[package_name] = True
                self.update_status_dict[package_name] = False
                if self.status_queue:
                    self.status_queue.put(("update_package", (package_name, True, False)))
                if callback:
                    callback(f"Successfully updated {package_name}")
            else:
                if callback:
                    logger.error(f"Failed to update {package_name}", 
                                            f"Error: {process.stderr}\nOutput: {process.stdout}")
                    callback(f"Failed to updated {package_name}")
        except Exception as e:
            logger.error(f"Error updating {package_name}: {str(e)}", exc_info=True)
            if callback:
                logger.error(f"Error updating {package_name}", 
                        f"{str(e)}")
                callback(f"Failed to updated {package_name}")

    def refresh_packages(self, callback=None, status_queue=None):
        threading.Thread(target=self.load_packages_async, args=(callback, status_queue), daemon=True).start()

    def get_package_info(self, package_name):
        return self.packages_data.get(package_name, {})
