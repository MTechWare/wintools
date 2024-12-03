#!/usr/bin/env python3
"""
MTechWinTool - Windows System Utility
Version: Beta 0.0.2a

A modern Windows utility for system monitoring and software management.
This application requires administrative privileges for certain operations:
- System monitoring (CPU, Memory, Disk usage)
- Software installation via winget

Changes in Beta 0.0.2a:
- Improved software installation reliability
- Added silent mode for software uninstallation
- Added timeout handling for installation/uninstallation
- Enhanced error messages and status display
- Fixed software status refresh performance (major improvement)
- Removed dependency installation step
- Optimized batch processing for software status checks

Note: This application may be flagged by antivirus software due to its
system monitoring capabilities. This is a false positive. The source code
is open and can be verified for safety.

Author: MTechWare
License: MIT
Repository: https://github.com/MTechWare/wintools
"""

import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Label, filedialog
import sv_ttk
import psutil
import platform
import win32api
import win32con
import os
import sys
import json
from PIL import Image
import threading
import time
import wmi
from datetime import datetime
import requests
from tqdm import tqdm
import subprocess
import webbrowser
from bs4 import BeautifulSoup
import zipfile
import pkg_resources
from concurrent.futures import ThreadPoolExecutor, as_completed
import pystray
import ctypes

class SingleInstance:
    def __init__(self, name):
        self.mutexname = name
        self.mutex = None
        
    def __enter__(self):
        try:
            import win32event
            import win32api
            import winerror
            import win32con
            
            self.mutex = win32event.CreateMutex(None, False, self.mutexname)
            if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
                win32api.CloseHandle(self.mutex)
                return False
            return True
        except ImportError:
            return True  # Skip mutex check if win32event is not available
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mutex:
            try:
                import win32api
                win32api.CloseHandle(self.mutex)
            except:
                pass

class InitializationUI:
    def __init__(self):
        self.root = None
        self.progress_var = None
        self.status_var = None
        self.status_label = None
        self.progress_bar = None
        self.exit_button = None
        self.setup_complete = False

    def create_window(self):
        """Create and configure the initialization window"""
        self.root = tk.Tk()
        self.root.title("MTech WinTool Setup")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Center window
        window_width = 400
        window_height = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Configure theme
        sv_ttk.set_theme("dark")
        
        # Create and pack widgets
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Initializing...")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack(pady=(0, 10))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var,
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(pady=(0, 20))

        self.exit_button = ttk.Button(
            main_frame,
            text="Exit",
            command=self.on_exit,
            state=tk.DISABLED
        )
        self.exit_button.pack()

    def update_status(self, message, progress=None):
        """Update status message and progress bar"""
        if self.root and self.status_var:
            self.status_var.set(message)
            if progress is not None and self.progress_var:
                self.progress_var.set(progress)
            self.root.update()

    def on_exit(self):
        """Handle exit button click"""
        if self.root:
            self.root.quit()

    def check_winget(self):
        """Check if winget is installed and accessible"""
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(['winget', '--version'], 
                                 capture_output=True, 
                                 text=True, 
                                 startupinfo=startupinfo,
                                 timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False

    def run(self):
        """Run the initialization process"""
        try:
            self.create_window()
            
            # Check winget
            self.update_status("Checking winget installation...", 10)
            if not self.check_winget():
                self.update_status("Winget is not installed. \nPlease install Windows Package Manager.", 100)
                self.exit_button.configure(state=tk.NORMAL)
                self.root.mainloop()
                if self.root:  # Check if window still exists
                    self.root.destroy()
                    self.root = None
                return False
            
            self.update_status("Setup completed successfully!", 100)
            self.setup_complete = True
            self.exit_button.configure(state=tk.NORMAL)
            self.root.mainloop()
            
            # Clean up window if it still exists
            if self.root:
                self.root.destroy()
                self.root = None
                
            return True
            
        except Exception as e:
            if self.root:
                self.update_status(f"An unexpected error occurred: {str(e)}", 100)
                self.exit_button.configure(state=tk.NORMAL)
                self.root.mainloop()
                if self.root:  # Check if window still exists
                    self.root.destroy()
                    self.root = None
            return False
        finally:
            if self.root:
                self.root.destroy()
                self.root = None

class MTechWinTool:
    
    # Software categories and packages with descriptions
    SOFTWARE_CATEGORIES = {
        "Browsers": {
            "Google Chrome": {
                "id": "Google.Chrome",
                "description": "Fast, secure, and user-friendly web browser from Google"
            },
            "Mozilla Firefox": {
                "id": "Mozilla.Firefox",
                "description": "Privacy-focused web browser with extensive customization options"
            },
            "Opera GX": {
                "id": "Opera.OperaGX",
                "description": "Gaming browser with CPU, RAM & network limiters"
            },
            "Opera": {
                "id": "Opera.Opera",
                "description": "Feature-rich browser with built-in VPN and ad-blocking"
            },
            "Brave": {
                "id": "BraveSoftware.BraveBrowser",
                "description": "Privacy-first browser with built-in ad blocking and crypto wallet"
            },
            "Microsoft Edge": {
                "id": "Microsoft.Edge",
                "description": "Modern Chromium-based browser from Microsoft"
            },
            "Vivaldi": {
                "id": "VivaldiTechnologies.Vivaldi",
                "description": "Highly customizable browser with powerful features"
            }
        },
        "Development": {
            "Visual Studio Code": {
                "id": "Microsoft.VisualStudioCode",
                "description": "Lightweight but powerful source code editor"
            },
            "Git": {
                "id": "Git.Git",
                "description": "Distributed version control system"
            },
            "Python": {
                "id": "Python.Python.3.12",
                "description": "Popular programming language for general-purpose development"
            },
            "Node.js": {
                "id": "OpenJS.NodeJS.LTS",
                "description": "JavaScript runtime built on Chrome's V8 engine"
            },
            "JDK": {
                "id": "Oracle.JDK.21",
                "description": "Java Development Kit for building Java applications"
            },
            "Docker Desktop": {
                "id": "Docker.DockerDesktop",
                "description": "Platform for building and sharing containerized applications"
            },
            "Postman": {
                "id": "Postman.Postman",
                "description": "API platform for building and testing API requests"
            },
            "MongoDB Compass": {
                "id": "MongoDB.Compass.Full",
                "description": "GUI for MongoDB database management"
            },
            "MySQL Workbench": {
                "id": "Oracle.MySQL.WorkBench",
                "description": "Visual database design and administration tool for MySQL"
            },
            "Android Studio": {
                "id": "Google.AndroidStudio",
                "description": "Official IDE for Android app development"
            },
            "Visual Studio Community": {
                "id": "Microsoft.VisualStudio.2022.Community",
                "description": "Full-featured IDE for .NET development"
            },
            "GitHub Desktop": {
                "id": "GitHub.GitHubDesktop",
                "description": "GUI for managing Git repositories"
            },
            "HeidiSQL": {
                "id": "HeidiSQL.HeidiSQL",
                "description": "Lightweight SQL client and admin tool"
            },
            "DBeaver": {
                "id": "dbeaver.dbeaver",
                "description": "Universal database management tool"
            }
        },
        "Code Editors": {
            "IntelliJ IDEA Community": {
                "id": "JetBrains.IntelliJIDEA.Community",
                "description": "Capable and ergonomic Java IDE"
            },
            "PyCharm Community": {
                "id": "JetBrains.PyCharm.Community",
                "description": "Python IDE with intelligent code assistance"
            },
            "Sublime Text": {
                "id": "SublimeHQ.SublimeText.4",
                "description": "Sophisticated text editor for code and markup"
            },
            "Atom": {
                "id": "GitHub.Atom",
                "description": "Hackable text editor for the 21st Century"
            },
            "Notepad++": {
                "id": "Notepad++.Notepad++",
                "description": "Feature-rich text and source code editor"
            },
            "WebStorm": {
                "id": "JetBrains.WebStorm",
                "description": "Professional IDE for JavaScript development"
            },
            "Eclipse": {
                "id": "EclipseAdoptium.Temurin.21.JDK",
                "description": "Popular IDE supporting multiple programming languages"
            }
        },
        "Utilities": {
            "7-Zip": {
                "id": "7zip.7zip",
                "description": "File archiver with high compression ratio"
            },
            "VLC Media Player": {
                "id": "VideoLAN.VLC",
                "description": "Versatile media player supporting various formats"
            },
            "CPU-Z": {
                "id": "CPUID.CPU-Z",
                "description": "System information and CPU monitoring tool"
            },
            "GPU-Z": {
                "id": "TechPowerUp.GPU-Z",
                "description": "Graphics card information and monitoring utility"
            },
            "MSI Afterburner": {
                "id": "MSI.Afterburner",
                "description": "Graphics card overclocking and monitoring tool"
            },
            "HWiNFO": {
                "id": "REALiX.HWiNFO",
                "description": "Comprehensive hardware analysis and monitoring tool"
            },
            "PowerToys": {
                "id": "Microsoft.PowerToys",
                "description": "Windows power user productivity tools"
            },
            "Everything": {
                "id": "voidtools.Everything",
                "description": "Ultra-fast file search utility"
            },
            "TreeSize Free": {
                "id": "JAMSoftware.TreeSize.Free",
                "description": "Disk space management and visualization"
            },
            "WinDirStat": {
                "id": "WinDirStat.WinDirStat",
                "description": "Disk usage statistics viewer and cleanup tool"
            },
            "Process Explorer": {
                "id": "Microsoft.Sysinternals.ProcessExplorer",
                "description": "Advanced task manager and system monitor"
            },
            "Autoruns": {
                "id": "Microsoft.Sysinternals.Autoruns",
                "description": "Windows startup program manager"
            }
        },
        "Media & Design": {
            "Adobe Reader DC": {
                "id": "Adobe.Acrobat.Reader.64-bit",
                "description": "Popular PDF viewer and editor"
            },
            "GIMP": {
                "id": "GIMP.GIMP",
                "description": "Free and open-source raster graphics editor"
            },
            "Blender": {
                "id": "BlenderFoundation.Blender",
                "description": "Free and open-source 3D creation software"
            },
            "Audacity": {
                "id": "Audacity.Audacity",
                "description": "Free and open-source audio editing software"
            },
            "OBS Studio": {
                "id": "OBSProject.OBSStudio",
                "description": "Free and open-source screen recording and streaming software"
            },
            "Paint.NET": {
                "id": "dotPDN.PaintDotNet",
                "description": "Free image and photo editing software"
            },
            "Inkscape": {
                "id": "Inkscape.Inkscape",
                "description": "Free and open-source vector graphics editor"
            },
            "Kdenlive": {
                "id": "KDE.Kdenlive",
                "description": "Free and open-source video editing software"
            },
            "HandBrake": {
                "id": "HandBrake.HandBrake",
                "description": "Free and open-source video transcoder"
            },
            "ShareX": {
                "id": "ShareX.ShareX",
                "description": "Free and open-source screenshot and screen recording software"
            }
        },
        "Communication": {
            "Microsoft Teams": {
                "id": "Microsoft.Teams",
                "description": "Communication and collaboration platform"
            },
            "Zoom": {
                "id": "Zoom.Zoom",
                "description": "Video conferencing and online meeting platform"
            },
            "Slack": {
                "id": "SlackTechnologies.Slack",
                "description": "Communication platform for teams"
            },
            "Discord": {
                "id": "Discord.Discord",
                "description": "Communication platform for communities"
            },
            "Skype": {
                "id": "Microsoft.Skype",
                "description": "Video conferencing and online meeting platform"
            },
            "Telegram": {
                "id": "Telegram.TelegramDesktop",
                "description": "Cloud-based messaging platform"
            },
            "WhatsApp": {
                "id": "WhatsApp.WhatsApp",
                "description": "Cross-platform messaging app"
            },
            "Signal": {
                "id": "OpenWhisperSystems.Signal",
                "description": "Private messaging app"
            }
        },
        "Security": {
            "Malwarebytes": {
                "id": "Malwarebytes.Malwarebytes",
                "description": "Anti-malware software"
            },
            "Wireshark": {
                "id": "WiresharkFoundation.Wireshark",
                "description": "Network protocol analyzer"
            },
            "Advanced IP Scanner": {
                "id": "Famatech.AdvancedIPScanner",
                "description": "Network scanner and manager"
            },
            "Bitwarden": {
                "id": "Bitwarden.Bitwarden",
                "description": "Password manager"
            },
            "CCleaner": {
                "id": "Piriform.CCleaner",
                "description": "System cleaning and optimization tool"
            },
            "Windows Terminal": {
                "id": "Microsoft.WindowsTerminal",
                "description": "Terminal emulator for Windows"
            },
            "OpenVPN": {
                "id": "OpenVPNTechnologies.OpenVPN",
                "description": "Virtual private network software"
            },
            "KeePass": {
                "id": "DominikReichl.KeePass",
                "description": "Password manager"
            },
            "Glasswire": {
                "id": "GlassWire.GlassWire",
                "description": "Network security and monitoring software"
            },
            "Cryptomator": {
                "id": "Cryptomator.Cryptomator",
                "description": "Cloud storage encryption software"
            }
        },
        "Gaming": {
            "Steam": {
                "id": "Valve.Steam",
                "description": "Digital distribution platform for PC games"
            },
            "Epic Games Launcher": {
                "id": "EpicGames.EpicGamesLauncher",
                "description": "Digital distribution platform for PC games"
            },
            "GOG Galaxy": {
                "id": "GOG.Galaxy",
                "description": "Digital distribution platform for PC games"
            },
            "Xbox": {
                "id": "Microsoft.Xbox",
                "description": "Digital distribution platform for PC games"
            },
            "Ubisoft Connect": {
                "id": "Ubisoft.Connect",
                "description": "Digital distribution platform for PC games"
            },
            "EA App": {
                "id": "ElectronicArts.EADesktop",
                "description": "Digital distribution platform for PC games"
            },
            "Battle.net": {
                "id": "Blizzard.BattleNet",
                "description": "Digital distribution platform for PC games"
            },
            "PlayStation": {
                "id": "PlayStation.PSRemotePlay",
                "description": "Remote play software for PlayStation consoles"
            }
        }
    }

    def __init__(self):
        # Initialize software descriptions first
        self.software_descriptions = {}
        self.software_status = {}
        self.status_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "software_status.json")
        
        # Load software descriptions
        for category, software_dict in self.SOFTWARE_CATEGORIES.items():
            for software_name, software_info in software_dict.items():
                self.software_descriptions[software_name] = software_info['description']
        
        # Load saved software status
        self.load_software_status()
        
        # Initialize main window and other variables
        self.root = tk.Tk()
        self._setup_window()
        
        # Set window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_button)
        
        # Check if we need to refresh software status
        if not os.path.exists(self.status_file):
            self.root.after(500, self.refresh_software_status)
        
        # Initialize monitoring variables
        self.monitoring = True
        
        # Initialize WMI
        self._init_wmi()
        
        # Create UI components
        self._create_title_bar()
        self._create_main_container()
        self._create_tabs()
        
        # Start monitoring thread
        self._start_monitoring()
        
        # Setup tray icon
        self._setup_tray()
        
        # Load settings
        self._load_settings()
        
    def load_software_status(self):
        self.software_status = {}
        if os.path.exists('software_status.json'):
            try:
                with open('software_status.json', 'r') as f:
                    self.software_status = json.load(f)
            except Exception as e:
                print(f"Error loading software status: {e}")

    def save_software_status(self):
        """Save software status to file"""
        # Don't save if skip flag is set
        if hasattr(self, 'skip_status_save') and self.skip_status_save:
            return
            
        try:
            with open('software_status.json', 'w') as f:
                json.dump(self.software_status, f, indent=4)
        except Exception as e:
            print(f"Error saving software status: {str(e)}")

    def update_software_status(self, software_name, is_installed):
        """Update status for a specific software"""
        # Update in-memory status
        self.software_status[software_name] = is_installed
        
        # Update UI if the software is in the tree
        def update_ui():
            if software_name in self.software_items:
                item = self.software_items[software_name]
                if is_installed:
                    self.software_tree.item(item, tags=('installed',))
                else:
                    self.software_tree.item(item, tags=())
        
            # Save to file
            try:
                with open('software_status.json', 'w') as f:
                    json.dump(self.software_status, f, indent=4)
            except Exception as e:
                print(f"Error saving software status: {str(e)}")
    
        # Schedule UI update in main thread if not already in it
        if threading.current_thread() is threading.main_thread():
            update_ui()
        else:
            self.root.after(0, update_ui)

    def _setup_window(self):
        """Set up the main window"""        
        # Set window size and center it
        window_width = 1024
        window_height = 768
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.minsize(800, 600)
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Set window position
        self.first_map = True
        
        # Apply theme
        sv_ttk.set_theme("dark")
        self._configure_styles()
        
        # Set up window after a short delay to prevent initial minimize
        self.root.after(100, self._finish_window_setup)
        
        # Bind window events
        self.root.bind("<Map>", self._on_map)
        self.root.bind("<Unmap>", self._on_unmap)

    def _configure_styles(self):
        style = ttk.Style()
        
        # Common button style
        style.configure("TButton", 
                       padding=2,
                       background='#2b2b2b',
                       borderwidth=0,
                       relief="flat",
                       foreground='white',
                       font=("Segoe UI", 10))
        
        # Window control buttons
        style.configure("MinMax.TButton",
                       padding=2,
                       background='#2b2b2b',
                       borderwidth=0,
                       relief="flat",
                       foreground='white',
                       font=("Segoe UI", 10))
        
        style.map("MinMax.TButton",
                 background=[("!active", "#2b2b2b"), ("active", "#404040")],
                 foreground=[("!active", "white"), ("active", "white")])
        
        # Progress bar
        style.configure("Custom.Horizontal.TProgressbar",
                       troughcolor='#2b2b2b',
                       background='#2b2b2b',
                       thickness=15)

    def toggle_theme(self):
        if self.theme_var.get():
            sv_ttk.set_theme("dark")
        else:
            sv_ttk.set_theme("light")
    
    def toggle_network_fields(self):
        state = "disabled" if self.network_type_var.get() == "dhcp" else "normal"
        for entry in [self.ip_entry, self.subnet_entry, self.gateway_entry, self.dns_entry]:
            entry.configure(state=state)
    
    def _finish_window_setup(self):
        # Overrideredirect to keep custom window style
        self.root.overrideredirect(True)
        
        # Bind minimize event to handle it properly
        self.root.bind("<Map>", self._on_map)
        self.root.bind("<Unmap>", self._on_unmap)

    def _create_title_bar(self):
        title_bar = ttk.Frame(self.root)
        title_bar.pack(fill="x", pady=0)
        
        # Title section
        title_frame = ttk.Frame(title_bar)
        title_frame.pack(side="left", fill="y", padx=(5, 0))
        
        # Title text
        title_text = ttk.Label(title_frame, 
                             text="MTech Application", 
                             font=("Segoe UI", 10))
        title_text.pack(side="left", padx=(5, 10), pady=3)
        
        # Window controls
        controls_frame = ttk.Frame(title_bar)
        controls_frame.pack(side="right", fill="y")
        
        ttk.Button(controls_frame, 
                  text="─", 
                  width=2,
                  style="MinMax.TButton",
                  command=self.minimize_window).pack(side="left", padx=1, pady=1)
        
        ttk.Button(controls_frame, 
                  text="□", 
                  width=2,
                  style="MinMax.TButton",
                  command=self.toggle_maximize).pack(side="left", padx=1, pady=1)
        
        ttk.Button(controls_frame, 
                  text="×", 
                  width=2,
                  style="MinMax.TButton",
                  command=self._on_close_button).pack(side="left", padx=1, pady=1)
        
        # Make window draggable
        for widget in [title_bar, title_frame, title_text]:
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)

    def _create_main_container(self):
        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create header
        header_frame = ttk.Frame(self.container)
        header_frame.pack(fill="x", pady=(0, 20))
        

    def _create_tabs(self):
        self.notebook = ttk.Notebook(self.container)
        self.notebook.pack(fill="both", expand=True)
        
        # Initialize tab frames
        self.tab_system = ttk.Frame(self.notebook)
        self.tab_hardware = ttk.Frame(self.notebook)
        self.tab_tools = ttk.Frame(self.notebook)
        self.tab_autoinstall = ttk.Frame(self.notebook)
        self.tab_autounattend = ttk.Frame(self.notebook)
        self.tab_about = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.tab_system, text="System")
        self.notebook.add(self.tab_hardware, text="Hardware")
        self.notebook.add(self.tab_tools, text="Tools")
        self.notebook.add(self.tab_autoinstall, text="Install")
        self.notebook.add(self.tab_autounattend, text="Unattend")
        self.notebook.add(self.tab_about, text="About")
        
        # Setup tab contents
        self.setup_system_and_performance()
        self.setup_hardware_info()
        self.setup_tools()
        self.setup_autoinstall()
        self.setup_autounattend()
        self.setup_about()

    def _start_monitoring(self):
        self._monitoring_thread = threading.Thread(target=self.update_stats)
        self._monitoring_thread.daemon = True
        self._monitoring_thread.start()

    def setup_system_and_performance(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.tab_system, padding=15)
        main_frame.pack(fill="both", expand=True)
        
        # Create two columns with equal width
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Left Column - System Information
        sys_info_frame = ttk.LabelFrame(left_frame, text=" 🖥️ System Information ", padding=15)
        sys_info_frame.pack(fill="x", pady=(0, 15))
        
        # OS Info with icons
        os_info = platform.uname()
        
        # OS Info with better formatting and icons
        info_items = [
            ("🪟", "OS", f"{os_info.system} {os_info.release}"),
            ("📦", "Version", os_info.version),
            ("💻", "Machine", os_info.machine),
            ("⚡", "Processor", os_info.processor)
        ]
        
        for icon, label, value in info_items:
            frame = ttk.Frame(sys_info_frame)
            frame.pack(fill="x", pady=3)
            ttk.Label(frame, text=icon, font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
            ttk.Label(frame, text=f"{label}:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))
            ttk.Label(frame, text=value, font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True)
        
        # Boot Time with icon
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        boot_frame = ttk.Frame(sys_info_frame)
        boot_frame.pack(fill="x", pady=3)
        ttk.Label(boot_frame, text="⏰", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(boot_frame, text="Boot Time:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))
        ttk.Label(boot_frame, text=boot_time.strftime('%Y-%m-%d %H:%M:%S'), 
                 font=("Segoe UI", 9)).pack(side="left")
        
        # Memory Information
        mem_frame = ttk.LabelFrame(left_frame, text=" 🧠 Memory Information ", padding=15)
        mem_frame.pack(fill="x", pady=(0, 15))
        
        svmem = psutil.virtual_memory()
        mem_items = [
            ("📊", "Total", self.format_bytes(svmem.total)),
            ("✨", "Available", self.format_bytes(svmem.available)),
            ("📈", "Used", f"{self.format_bytes(svmem.used)} ({svmem.percent}%)")
        ]
        
        for icon, label, value in mem_items:
            frame = ttk.Frame(mem_frame)
            frame.pack(fill="x", pady=3)
            ttk.Label(frame, text=icon, font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
            ttk.Label(frame, text=f"{label}:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))
            ttk.Label(frame, text=value, font=("Segoe UI", 9)).pack(side="left")
        
        # Disk Information
        disk_frame = ttk.LabelFrame(left_frame, text=" 💾 Disk Information ", padding=15)
        disk_frame.pack(fill="x")
        
        partitions = psutil.disk_partitions()
        for partition in partitions:
            if os.name == 'nt' and ('cdrom' in partition.opts or partition.fstype == ''):
                continue
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                # Drive header
                drive_frame = ttk.Frame(disk_frame)
                drive_frame.pack(fill="x", pady=(5, 3))
                ttk.Label(drive_frame, text="💿", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
                ttk.Label(drive_frame, text=f"Drive {partition.device}", 
                         font=("Segoe UI", 9, "bold")).pack(side="left")
                
                # Drive details with consistent layout
                details_frame = ttk.Frame(disk_frame)
                details_frame.pack(fill="x", padx=15, pady=(0, 5))
                
                drive_items = [
                    ("📦", "Total", self.format_bytes(usage.total)),
                    ("📊", "Used", f"{self.format_bytes(usage.used)} ({usage.percent}%)"),
                    ("✨", "Free", self.format_bytes(usage.free))
                ]
                
                for icon, label, value in drive_items:
                    item_frame = ttk.Frame(details_frame)
                    item_frame.pack(fill="x", pady=2)
                    ttk.Label(item_frame, text=icon, font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
                    ttk.Label(item_frame, text=f"{label}:", font=("Segoe UI", 9)).pack(side="left", padx=(0, 10))
                    ttk.Label(item_frame, text=value, font=("Segoe UI", 9)).pack(side="left")
            except Exception:
                continue
        
        # Right Column - Performance Monitoring
        perf_frame = ttk.LabelFrame(right_frame, text=" 📊 Performance Monitoring ", padding=15)
        perf_frame.pack(fill="both", expand=True)
        
        # CPU Usage with custom styling
        cpu_frame = ttk.Frame(perf_frame)
        cpu_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(cpu_frame, text="⚡", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(cpu_frame, text="CPU Usage:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))
        self.cpu_label = ttk.Label(cpu_frame, text="0%", font=("Segoe UI", 9))
        self.cpu_label.pack(side="left", padx=(0, 10))
        self.cpu_progress = ttk.Progressbar(cpu_frame, length=200, mode='determinate', 
                                          style="Custom.Horizontal.TProgressbar")
        self.cpu_progress.pack(side="left", fill="x", expand=True)
        
        # CPU Temperature
        cpu_temp_frame = ttk.Frame(perf_frame)
        cpu_temp_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(cpu_temp_frame, text="🌡️", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(cpu_temp_frame, text="CPU Temp:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))
        self.cpu_temp_label = ttk.Label(cpu_temp_frame, text="N/A", font=("Segoe UI", 9))
        self.cpu_temp_label.pack(side="left", padx=(0, 10))
        self.cpu_temp_progress = ttk.Progressbar(cpu_temp_frame, length=200, mode='determinate',
                                               style="Custom.Horizontal.TProgressbar")
        self.cpu_temp_progress.pack(side="left", fill="x", expand=True)
        
        # Memory Usage
        mem_usage_frame = ttk.Frame(perf_frame)
        mem_usage_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(mem_usage_frame, text="🧠", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(mem_usage_frame, text="Memory:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))
        self.memory_label = ttk.Label(mem_usage_frame, text="0%", font=("Segoe UI", 9))
        self.memory_label.pack(side="left", padx=(0, 10))
        self.memory_progress = ttk.Progressbar(mem_usage_frame, length=200, mode='determinate',
                                             style="Custom.Horizontal.TProgressbar")
        self.memory_progress.pack(side="left", fill="x", expand=True)
        
        # Disk Usage
        disk_usage_frame = ttk.Frame(perf_frame)
        disk_usage_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(disk_usage_frame, text="💾", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(disk_usage_frame, text="Disk:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))
        self.disk_label = ttk.Label(disk_usage_frame, text="0%", font=("Segoe UI", 9))
        self.disk_label.pack(side="left", padx=(0, 10))
        self.disk_progress = ttk.Progressbar(disk_usage_frame, length=200, mode='determinate',
                                           style="Custom.Horizontal.TProgressbar")
        self.disk_progress.pack(side="left", fill="x", expand=True)
        
        # Network Usage
        net_frame = ttk.LabelFrame(right_frame, text=" 🌐 Network Usage ", padding=15)
        net_frame.pack(fill="x", pady=(15, 0))
        
        self.net_labels = {}
        net_io = psutil.net_io_counters(pernic=True)
        for nic, stats in net_io.items():
            if nic != 'lo' and not nic.startswith('veth'):
                # Network interface header
                nic_frame = ttk.Frame(net_frame)
                nic_frame.pack(fill="x", pady=(5, 3))
                ttk.Label(nic_frame, text="🔌", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
                ttk.Label(nic_frame, text=f"{nic}:", 
                         font=("Segoe UI", 9, "bold")).pack(side="left")
                
                # Network stats with consistent layout
                stats_frame = ttk.Frame(net_frame)
                stats_frame.pack(fill="x", padx=15, pady=(0, 5))
                
                sent_frame = ttk.Frame(stats_frame)
                sent_frame.pack(fill="x", pady=2)
                ttk.Label(sent_frame, text="⬆️", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
                ttk.Label(sent_frame, text="Sent:", font=("Segoe UI", 9)).pack(side="left", padx=(0, 10))
                sent_label = ttk.Label(sent_frame, text=self.format_bytes(stats.bytes_sent),
                                     font=("Segoe UI", 9))
                sent_label.pack(side="left")
                
                recv_frame = ttk.Frame(stats_frame)
                recv_frame.pack(fill="x", pady=2)
                ttk.Label(recv_frame, text="⬇️", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
                ttk.Label(recv_frame, text="Received:", font=("Segoe UI", 9)).pack(side="left", padx=(0, 10))
                recv_label = ttk.Label(recv_frame, text=self.format_bytes(stats.bytes_recv),
                                     font=("Segoe UI", 9))
                recv_label.pack(side="left")
                
                self.net_labels[nic] = (sent_label, recv_label)
    
    def setup_hardware_info(self):
        main_frame = ttk.Frame(self.tab_hardware, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Left column - CPU Information
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # CPU Information
        cpu_frame = ttk.LabelFrame(left_frame, text=" 🖥️ CPU Information ", padding=20)
        cpu_frame.pack(fill="x", pady=(0, 10))
        
        # Basic CPU Info
        basic_info = [
            ("💻", "Total Cores", psutil.cpu_count()),
            ("📈", "Physical Cores", psutil.cpu_count(logical=False)),
            ("⚡", "Base Frequency", f"{psutil.cpu_freq().current:.2f} MHz"),
            ("🔋", "Max Frequency", f"{psutil.cpu_freq().max:.2f} MHz")
        ]
        
        for icon, label, value in basic_info:
            info_frame = ttk.Frame(cpu_frame)
            info_frame.pack(fill="x", pady=5)
            ttk.Label(info_frame, text=icon, font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
            ttk.Label(info_frame, text=label + ":", font=("Segoe UI", 10, "bold")).pack(side="left")
            ttk.Label(info_frame, text=str(value)).pack(side="right")
        
        # CPU Usage with progress bar
        usage_frame = ttk.Frame(cpu_frame)
        usage_frame.pack(fill="x", pady=10)
        ttk.Label(usage_frame, text="⚡", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        ttk.Label(usage_frame, text="CPU Usage:", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.cpu_usage_label = ttk.Label(usage_frame, text="0%")
        self.cpu_usage_label.pack(side="right")
        self.cpu_usage_progress = ttk.Progressbar(cpu_frame, mode='determinate')
        self.cpu_usage_progress.pack(fill="x", pady=(0, 10))
        
        # CPU Temperature (if available)
        temp_frame = ttk.Frame(cpu_frame)
        temp_frame.pack(fill="x", pady=5)
        ttk.Label(temp_frame, text="🌡️", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        ttk.Label(temp_frame, text="CPU Temperature:", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.cpu_temp_label = ttk.Label(temp_frame, text="N/A")
        self.cpu_temp_label.pack(side="right")
        self.cpu_temp_progress = ttk.Progressbar(cpu_frame, mode='determinate', maximum=100)
        self.cpu_temp_progress.pack(fill="x", pady=(0, 10))
        
        # Memory Information
        memory_frame = ttk.LabelFrame(left_frame, text=" 🧠 Memory Information ", padding=20)
        memory_frame.pack(fill="x")
        
        # Memory Usage with progress bar
        usage_frame = ttk.Frame(memory_frame)
        usage_frame.pack(fill="x", pady=10)
        ttk.Label(usage_frame, text="📊", font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        ttk.Label(usage_frame, text="Memory Usage:", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.memory_usage_label = ttk.Label(usage_frame, text="0%")
        self.memory_usage_label.pack(side="right")
        self.memory_usage_progress = ttk.Progressbar(memory_frame, mode='determinate')
        self.memory_usage_progress.pack(fill="x", pady=(0, 10))
        
        # Detailed Memory Info
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        memory_info = [
            ("📦", "Total Memory", self.format_bytes(memory.total)),
            ("✨", "Available Memory", self.format_bytes(memory.available)),
            ("📈", "Used Memory", self.format_bytes(memory.used)),
            ("💻", "Free Memory", self.format_bytes(memory.free)),
            ("📊", "Swap Total", self.format_bytes(swap.total)),
            ("📈", "Swap Used", self.format_bytes(swap.used)),
            ("✨", "Swap Free", self.format_bytes(swap.free))
        ]
        
        for icon, label, value in memory_info:
            info_frame = ttk.Frame(memory_frame)
            info_frame.pack(fill="x", pady=5)
            ttk.Label(info_frame, text=icon, font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
            ttk.Label(info_frame, text=label + ":", font=("Segoe UI", 10, "bold")).pack(side="left")
            ttk.Label(info_frame, text=value).pack(side="right")
    
    def setup_tools(self):
        main_frame = ttk.Frame(self.tab_tools, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Tools grid
        tools = [
            ("Task Manager", "taskmgr", "Manage running applications and system resources"),
            ("Control Panel", "control", "Configure system settings"),
            ("System Properties", "sysdm.cpl", "View and modify system properties"),
            ("Disk Cleanup", "cleanmgr", "Clean up unnecessary files"),
            ("Empty Recycle Bin", self.empty_recycle_bin, "Empty the Recycle Bin")
        ]
        
        for i, (name, command, description) in enumerate(tools):
            tool_frame = ttk.LabelFrame(main_frame, text=f" 🛠️ {name} ", padding=15)
            tool_frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            ttk.Label(tool_frame, text=description, wraplength=250).pack(pady=(0, 10))
            
            if callable(command):
                btn = ttk.Button(tool_frame, text="Launch", command=command, style="TButton")
            else:
                btn = ttk.Button(tool_frame, text="Launch", 
                               command=lambda cmd=command: os.system(cmd), 
                               style="TButton")
            btn.pack()
        
        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
    
    def setup_autoinstall(self):
        main_frame = ttk.Frame(self.tab_autoinstall, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Left side - Categories and Search
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # Search frame
        search_frame = ttk.LabelFrame(left_frame, text=" 🔍 Search ", padding=10)
        search_frame.pack(fill="x", pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_software())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill="x")
        
        # Categories frame
        categories_frame = ttk.LabelFrame(left_frame, text=" 📁 Categories ", padding=10)
        categories_frame.pack(fill="both", expand=True)
        
        self.category_vars = {}
        for category in self.SOFTWARE_CATEGORIES.keys():
            var = tk.BooleanVar(value=True)
            self.category_vars[category] = var
            ttk.Checkbutton(categories_frame, text=category, variable=var,
                          command=self.filter_software).pack(fill="x", pady=2)
        
        # Right side - Software list and details
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Header frame
        header_frame = ttk.Frame(right_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text=" 📦 Software Installation ", 
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        
        # Status frame with progress bar
        status_frame = ttk.Frame(right_frame)
        status_frame.pack(fill="x", pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="")
        self.status_label.pack(fill='x', pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate', length=350)
        self.progress_bar.pack(fill='x', pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side="right")
        
        # Install button
        install_btn = ttk.Button(buttons_frame, text="Install Selected", 
                               command=self.install_selected_software,
                               style="TButton")
        install_btn.pack(side="right", padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(buttons_frame, text="Check Status", 
                               command=self.refresh_software_status)
        refresh_btn.pack(side="right", padx=5)
        
        # Create Treeview with style
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        
        # Create the treeview
        self.software_tree = ttk.Treeview(right_frame, show="tree headings", style="Treeview")
        self.software_tree["columns"] = ("Software", "Description")
        
        # Configure columns
        self.software_tree.column("#0", width=30)  # Tree column (arrow)
        self.software_tree.column("Software", width=150)
        self.software_tree.column("Description", width=300)
        
        # Configure column headings
        self.software_tree.heading("Software", text="Software")
        self.software_tree.heading("Description", text="Description")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.software_tree.yview)
        self.software_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack everything
        self.software_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store category nodes and software items
        self.category_nodes = {}
        self.software_items = {}
        
        # Populate software list
        for category in self.SOFTWARE_CATEGORIES:
            category_node = self.software_tree.insert("", "end", text=category)
            self.category_nodes[category] = category_node
            
            software_dict = self.SOFTWARE_CATEGORIES[category]
            for software_name in software_dict:
                item = self.software_tree.insert(category_node, "end", 
                                              values=(software_name, software_dict[software_name]['description']))
                self.software_items[software_name] = item
            
            # Expand the category node
            self.software_tree.item(category_node, open=True)
        
        # Apply saved status
        if hasattr(self, 'software_status'):
            for software_name, is_installed in self.software_status.items():
                if software_name in self.software_items:
                    item = self.software_items[software_name]
                    if is_installed:
                        self.software_tree.item(item, tags=('installed',))
        
        # Configure tag for installed items
        self.software_tree.tag_configure('installed', foreground='green')
        
        # Bind double-click to toggle category expansion
        self.software_tree.bind("<Double-1>", self.toggle_category)
        
        # Add right-click menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Uninstall", command=self.uninstall_selected_software)
        
        # Bind right-click to show context menu
        self.software_tree.bind("<Button-3>", self.show_context_menu)
        
        # Auto-check status if no status file exists
        if not os.path.exists('software_status.json'):
            self.status_label.config(text="Starting software status check...")
            self.progress_bar.start(10)
            self.root.after(500, self.refresh_software_status)
    
    def setup_autounattend(self):
        # Create main container frame
        container = ttk.Frame(self.tab_autounattend)
        container.pack(fill="both", expand=True)

        # Create scrollable frame for content
        content_frame = ttk.Frame(container)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create a canvas with scrollbar for the content
        canvas = tk.Canvas(content_frame)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        
        # Create the main frame inside canvas
        main_frame = ttk.Frame(canvas)
        main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create two columns
        left_column = ttk.Frame(main_frame)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        right_column = ttk.Frame(main_frame)
        right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Bottom frame for Generate XML button
        bottom_frame = ttk.Frame(container)
        bottom_frame.pack(fill="x", side="bottom", pady=10, padx=10)

        # Theme toggle
        theme_frame = ttk.Frame(bottom_frame)
        theme_frame.pack(side="left")
        self.theme_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(theme_frame, text="Dark Theme", variable=self.theme_var, 
                       command=self.toggle_theme).pack(side="left")

        # Generate XML button
        generate_btn = ttk.Button(bottom_frame, text="Generate XML", 
                                command=self.generate_unattend_xml, 
                                style="TButton",
                                width=20)
        generate_btn.pack(side="right")

        # Configure style for accent button
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        
        # Windows Settings (Left Column)
        windows_frame = ttk.LabelFrame(left_column, text=" 🖥️ Windows Settings ", padding=10)
        windows_frame.pack(fill="x", pady=(0, 10))
        
        # Windows Edition
        edition_frame = ttk.Frame(windows_frame)
        edition_frame.pack(fill="x", pady=5)
        ttk.Label(edition_frame, text="📦", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(edition_frame, text="Windows Edition:").pack(side="left")
        self.edition_var = tk.StringVar(value="Windows 10 Pro")
        editions = ["Windows 10 Home", "Windows 10 Pro", "Windows 10 Enterprise", 
                   "Windows 11 Home", "Windows 11 Pro", "Windows 11 Enterprise"]
        edition_combo = ttk.Combobox(edition_frame, textvariable=self.edition_var, values=editions)
        edition_combo.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Product Key
        key_frame = ttk.Frame(windows_frame)
        key_frame.pack(fill="x", pady=5)
        ttk.Label(key_frame, text="🔑", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(key_frame, text="Product Key:").pack(side="left")
        self.key_var = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.key_var).pack(side="right", fill="x", expand=True, padx=(10, 0))

        # User Settings
        user_frame = ttk.LabelFrame(left_column, text=" 👥 User Account ", padding=10)
        user_frame.pack(fill="x", pady=(0, 10))
        
        # Username
        username_frame = ttk.Frame(user_frame)
        username_frame.pack(fill="x", pady=5)
        ttk.Label(username_frame, text="👋", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(username_frame, text="Username:").pack(side="left")
        self.username_var = tk.StringVar(value="User")
        ttk.Entry(username_frame, textvariable=self.username_var).pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Password
        password_frame = ttk.Frame(user_frame)
        password_frame.pack(fill="x", pady=5)
        ttk.Label(password_frame, text="🔒", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(password_frame, text="Password:").pack(side="left")
        self.password_var = tk.StringVar()
        ttk.Entry(password_frame, textvariable=self.password_var, show="*").pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Organization
        org_frame = ttk.Frame(user_frame)
        org_frame.pack(fill="x", pady=5)
        ttk.Label(org_frame, text="🏢", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(org_frame, text="Organization:").pack(side="left")
        self.org_var = tk.StringVar()
        ttk.Entry(org_frame, textvariable=self.org_var).pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Computer name
        computer_frame = ttk.Frame(user_frame)
        computer_frame.pack(fill="x", pady=5)
        ttk.Label(computer_frame, text="🖥️", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(computer_frame, text="Computer Name:").pack(side="left")
        self.computer_var = tk.StringVar(value="DESKTOP-PC")
        ttk.Entry(computer_frame, textvariable=self.computer_var).pack(side="right", fill="x", expand=True, padx=(10, 0))

        # Windows Update Settings
        update_frame = ttk.LabelFrame(user_frame, text=" 📈 Windows Update ", padding=10)
        update_frame.pack(fill="x", pady=(10, 5))

        self.update_behavior_var = tk.StringVar(value="download")
        ttk.Radiobutton(update_frame, text="Download and Install Updates", value="download", 
                       variable=self.update_behavior_var).pack(fill="x", pady=2)
        ttk.Radiobutton(update_frame, text="Only Download Updates", value="downloadonly", 
                       variable=self.update_behavior_var).pack(fill="x", pady=2)
        ttk.Radiobutton(update_frame, text="Disable Windows Update", value="disable", 
                       variable=self.update_behavior_var).pack(fill="x", pady=2)

        # Power Settings
        power_frame = ttk.LabelFrame(user_frame, text=" ⚡ Power Settings ", padding=10)
        power_frame.pack(fill="x", pady=(5, 10))

        # Power Plan
        self.power_plan_var = tk.StringVar(value="balanced")
        ttk.Radiobutton(power_frame, text="Balanced", value="balanced", 
                       variable=self.power_plan_var).pack(fill="x", pady=2)
        ttk.Radiobutton(power_frame, text="High Performance", value="performance", 
                       variable=self.power_plan_var).pack(fill="x", pady=2)
        ttk.Radiobutton(power_frame, text="Power Saver", value="powersaver", 
                       variable=self.power_plan_var).pack(fill="x", pady=2)

        # Regional Settings (Right Column)
        lang_frame = ttk.LabelFrame(right_column, text=" 🌎 Regional Settings ", padding=10)
        lang_frame.pack(fill="x", pady=(0, 10))
        
        # System Language
        lang_select_frame = ttk.Frame(lang_frame)
        lang_select_frame.pack(fill="x", pady=5)
        ttk.Label(lang_select_frame, text="🌐", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(lang_select_frame, text="System Language:").pack(side="left")
        self.system_lang_var = tk.StringVar(value="en-US")
        ttk.Entry(lang_select_frame, textvariable=self.system_lang_var).pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Keyboard Layout
        keyboard_frame = ttk.Frame(lang_frame)
        keyboard_frame.pack(fill="x", pady=5)
        ttk.Label(keyboard_frame, text="🖥️", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(keyboard_frame, text="Keyboard Layout:").pack(side="left")
        self.keyboard_var = tk.StringVar(value="en-US")
        ttk.Entry(keyboard_frame, textvariable=self.keyboard_var).pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Time Zone
        timezone_frame = ttk.Frame(lang_frame)
        timezone_frame.pack(fill="x", pady=5)
        ttk.Label(timezone_frame, text="🕰️", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(timezone_frame, text="Time Zone:").pack(side="left")
        self.timezone_var = tk.StringVar(value="UTC")
        ttk.Entry(timezone_frame, textvariable=self.timezone_var).pack(side="right", fill="x", expand=True, padx=(10, 0))

        # Network Settings
        network_frame = ttk.LabelFrame(right_column, text=" 🌐 Network Configuration ", padding=10)
        network_frame.pack(fill="x", pady=(0, 10))

        # Network Type
        self.network_type_var = tk.StringVar(value="dhcp")
        ttk.Radiobutton(network_frame, text="DHCP (Automatic IP)", value="dhcp", 
                       variable=self.network_type_var, command=self.toggle_network_fields).pack(fill="x", pady=2)
        ttk.Radiobutton(network_frame, text="Static IP", value="static", 
                       variable=self.network_type_var, command=self.toggle_network_fields).pack(fill="x", pady=2)

        # IP Address
        ip_frame = ttk.Frame(network_frame)
        ip_frame.pack(fill="x", pady=5)
        ttk.Label(ip_frame, text="📍", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(ip_frame, text="IP Address:").pack(side="left")
        self.ip_var = tk.StringVar()
        self.ip_entry = ttk.Entry(ip_frame, textvariable=self.ip_var)
        self.ip_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # Subnet Mask
        subnet_frame = ttk.Frame(network_frame)
        subnet_frame.pack(fill="x", pady=5)
        ttk.Label(subnet_frame, text="🔗", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(subnet_frame, text="Subnet Mask:").pack(side="left")
        self.subnet_var = tk.StringVar()
        self.subnet_entry = ttk.Entry(subnet_frame, textvariable=self.subnet_var)
        self.subnet_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # Gateway
        gateway_frame = ttk.Frame(network_frame)
        gateway_frame.pack(fill="x", pady=5)
        ttk.Label(gateway_frame, text="🚪", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(gateway_frame, text="Gateway:").pack(side="left")
        self.gateway_var = tk.StringVar()
        self.gateway_entry = ttk.Entry(gateway_frame, textvariable=self.gateway_var)
        self.gateway_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # DNS
        dns_frame = ttk.Frame(network_frame)
        dns_frame.pack(fill="x", pady=5)
        ttk.Label(dns_frame, text="📚", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        ttk.Label(dns_frame, text="DNS Server:").pack(side="left")
        self.dns_var = tk.StringVar()
        self.dns_entry = ttk.Entry(dns_frame, textvariable=self.dns_var)
        self.dns_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # Additional Options
        options_frame = ttk.LabelFrame(network_frame, text=" 📝 Additional Options ", padding=10)
        options_frame.pack(fill="x", pady=(5, 0))
        
        self.auto_logon_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Enable Auto Logon", variable=self.auto_logon_var).pack(fill="x", pady=2)
        
        self.skip_eula_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Skip EULA", variable=self.skip_eula_var).pack(fill="x", pady=2)
        
        self.skip_updates_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Skip Windows Update", variable=self.skip_updates_var).pack(fill="x", pady=2)

        self.disable_telemetry_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Disable Telemetry", variable=self.disable_telemetry_var).pack(fill="x", pady=2)

        self.disable_cortana_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Disable Cortana", variable=self.disable_cortana_var).pack(fill="x", pady=2)

        self.remove_bloatware_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Remove Bloatware", variable=self.remove_bloatware_var).pack(fill="x", pady=2)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def generate_xml_content(self):
        # Prepare disk configuration based on layout choice
        disk_config = ""
        if self.disk_layout_var.get() == "single":
            disk_config = f'''
                <DiskConfiguration>
                    <Disk wcm:action="add">
                        <DiskID>0</DiskID>
                        <WillWipeDisk>true</WillWipeDisk>
                        <CreatePartitions>
                            <CreatePartition wcm:action="add">
                                <Order>1</Order>
                                <Type>Primary</Type>
                                <Size>{int(self.sys_size_var.get()) * 1024}</Size>
                            </CreatePartition>
                        </CreatePartitions>
                        <ModifyPartitions>
                            <ModifyPartition wcm:action="add">
                                <Order>1</Order>
                                <PartitionID>1</PartitionID>
                                <Format>NTFS</Format>
                                <Label>Windows</Label>
                            </ModifyPartition>
                        </ModifyPartitions>
                    </Disk>
                </DiskConfiguration>'''
        else:
            disk_config = f'''
                <DiskConfiguration>
                    <Disk wcm:action="add">
                        <DiskID>0</DiskID>
                        <WillWipeDisk>true</WillWipeDisk>
                        <CreatePartitions>
                            <CreatePartition wcm:action="add">
                                <Order>1</Order>
                                <Type>Primary</Type>
                                <Size>{int(self.sys_size_var.get()) * 1024}</Size>
                            </CreatePartition>
                            <CreatePartition wcm:action="add">
                                <Order>2</Order>
                                <Type>Primary</Type>
                                <Extend>true</Extend>
                            </CreatePartition>
                        </CreatePartitions>
                        <ModifyPartitions>
                            <ModifyPartition wcm:action="add">
                                <Order>1</Order>
                                <PartitionID>1</PartitionID>
                                <Format>NTFS</Format>
                                <Label>Windows</Label>
                            </ModifyPartition>
                            <ModifyPartition wcm:action="add">
                                <Order>2</Order>
                                <PartitionID>2</PartitionID>
                                <Format>NTFS</Format>
                                <Label>Data</Label>
                            </ModifyPartition>
                        </ModifyPartitions>
                    </Disk>
                </DiskConfiguration>'''

        # Network configuration
        network_config = ""
        if self.network_type_var.get() == "static":
            network_config = f'''
            <component name="Microsoft-Windows-TCPIP" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
                <Interfaces>
                    <Interface wcm:action="add">
                        <Ipv4Settings>
                            <DhcpEnabled>false</DhcpEnabled>
                        </Ipv4Settings>
                        <Identifier>Ethernet</Identifier>
                        <UnicastIpAddresses>
                            <IpAddress wcm:action="add">{self.ip_var.get()}</IpAddress>
                        </UnicastIpAddresses>
                        <Routes>
                            <Route wcm:action="add">
                                <Prefix>0.0.0.0/0</Prefix>
                                <NextHopAddress>{self.gateway_var.get()}</NextHopAddress>
                            </Route>
                        </Routes>
                    </Interface>
                </Interfaces>
            </component>
            <component name="Microsoft-Windows-DNS-Client" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
                <Interfaces>
                    <Interface wcm:action="add">
                        <DNSServerSearchOrder>
                            <IpAddress wcm:action="add">{self.dns_var.get()}</IpAddress>
                        </DNSServerSearchOrder>
                    </Interface>
                </Interfaces>
            </component>'''

        # Windows Update configuration
        update_config = ""
        if self.update_behavior_var.get() == "disable":
            update_config = '''
            <component name="Microsoft-Windows-WindowsUpdate-AU" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
                <NoAutoUpdate>true</NoAutoUpdate>
            </component>'''
        elif self.update_behavior_var.get() == "downloadonly":
            update_config = '''
            <component name="Microsoft-Windows-WindowsUpdate-AU" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
                <AUOptions>3</AUOptions>
                <NoAutoReboot>true</NoAutoReboot>
            </component>'''

        # Power settings
        power_config = ""
        if self.power_plan_var.get() != "balanced":
            power_scheme = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" if self.power_plan_var.get() == "performance" else "a1841308-3541-4fab-bc81-f71556f20b4a"
            power_config = f'''
            <component name="Microsoft-Windows-PowerShell" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
                <FirstLogonCommands>
                    <SynchronousCommand wcm:action="add">
                        <CommandLine>powercfg /setactive {power_scheme}</CommandLine>
                        <Order>1</Order>
                    </SynchronousCommand>
                </FirstLogonCommands>
            </component>'''

        # Privacy settings
        privacy_config = ""
        if self.disable_telemetry_var.get() or self.disable_cortana_var.get():
            privacy_config = '''
            <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
                <FirstLogonCommands>'''
            if self.disable_telemetry_var.get():
                privacy_config += '''
                    <SynchronousCommand wcm:action="add">
                        <CommandLine>reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f</CommandLine>
                        <Order>1</Order>
                    </SynchronousCommand>'''
            if self.disable_cortana_var.get():
                privacy_config += '''
                    <SynchronousCommand wcm:action="add">
                        <CommandLine>reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f</CommandLine>
                        <Order>2</Order>
                    </SynchronousCommand>'''
            privacy_config += '''
                </FirstLogonCommands>
            </component>'''

        xml_template = f'''<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend">
    <settings pass="windowsPE">
        <component name="Microsoft-Windows-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            {disk_config}
            <ImageInstall>
                <OSImage>
                    <InstallTo>
                        <DiskID>0</DiskID>
                        <PartitionID>1</PartitionID>
                    </InstallTo>
                    <InstallToAvailablePartition>false</InstallToAvailablePartition>
                </OSImage>
            </ImageInstall>
            <UserData>
                <AcceptEula>{str(self.skip_eula_var.get()).lower()}</AcceptEula>
                <ProductKey>
                    <Key>{self.key_var.get()}</Key>
                </ProductKey>
            </UserData>
            <EnableFirewall>true</EnableFirewall>
        </component>
        <component name="Microsoft-Windows-International-Core-WinPE" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <SetupUILanguage>
                <UILanguage>{self.lang_var.get()}</UILanguage>
            </SetupUILanguage>
            <InputLocale>{self.keyboard_var.get()}</InputLocale>
            <SystemLocale>{self.lang_var.get()}</SystemLocale>
            <UILanguage>{self.lang_var.get()}</UILanguage>
            <UserLocale>{self.lang_var.get()}</UserLocale>
        </component>
    </settings>
    <settings pass="specialize">
        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <ComputerName>{self.computer_var.get()}</ComputerName>
            <RegisteredOrganization>{self.org_var.get()}</RegisteredOrganization>
            <TimeZone>{self.timezone_var.get()}</TimeZone>
        </component>
        {network_config}
        {update_config}
        {power_config}
    </settings>
    <settings pass="oobeSystem">
        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <AutoLogon>
                <Enabled>{str(self.auto_logon_var.get()).lower()}</Enabled>
                <Username>{self.username_var.get()}</Username>
                <Password>
                    <Value>{self.password_var.get()}</Value>
                    <PlainText>true</PlainText>
                </Password>
            </AutoLogon>
            <OOBE>
                <HideEULAPage>{str(self.skip_eula_var.get()).lower()}</HideEULAPage>
                <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>
                <NetworkLocation>Work</NetworkLocation>
                <ProtectYourPC>3</ProtectYourPC>
                <SkipMachineOOBE>true</SkipMachineOOBE>
                <SkipUserOOBE>true</SkipUserOOBE>
            </OOBE>
            <UserAccounts>
                <LocalAccounts>
                    <LocalAccount wcm:action="add">
                        <Password>
                            <Value>{self.password_var.get()}</Value>
                            <PlainText>true</PlainText>
                        </Password>
                        <DisplayName>{self.username_var.get()}</DisplayName>
                        <Group>Administrators</Group>
                        <Name>{self.username_var.get()}</Name>
                    </LocalAccount>
                </LocalAccounts>
            </UserAccounts>
            {privacy_config}
        </component>
        <component name="Microsoft-Windows-International-Core" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <InputLocale>{self.keyboard_var.get()}</InputLocale>
            <SystemLocale>{self.lang_var.get()}</SystemLocale>
            <UILanguage>{self.lang_var.get()}</UILanguage>
            <UserLocale>{self.lang_var.get()}</UserLocale>
        </component>
    </settings>
</unattend>'''
        return xml_template
    
    def generate_unattend_xml(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml")],
                initialfile="autounattend.xml"
            )
            if file_path:
                xml_content = self.generate_xml_content()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
                messagebox.showinfo("Success", f"Unattend XML saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save XML: {str(e)}")
    
    def update_software_status(self, software_name, is_installed):
        """Update status for a specific software"""
        # Update in-memory status
        self.software_status[software_name] = is_installed
        
        # Update UI if the software is in the tree
        def update_ui():
            if software_name in self.software_items:
                item = self.software_items[software_name]
                if is_installed:
                    self.software_tree.item(item, tags=('installed',))
                else:
                    self.software_tree.item(item, tags=())
        
            # Save to file
            try:
                with open('software_status.json', 'w') as f:
                    json.dump(self.software_status, f, indent=4)
            except Exception as e:
                print(f"Error saving software status: {str(e)}")
    
        # Schedule UI update in main thread if not already in it
        if threading.current_thread() is threading.main_thread():
            update_ui()
        else:
            self.root.after(0, update_ui)

    def load_software_status(self):
        self.software_status = {}
        if os.path.exists('software_status.json'):
            try:
                with open('software_status.json', 'r') as f:
                    self.software_status = json.load(f)
            except Exception as e:
                print(f"Error loading software status: {e}")

    def save_software_status(self):
        """Save software status to file"""
        # Don't save if skip flag is set
        if hasattr(self, 'skip_status_save') and self.skip_status_save:
            return
            
        try:
            with open('software_status.json', 'w') as f:
                json.dump(self.software_status, f, indent=4)
        except Exception as e:
            print(f"Error saving software status: {str(e)}")

    def install_selected_software(self):
        """Install selected software using winget"""
        selected = self.software_tree.selection()
        if not selected:
            messagebox.showinfo("Select Software", "Please select software to install")
            return

        # Filter out category nodes and get valid software selections
        software_to_install = []
        for item in selected:
            item_data = self.software_tree.item(item)
            values = item_data.get("values", [])
            
            # Skip if it's a category (no values) or not enough values
            if not values or len(values) < 2:
                continue
                
            software_name = values[0]
            # Find the category for this software
            for category, software_dict in self.SOFTWARE_CATEGORIES.items():
                if software_name in software_dict:
                    software_to_install.append((item, category, software_name))
                    break

        if not software_to_install:
            messagebox.showinfo("Select Software", "Please select valid software to install")
            return
        
        # Create progress window
        progress_window = Toplevel(self.root)
        progress_window.title("Installing Software")
        progress_window.geometry("400x150")
        
        # Center the window
        progress_window.transient(self.root)
        progress_window.grab_set()
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
        progress_window.geometry(f"+{x}+{y}")
        
        # Add progress elements
        frame = ttk.Frame(progress_window, padding="20")
        frame.pack(fill='both', expand=True)
        
        status_label = ttk.Label(frame, text="Starting installation...", wraplength=350)
        status_label.pack(fill='x', pady=(0, 10))
        
        progress_bar = ttk.Progressbar(frame, mode='indeterminate', length=350)
        progress_bar.pack(fill='x', pady=(0, 10))
        progress_bar.start(10)
        
        def install_software():
            try:
                for item, category, software_name in software_to_install:
                    winget_id = self.SOFTWARE_CATEGORIES[category][software_name]['id']
                    try:
                        status_label.config(text=f"Installing {software_name}...")
                        
                        # Run winget install
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        
                        result = subprocess.run(
                            ["winget", "install", "-e", "--id", winget_id, "--accept-source-agreements", "--accept-package-agreements"],
                            capture_output=True,
                            text=True,
                            startupinfo=startupinfo
                        )
                        
                        if result.returncode == 0:
                            # Update status and UI
                            self.update_software_status(software_name, True)
                            status_label.config(text=f"Successfully installed {software_name}")
                            print(f"Successfully installed {software_name}")
                        else:
                            error_msg = f"Failed to install {software_name}. Error: {result.stderr}"
                            status_label.config(text=error_msg)
                            print(error_msg)
                            messagebox.showerror("Installation Error", error_msg)
                    except Exception as e:
                        error_msg = f"Error installing {software_name}: {str(e)}"
                        status_label.config(text=error_msg)
                        print(error_msg)
                        messagebox.showerror("Installation Error", error_msg)
            finally:
                # Stop progress and close window
                progress_bar.stop()
                progress_window.after(1500, progress_window.destroy)
        
        # Run installation in a separate thread
        threading.Thread(target=install_software, daemon=True).start()
    
    def toggle_category(self, event):
        item = self.software_tree.identify('item', event.x, event.y)
        if item in self.category_nodes.values():
            if self.software_tree.item(item, "open"):
                self.software_tree.item(item, open=False)
            else:
                self.software_tree.item(item, open=True)
    
    def filter_software(self):
        search_text = self.search_var.get().lower()
        
        # Hide all items first
        for category_node in self.category_nodes.values():
            self.software_tree.detach(category_node)
        
        # Show items that match the filter
        for category, node in self.category_nodes.items():
            if not self.category_vars[category].get():
                continue
                
            show_category = False
            category_children = self.software_tree.get_children(node)
            
            for child in category_children:
                values = self.software_tree.item(child)['values']
                software_name = values[0].lower()
                description = values[1].lower()
                
                if search_text in software_name or search_text in description:
                    show_category = True
                    break
            
            if show_category:
                self.software_tree.reattach(node, "", "end")
    
    def refresh_software_status(self, force=False):
        """Refresh software installation status using batch processing"""
        def check_status():
            if not hasattr(self, 'root') or not self.root:
                return

            try:
                # Prepare command to check all software at once
                all_ids = []
                id_to_name = {}
                
                for category, software_dict in self.SOFTWARE_CATEGORIES.items():
                    for software_name, software_info in software_dict.items():
                        # Use cache if available and not forcing refresh
                        if not force and software_name in self.software_status:
                            if hasattr(self, 'root') and self.root:
                                self.root.after(0, lambda name=software_name, installed=self.software_status[software_name]:
                                    self.update_software_status(name, installed) if hasattr(self, 'root') else None)
                            continue
                            
                        all_ids.append(software_info['id'])
                        id_to_name[software_info['id']] = software_name

                if all_ids:  # Only proceed if we have IDs to check
                    # Update status
                    if hasattr(self, 'status_label'):
                        self.root.after(0, lambda: 
                            self.status_label.config(text="Checking software status...") if hasattr(self, 'status_label') else None)

                    # Run single winget command for all software
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    result = subprocess.run(
                        ["winget", "list"],
                        capture_output=True,
                        text=True,
                        startupinfo=startupinfo
                    )

                    # Process output to determine installed software
                    output = result.stdout.lower()
                    for software_id in all_ids:
                        is_installed = software_id.lower() in output
                        software_name = id_to_name[software_id]
                        
                        # Update UI in main thread
                        if hasattr(self, 'root') and self.root:
                            self.root.after(0, lambda name=software_name, installed=is_installed:
                                self.update_software_status(name, installed) if hasattr(self, 'root') else None)

                # Schedule final status update in main thread
                if hasattr(self, 'root') and self.root and hasattr(self, 'status_label'):
                    self.root.after(0, lambda: 
                        self.status_label.config(text="Status check complete!") if hasattr(self, 'status_label') else None)

            except Exception as e:
                if hasattr(self, 'root') and self.root:
                    print(f"Error in check_status: {str(e)}")
                    if hasattr(self, 'status_label'):
                        self.root.after(0, lambda: 
                            self.status_label.config(text="Error checking software status") if hasattr(self, 'status_label') else None)
            finally:
                # Schedule progress bar cleanup in main thread if widgets still exist
                if hasattr(self, 'root') and self.root:
                    if hasattr(self, 'progress_bar'):
                        self.root.after(0, lambda: 
                            self.progress_bar.stop() if hasattr(self, 'progress_bar') else None)
                    if hasattr(self, 'status_label'):
                        self.root.after(1500, lambda: 
                            self.status_label.config(text="") if hasattr(self, 'status_label') else None)

        # Start progress bar if it exists
        if hasattr(self, 'progress_bar'):
            self.progress_bar.start()

        # Run check in background thread
        threading.Thread(target=check_status, daemon=True).start()
    
    def update_stats(self):
        while self.monitoring:
            try:
                # Update CPU usage
                cpu_percent = psutil.cpu_percent()
                
                # Update Memory usage
                memory = psutil.virtual_memory()
                
                # Update Disk usage
                disk = psutil.disk_usage('/')
                
                # Update System Monitor tab
                if self.cpu_label:
                    self.cpu_label.configure(text=f"{cpu_percent}%")
                    self.cpu_progress['value'] = cpu_percent
                
                if self.memory_label:
                    self.memory_label.configure(text=f"{memory.percent}%")
                    self.memory_progress['value'] = memory.percent
                
                if self.disk_label:
                    self.disk_label.configure(text=f"{disk.percent}%")
                    self.disk_progress['value'] = disk.percent
                
                # Update Hardware tab
                if hasattr(self, 'cpu_usage_label'):
                    self.cpu_usage_label.configure(text=f"{cpu_percent}%")
                    self.cpu_usage_progress['value'] = cpu_percent
                
                if hasattr(self, 'memory_usage_label'):
                    self.memory_usage_label.configure(text=f"{memory.percent}%")
                    self.memory_usage_progress['value'] = memory.percent
                
                # Update Network tab
                if hasattr(self, 'net_labels'):
                    net_io = psutil.net_io_counters(pernic=True)
                    for nic, (sent_label, recv_label) in self.net_labels.items():
                        if nic in net_io:
                            sent_label.configure(text=f"Sent: {self.format_bytes(net_io[nic].bytes_sent)}")
                            recv_label.configure(text=f"Received: {self.format_bytes(net_io[nic].bytes_recv)}")
                
                time.sleep(1)
            except Exception as e:
                print(f"Error updating stats: {str(e)}")
                time.sleep(1)
    
    def format_bytes(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} PB"
    
    def empty_recycle_bin(self):
        try:
            import winshell
            winshell.recycle_bin().empty(confirm=True, show_progress=True, sound=True)
            messagebox.showinfo("Success", "Recycle Bin emptied successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to empty Recycle Bin: {str(e)}")
    
    def toggle_theme(self):
        if self.theme_var.get():
            sv_ttk.set_theme("dark")
        else:
            sv_ttk.set_theme("light")
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def toggle_maximize(self):
        if self.is_maximized:
            self.root.geometry(self.window_size)
            self.is_maximized = False
        else:
            self.window_size = self.root.geometry()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.is_maximized = True
    
    def setup_about(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.tab_about, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Left side - App info
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        
        # App logo/icon
        if os.path.exists("sun_valley_app/assets/icon.ico"):
            icon = tk.PhotoImage(file="sun_valley_app/assets/icon.ico")
            icon_label = ttk.Label(left_frame, image=icon)
            icon_label.image = icon
            icon_label.pack(pady=(0, 20))
    
        
        # Version
        version = ttk.Label(left_frame, text="Beta Version 0.0.2a", 
                          font=("Segoe UI", 12))
        version.pack(pady=(0, 20))
        
        # Description
        description = ttk.Label(left_frame, text="A comprehensive Windows utility tool\n" +
                              "for system management and optimization.",
                              font=("Segoe UI", 10),
                              justify="center")
        description.pack(pady=(0, 20))
        
        # Copyright
        copyright_text = ttk.Label(left_frame, text=" 2024 MTech. All rights reserved.",
                                font=("Segoe UI", 9))
        copyright_text.pack(pady=(0, 10))
        
        # Website link
        website_frame = ttk.Frame(left_frame)
        website_frame.pack(pady=(0, 20))
        
        website_label = ttk.Label(website_frame, text="Visit our website:",
                               font=("Segoe UI", 9))
        website_label.pack(side="left", padx=(0, 5))
        
        website_link = ttk.Label(website_frame, text="mtech.glitch.me",
                              font=("Segoe UI", 9, "underline"),
                              foreground="blue",
                              cursor="hand2")
        website_link.pack(side="left")
        website_link.bind("<Button-1>", lambda e: webbrowser.open("https://mtech.glitch.me"))
        
        # Separator
        separator = ttk.Separator(main_frame, orient="vertical")
        separator.pack(side="left", fill="y")
        
        # Right side - Features
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        # Features title
        features_title = ttk.Label(right_frame, text="Key Features",
                                font=("Segoe UI", 16, "bold"))
        features_title.pack(pady=(0, 20))
        
        # Features list
        features = [
            ("System & Performance", "Monitor and optimize system performance"),
            ("Hardware Information", "View detailed hardware specifications"),
            ("System Tools", "Essential tools for system maintenance"),
            ("Auto Install", "Bulk install popular software packages"),
            ("Auto Unattend", "Create Windows answer files"),
            ("Real-time Monitoring", "Track CPU, RAM, and disk usage"),
            ("Dark Theme", "Modern Sun Valley dark theme interface"),
            ("User-Friendly", "Clean and intuitive design")
        ]
        
        for title, desc in features:
            feature_frame = ttk.Frame(right_frame)
            feature_frame.pack(fill="x", pady=5)
            
            bullet = ttk.Label(feature_frame, text="•",
                            font=("Segoe UI", 12, "bold"))
            bullet.pack(side="left", padx=(0, 10))
            
            feature_title = ttk.Label(feature_frame, text=title,
                                   font=("Segoe UI", 10, "bold"))
            feature_title.pack(side="left")
            
            feature_desc = ttk.Label(feature_frame, text=f" - {desc}",
                                  font=("Segoe UI", 10))
            feature_desc.pack(side="left", padx=(5, 0))
    
    def run(self):
        """Start the application"""
        try:
            # Initialize monitoring thread
            self.monitoring = True
            self.monitoring_thread = threading.Thread(target=self.update_stats, daemon=True)
            self.monitoring_thread.start()
            
            # Create system tray icon
            self.icon = None
            if os.path.exists("assets/icon.ico"):
                try:
                    image = Image.open("assets/icon.ico")
                    menu = pystray.Menu(
                        pystray.MenuItem("Show", self._show_window),
                        pystray.MenuItem("Exit", self._quit_app)
                    )
                    self.icon = pystray.Icon("MTech WinTool", image, "MTech WinTool", menu)
                    self.icon_thread = threading.Thread(target=self.icon.run, daemon=True)
                    self.icon_thread.start()
                except Exception as e:
                    print(f"Failed to create system tray icon: {e}")
                    self.icon = None
            
            # Start the main event loop
            self.root.mainloop()
            
        except Exception as e:
            print(f"Error running application: {e}")
            self.cleanup()
            raise
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources before exit"""
        try:
            # Set flag to stop background operations
            self.monitoring = False
            
            # Immediately terminate any running processes
            if hasattr(self, 'ohm_process') and self.ohm_process:
                try:
                    self.ohm_process.kill()
                except:
                    pass

            # Force stop system tray icon
            if hasattr(self, 'icon') and self.icon:
                try:
                    self.icon.stop()
                except:
                    pass

            # Quick save of critical data
            try:
                self._save_settings()
                # Only save software status if not skipping
                if not hasattr(self, 'skip_status_save') or not self.skip_status_save:
                    self.save_software_status()
            except:
                pass

            # Get current process ID
            current_pid = os.getpid()
            
            # Use Windows API to terminate the process
            import ctypes
            kernel32 = ctypes.WinDLL('kernel32')
            handle = kernel32.OpenProcess(1, 0, current_pid)
            kernel32.TerminateProcess(handle, 0)
            
        except:
            # If anything fails, still force exit
            os._exit(0)

    def _show_window(self, icon, item):
        """Show the main window from system tray"""
        icon.stop()
        self.root.after(0, self.root.deiconify)

    def _quit_app(self, icon, item):
        """Quit the application from system tray"""
        icon.stop()
        self.root.after(0, self._on_close_button)

    def _on_closing(self, event=None):
        """Legacy close handler for protocol"""
        self._on_close_button()
    
    def _on_close_button(self):
        """Handle window close button click"""
        # Check if status label shows we're checking software or uninstalling
        if (hasattr(self, 'status_label') and 
            hasattr(self.status_label, 'cget') and 
            ('Checking' in self.status_label.cget('text') or 'Uninstalling' in self.status_label.cget('text'))):
            # Show warning if we're checking software status or uninstalling
            if messagebox.askokcancel("Quit", "MTech WinTool is still processing.\nClosing now may lead to inconsistent software status.\nDo you still want to quit?"):
                # Set flag to prevent saving software status
                self.skip_status_save = True
                # Delete software_status.json to force a fresh check next time
                try:
                    if os.path.exists('software_status.json'):
                        os.remove('software_status.json')
                except Exception as e:
                    print(f"Error deleting software_status.json: {str(e)}")
                self.cleanup()
        else:
            # Just cleanup and exit if we're not checking status
            self.cleanup()

    def _on_map(self, event):
        if event.widget is self.root:
            self.root.deiconify()
            self.minimized = False
        
    def _on_unmap(self, event):
        if event.widget is self.root and not self.minimized:
            self.minimized = True
            self.root.withdraw()
            
    def minimize_window(self):
        """Minimize window to tray with first-time notification"""
        if not self.minimized:
            if self.settings.get("show_minimize_message", True):
                result = messagebox.showinfo(
                    "Minimized to Tray",
                    "MTech WinTool will continue running in the system tray.\n" +
                    "Click the tray icon to restore the window.\n\n" +
                    "This message won't show again.",
                    icon="info"
                )
                self.settings["show_minimize_message"] = False
                self._save_settings()
            
            self.root.withdraw()
            self.minimized = True

    def _setup_tray(self):
        # Create tray icon menu
        menu = (
            pystray.MenuItem('Open', self._show_window),
            pystray.MenuItem('Minimize', self.minimize_window),
        )
        
        try:
            # Try to load the icon
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
            else:
                # Create a default icon (16x16 black square)
                icon_image = Image.new('RGB', (16, 16), 'black')
            
            # Create the icon
            self.icon = pystray.Icon(
                "MTechWinTool",
                icon_image,
                "MTech WinTool",
                menu
            )
            
            # Start the icon
            self.icon.run_detached()
        except Exception as e:
            print(f"Failed to create tray icon: {str(e)}")
            self.icon = None
    
    def _load_settings(self):
        """Load application settings from settings.json"""
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        self.settings = {
            "show_minimize_message": True  # Default to show the message
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings.update(json.load(f))
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
            
    def _save_settings(self):
        """Save application settings to settings.json"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")

    def _setup_environment(self):
        """Set up the environment for the application"""
        self._check_winget()
    
    def _init_wmi(self):
        try:
            # Initialize WMI connections
            self.wmi = wmi.WMI()
            
            # Initialize monitoring variables
            self.cpu_temps = []
            self.gpu_temps = []
            
        except Exception as e:
            messagebox.showwarning(
                "WMI Error",
                "Failed to initialize WMI monitoring.\n" +
                "System monitoring features may be limited.\n" +
                f"Error: {str(e)}"
            )
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.software_tree.identify_row(event.y)
        if item and self.software_tree.parent(item):  # Only show menu for software items, not categories
            self.software_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def uninstall_selected_software(self):
        """Uninstall selected software using winget"""
        selected = self.software_tree.selection()
        if not selected:
            messagebox.showinfo("Select Software", "Please select software to uninstall")
            return

        # Get software info
        item = selected[0]
        values = self.software_tree.item(item).get("values", [])
        
        # Skip if it's a category (no values) or not enough values
        if not values:
            return
            
        software_name = values[0]
        
        # Find software ID
        software_id = None
        for category, software_dict in self.SOFTWARE_CATEGORIES.items():
            if software_name in software_dict:
                software_id = software_dict[software_name]['id']
                break
                
        if not software_id:
            return
            
        # Confirm uninstallation
        if not messagebox.askyesno("Confirm Uninstall", 
                                 f"Are you sure you want to uninstall {software_name}?"):
            return
            
        # Create progress window
        progress_window = Toplevel(self.root)
        progress_window.title("Uninstalling Software")
        progress_window.geometry("400x150")
        
        # Center the window
        progress_window.transient(self.root)
        progress_window.grab_set()
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
        progress_window.geometry(f"+{x}+{y}")
        
        # Add progress elements
        frame = ttk.Frame(progress_window, padding="20")
        frame.pack(fill='both', expand=True)
        
        status_label = ttk.Label(frame, text=f"Uninstalling {software_name}...", wraplength=350)
        status_label.pack(fill='x', pady=(0, 10))
        
        progress_bar = ttk.Progressbar(frame, mode='indeterminate', length=350)
        progress_bar.pack(fill='x', pady=(0, 10))
        progress_bar.start(10)
        
        def uninstall_software():
            try:
                # Run winget uninstall with silent mode
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                result = subprocess.run(
                    ["winget", "uninstall", "--silent", "--id", software_id, "--accept-source-agreements"],
                    capture_output=True,
                    text=True,
                    startupinfo=startupinfo,
                    timeout=180  # 3 minute timeout
                )
                
                if result.returncode == 0:
                    # Update status and UI
                    self.update_software_status(software_name, False)
                    status_label.config(text=f"Successfully uninstalled {software_name}")
                    print(f"Successfully uninstalled {software_name}")
                else:
                    error_msg = f"Failed to uninstall {software_name}. Error: {result.stderr}"
                    status_label.config(text=error_msg)
                    print(error_msg)
                    messagebox.showerror("Uninstallation Error", error_msg)
            except subprocess.TimeoutExpired:
                error_msg = f"Uninstallation of {software_name} timed out after 3 minutes"
                status_label.config(text=error_msg)
                print(error_msg)
                messagebox.showerror("Uninstallation Error", error_msg)
            except Exception as e:
                error_msg = f"Error uninstalling {software_name}: {str(e)}"
                status_label.config(text=error_msg)
                print(error_msg)
                messagebox.showerror("Uninstallation Error", error_msg)
            finally:
                # Stop progress and close window
                progress_bar.stop()
                progress_window.after(1500, progress_window.destroy)
        
        # Run uninstallation in a separate thread
        threading.Thread(target=uninstall_software, daemon=True).start()
    
if __name__ == "__main__":
    # First check if winget is installed
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.run(['winget', '--version'], capture_output=True, text=True, startupinfo=startupinfo)
        winget_installed = result.returncode == 0
    except:
        winget_installed = False

    # Use context manager for single instance check
    with SingleInstance("MTechWinTool_Instance") as running:
        if not running:
            messagebox.showwarning("Already Running", "MTech WinTool is already running!")
            sys.exit(0)
        
        # Only show initialization UI if winget is not installed
        if not winget_installed:
            init = InitializationUI()
            if not init.run():
                sys.exit(1)  # Exit if initialization failed
        
        try:
            # Start main app
            app = MTechWinTool()
            app.run()
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)