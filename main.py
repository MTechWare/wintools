#!/usr/bin/env python3
"""
MTechWinTool - Windows System Utility
Version: Beta 0.0.1a

A modern Windows utility for system monitoring and software management.
This application requires administrative privileges for certain operations:
- System monitoring (CPU, Memory, Disk usage)
- Software installation via winget
- Hardware monitoring via OpenHardwareMonitor

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
from PIL import Image
import threading
import time
import wmi
from datetime import datetime
import requests
from tqdm import tqdm
import subprocess
import webbrowser
import json
from bs4 import BeautifulSoup
import zipfile
import pkg_resources
from concurrent.futures import ThreadPoolExecutor, as_completed

class MTechWinTool:
    
    # Software categories and packages
    SOFTWARE_CATEGORIES = {
        "Browsers": {
            "Google Chrome": "Google.Chrome",
            "Mozilla Firefox": "Mozilla.Firefox",
            "Opera GX": "Opera.OperaGX",
            "Opera": "Opera.Opera",
            "Brave": "BraveSoftware.BraveBrowser",
            "Microsoft Edge": "Microsoft.Edge",
            "Vivaldi": "VivaldiTechnologies.Vivaldi"
        },
        "Development": {
            "Visual Studio Code": "Microsoft.VisualStudioCode",
            "Git": "Git.Git",
            "Python": "Python.Python.3.12",
            "Node.js": "OpenJS.NodeJS.LTS",
            "JDK": "Oracle.JDK.21",
            "Docker Desktop": "Docker.DockerDesktop",
            "Postman": "Postman.Postman",
            "MongoDB Compass": "MongoDB.Compass.Full",
            "MySQL Workbench": "Oracle.MySQL.WorkBench",
            "Android Studio": "Google.AndroidStudio",
            "Visual Studio Community": "Microsoft.VisualStudio.2022.Community",
            "GitHub Desktop": "GitHub.GitHubDesktop",
            "HeidiSQL": "HeidiSQL.HeidiSQL",
            "DBeaver": "dbeaver.dbeaver"
        },
        "Code Editors": {
            "IntelliJ IDEA Community": "JetBrains.IntelliJIDEA.Community",
            "PyCharm Community": "JetBrains.PyCharm.Community",
            "Sublime Text": "SublimeHQ.SublimeText.4",
            "Atom": "GitHub.Atom",
            "Notepad++": "Notepad++.Notepad++",
            "WebStorm": "JetBrains.WebStorm",
            "Eclipse": "EclipseAdoptium.Temurin.21.JDK"
        },
        "Utilities": {
            "7-Zip": "7zip.7zip",
            "VLC Media Player": "VideoLAN.VLC",
            "CPU-Z": "CPUID.CPU-Z",
            "GPU-Z": "TechPowerUp.GPU-Z",
            "MSI Afterburner": "MSI.Afterburner",
            "HWiNFO": "REALiX.HWiNFO",
            "PowerToys": "Microsoft.PowerToys",
            "Everything": "voidtools.Everything",
            "TreeSize Free": "JAMSoftware.TreeSize.Free",
            "WinDirStat": "WinDirStat.WinDirStat",
            "Process Explorer": "Microsoft.Sysinternals.ProcessExplorer",
            "Autoruns": "Microsoft.Sysinternals.Autoruns"
        },
        "Media & Design": {
            "Adobe Reader DC": "Adobe.Acrobat.Reader.64-bit",
            "GIMP": "GIMP.GIMP",
            "Blender": "BlenderFoundation.Blender",
            "Audacity": "Audacity.Audacity",
            "OBS Studio": "OBSProject.OBSStudio",
            "Paint.NET": "dotPDN.PaintDotNet",
            "Inkscape": "Inkscape.Inkscape",
            "Kdenlive": "KDE.Kdenlive",
            "HandBrake": "HandBrake.HandBrake",
            "ShareX": "ShareX.ShareX"
        },
        "Communication": {
            "Microsoft Teams": "Microsoft.Teams",
            "Zoom": "Zoom.Zoom",
            "Slack": "SlackTechnologies.Slack",
            "Discord": "Discord.Discord",
            "Skype": "Microsoft.Skype",
            "Telegram": "Telegram.TelegramDesktop",
            "WhatsApp": "WhatsApp.WhatsApp",
            "Signal": "OpenWhisperSystems.Signal"
        },
        "Security": {
            "Malwarebytes": "Malwarebytes.Malwarebytes",
            "Wireshark": "WiresharkFoundation.Wireshark",
            "Advanced IP Scanner": "Famatech.AdvancedIPScanner",
            "Bitwarden": "Bitwarden.Bitwarden",
            "CCleaner": "Piriform.CCleaner",
            "Windows Terminal": "Microsoft.WindowsTerminal",
            "OpenVPN": "OpenVPNTechnologies.OpenVPN",
            "KeePass": "DominikReichl.KeePass",
            "Glasswire": "GlassWire.GlassWire",
            "Cryptomator": "Cryptomator.Cryptomator"
        },
        "Gaming": {
            "Steam": "Valve.Steam",
            "Epic Games Launcher": "EpicGames.EpicGamesLauncher",
            "GOG Galaxy": "GOG.Galaxy",
            "Xbox": "Microsoft.Xbox",
            "Ubisoft Connect": "Ubisoft.Connect",
            "EA App": "ElectronicArts.EADesktop",
            "Battle.net": "Blizzard.BattleNet",
            "PlayStation": "PlayStation.PSRemotePlay"
        }
    }

    def __init__(self):
        # Initialize automated setup
        self._setup_environment()
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._setup_window()
        
        # Initialize monitoring variables
        self.monitoring = True
        self.is_maximized = False
        
        # Initialize WMI
        self._init_wmi()
        
        # Create UI components
        self._create_title_bar()
        self._create_main_container()
        self._create_tabs()
        
        # Start monitoring thread
        self._start_monitoring()

    def _setup_window(self):
        self.root.title("MTech Applcation")
        
        # Set window size and center it
        window_width = 1024
        window_height = 768
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.minsize(800, 600)
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Apply theme
        sv_ttk.set_theme("dark")
        self._configure_styles()

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

    def _setup_environment(self):
        try:
            self._setup_openhardwaremonitor()
            self._check_winget()
            self._install_required_packages()
        except Exception as e:
            messagebox.showwarning(
                "Setup Error",
                f"Error during automatic setup:\n{str(e)}\n" +
                "Some features may not work properly."
            )

    def _setup_openhardwaremonitor(self):
        ohm_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "OpenHardwareMonitor")
        ohm_zip = os.path.join(ohm_dir, "OpenHardwareMonitor.zip")
        ohm_exe = os.path.join(ohm_dir, "OpenHardwareMonitor.exe")
        
        # Extract if needed
        if not os.path.exists(ohm_exe) and os.path.exists(ohm_zip):
            with zipfile.ZipFile(ohm_zip, 'r') as zip_ref:
                zip_ref.extractall(ohm_dir)
        
        # Start if not running
        ohm_running = any(proc.info['name'].lower() == 'openhardwaremonitor.exe' 
                         for proc in psutil.process_iter(['name']))
        
        if not ohm_running and os.path.exists(ohm_exe):
            try:
                # Try to run with admin privileges
                subprocess.run(["powershell", "Start-Process", ohm_exe, "-Verb", "RunAs"],
                             creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(3)  # Give OHM more time to start and initialize
            except Exception as e:
                messagebox.showwarning(
                    "Hardware Monitoring",
                    "Failed to start OpenHardwareMonitor with admin rights.\n" +
                    "CPU temperatures will not be available.\n" +
                    f"Error: {str(e)}"
                )

    def _check_winget(self):
        try:
            subprocess.run(['winget', '--version'], 
                         capture_output=True, 
                         text=True, 
                         creationflags=subprocess.CREATE_NO_WINDOW)
        except FileNotFoundError:
            messagebox.showwarning(
                "Winget Not Found",
                "The Windows Package Manager (winget) is not installed.\n" +
                "Some features may not work properly.\n" +
                "Please install the latest version of App Installer from the Microsoft Store."
            )

    def _install_required_packages(self):
        requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
        if not os.path.exists(requirements_path):
            return
            
        try:
            required = {}
            with open(requirements_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '==' in line:
                            pkg, ver = line.split('==')
                            required[pkg] = ver
                        else:
                            required[line] = None
            
            installed = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
            missing = []
            
            for pkg, ver in required.items():
                if pkg not in installed or (ver and installed[pkg] != ver):
                    missing.append(line)
            
            if missing:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path],
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            messagebox.showwarning(
                "Package Installation Error",
                f"Error installing required packages:\n{str(e)}\n" +
                "Some features may not work properly."
            )

    def _init_wmi(self):
        try:
            self.wmi = wmi.WMI()
            # Try multiple times to connect to OpenHardwareMonitor
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    self.wmi_hardware = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                    # Test the connection by trying to get sensors
                    self.wmi_hardware.Sensor()
                    return  # Success, exit the function
                except Exception:
                    if attempt < max_attempts - 1:
                        time.sleep(2)  # Wait before retrying
                    continue
            
            # If we get here, all attempts failed
            raise Exception("Failed to connect to OpenHardwareMonitor after multiple attempts")
            
        except Exception as e:
            messagebox.showwarning(
                "Hardware Monitoring",
                "OpenHardwareMonitor is not running or accessible.\n" +
                "CPU temperatures will not be available.\n" +
                "Please run the application as administrator for full hardware monitoring."
            )
            self.wmi_hardware = None

    def _create_title_bar(self):
        title_bar = ttk.Frame(self.root)
        title_bar.pack(fill="x", pady=0)
        
        # Title section
        title_frame = ttk.Frame(title_bar)
        title_frame.pack(side="left", fill="y", padx=(5, 0))
        
        # Title text
        title_text = ttk.Label(title_frame, 
                             text="MTech Applcation", 
                             font=("Segoe UI", 10))
        title_text.pack(side="left", padx=(5, 10), pady=3)
        
        # Window controls
        controls_frame = ttk.Frame(title_bar)
        controls_frame.pack(side="right", fill="y")
        
        ttk.Button(controls_frame, 
                  text="─", 
                  width=2,
                  style="MinMax.TButton",
                  command=self.root.iconify).pack(side="left", padx=1, pady=1)
        
        ttk.Button(controls_frame, 
                  text="□", 
                  width=2,
                  style="MinMax.TButton",
                  command=self.toggle_maximize).pack(side="left", padx=1, pady=1)
        
        ttk.Button(controls_frame, 
                  text="×", 
                  width=2,
                  style="MinMax.TButton",
                  command=self.root.quit).pack(side="left", padx=1, pady=1)
        
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
        
        ttk.Label(header_frame, 
                 text="MTech WinTool", 
                 font=("Segoe UI", 24, "bold")).pack(side="left")

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
                btn = ttk.Button(tool_frame, text="Launch", command=command, style="Accent.TButton")
            else:
                btn = ttk.Button(tool_frame, text="Launch", 
                               command=lambda cmd=command: os.system(cmd), 
                               style="Accent.TButton")
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
        
        # Refresh status button
        refresh_btn = ttk.Button(header_frame, text="Refresh Status", 
                               command=self.refresh_software_status)
        refresh_btn.pack(side="right", padx=(0, 10))
        
        install_btn = ttk.Button(header_frame, text="Install Selected", 
                               command=self.install_selected_software,
                               style="Accent.TButton")
        install_btn.pack(side="right")
        
        # Create Treeview with style
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        
        columns = ("Software", "Status", "Description")
        self.software_tree = ttk.Treeview(right_frame, columns=columns, show="tree headings", style="Treeview")
        
        # Set column headings and widths
        self.software_tree.heading("Software", text="Software")
        self.software_tree.heading("Status", text="Status")
        self.software_tree.heading("Description", text="Description")
        self.software_tree.column("#0", width=120, minwidth=120)  # Tree column (arrow)
        self.software_tree.column("Software", width=150, minwidth=150)
        self.software_tree.column("Status", width=80, minwidth=80)
        self.software_tree.column("Description", width=500, minwidth=300)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.software_tree.yview)
        self.software_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack everything
        self.software_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Software descriptions
        self.software_descriptions = {
            # Browsers
            "Google Chrome": "Fast and popular web browser by Google",
            "Mozilla Firefox": "Privacy-focused web browser with extensive add-ons",
            "Opera GX": "Gaming-focused browser with system optimization",
            "Opera": "Feature-rich browser with built-in VPN",
            "Brave": "Privacy-focused browser with built-in ad blocking",
            "Microsoft Edge": "Modern browser based on Chromium with Windows integration",
            "Vivaldi": "Highly customizable browser with power user features",

            # Development
            "Visual Studio Code": "Lightweight but powerful code editor with extensive extensions",
            "Git": "Distributed version control system",
            "Python": "Popular programming language for various applications",
            "Node.js": "JavaScript runtime for server-side development",
            "JDK": "Java Development Kit for Java applications",
            "Docker Desktop": "Container platform for application development",
            "Postman": "API development and testing platform",
            "MongoDB Compass": "GUI for MongoDB database management",
            "MySQL Workbench": "Visual database design and administration tool",
            "Android Studio": "Official IDE for Android development",
            "Visual Studio Community": "Full-featured IDE for .NET and C++ development",
            "GitHub Desktop": "GitHub client for easy repository management",
            "HeidiSQL": "Lightweight SQL database client",
            "DBeaver": "Universal database tool and SQL client",

            # Code Editors
            "IntelliJ IDEA Community": "Powerful Java IDE with advanced features",
            "PyCharm Community": "Python IDE with intelligent coding assistance",
            "Sublime Text": "Fast and lightweight text editor",
            "Atom": "Hackable text editor for the 21st century",
            "Notepad++": "Enhanced text editor with syntax highlighting",
            "WebStorm": "JavaScript IDE with modern web development tools",
            "Eclipse": "Multi-language development environment",

            # Utilities
            "7-Zip": "File archiver with high compression ratio",
            "VLC Media Player": "Versatile media player supporting various formats",
            "CPU-Z": "System information and CPU monitoring tool",
            "GPU-Z": "Graphics card information and monitoring utility",
            "MSI Afterburner": "Graphics card overclocking and monitoring tool",
            "HWiNFO": "Comprehensive hardware analysis and monitoring tool",
            "PowerToys": "Windows power user productivity tools",
            "Everything": "Ultra-fast file search utility",
            "TreeSize Free": "Disk space management and visualization",
            "WinDirStat": "Disk usage statistics viewer and cleanup tool",
            "Process Explorer": "Advanced task manager and system monitor",
            "Autoruns": "Windows startup program manager",

            # Media & Design
            "Adobe Reader DC": "Industry-standard PDF viewer and tools",
            "GIMP": "Open-source image editor with professional features",
            "Blender": "3D creation suite for modeling, animation, and rendering",
            "Audacity": "Multi-track audio editor and recorder",
            "OBS Studio": "Professional broadcasting and recording software",
            "Paint.NET": "Image and photo editing software",
            "Inkscape": "Professional vector graphics editor",
            "Kdenlive": "Open-source video editor with professional features",
            "HandBrake": "Open-source video transcoder",
            "ShareX": "Screen capture and file sharing tool",

            # Communication
            "Microsoft Teams": "Business communication and collaboration platform",
            "Zoom": "Video conferencing and remote meeting platform",
            "Slack": "Team collaboration and messaging platform",
            "Discord": "Voice, video, and text chat platform",
            "Skype": "Video calls and instant messaging service",
            "Telegram": "Cloud-based messaging app with encryption",
            "WhatsApp": "Popular messaging app with voice and video calls",
            "Signal": "Privacy-focused encrypted messaging app",

            # Security
            "Malwarebytes": "Anti-malware and internet security tool",
            "Wireshark": "Network protocol analyzer for security analysis",
            "Advanced IP Scanner": "Network scanner for security and management",
            "Bitwarden": "Open-source password manager",
            "CCleaner": "System cleaner and optimization tool",
            "Windows Terminal": "Modern terminal application for Windows",
            "OpenVPN": "Secure VPN client for private networking",
            "KeePass": "Local password manager with strong encryption",
            "Glasswire": "Network monitor and security tool",
            "Cryptomator": "Cloud storage encryption tool",

            # Gaming
            "Steam": "Popular gaming platform and store",
            "Epic Games Launcher": "Game store with weekly free games",
            "GOG Galaxy": "DRM-free game platform and launcher",
            "Xbox": "Microsoft's gaming app for PC and cloud gaming",
            "Ubisoft Connect": "Ubisoft's game launcher and store",
            "EA App": "Electronic Arts' game platform",
            "Battle.net": "Blizzard's game launcher and store",
            "PlayStation": "Remote play for PlayStation consoles"
        }
        
        # Add software to tree with categories as parents
        self.category_nodes = {}
        self.software_items = {}  # Store software items for status updates
        
        for category, software_dict in self.SOFTWARE_CATEGORIES.items():
            category_node = self.software_tree.insert("", "end", text=category, open=True)
            self.category_nodes[category] = category_node
            
            for software_name in software_dict:
                description = self.software_descriptions.get(software_name, "")
                item = self.software_tree.insert(category_node, "end", 
                                              values=(software_name, "Checking...", description))
                self.software_items[software_name] = item
        
        # Bind double-click to toggle category expansion
        self.software_tree.bind("<Double-1>", self.toggle_category)
        
        # Start checking software status in background silently
        self._status_check_thread = threading.Thread(target=self.refresh_software_status, daemon=True)
        self._status_check_thread.start()
    
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
                                style="Accent.TButton",
                                width=20)
        generate_btn.pack(side="right")

        # Configure style for accent button
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        
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
    
    def check_software_status(self, software_name):
        try:
            # Find the category and ID for the software
            software_id = None
            for category, software_dict in self.SOFTWARE_CATEGORIES.items():
                if software_name in software_dict:
                    software_id = software_dict[software_name]
                    break
            
            if not software_id:
                return "Unknown"

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                ["winget", "list", "--id", software_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                text=True
            )
            output, _ = process.communicate()
            return "Available" if process.returncode != 0 else "Installed"
        except Exception as e:
            print(f"Error checking {software_name}: {str(e)}")
            return "Unknown"
    
    def refresh_software_status(self):
        """Refresh all software status in parallel"""
        import queue
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Create a queue for UI updates
        update_queue = queue.Queue()
        
        def update_status(category, software_name):
            try:
                status = self.check_software_status(software_name)
                update_queue.put((software_name, status))
                return software_name, status
            except Exception as e:
                print(f"Error checking {software_name}: {str(e)}")
                update_queue.put((software_name, "Unknown"))
                return software_name, "Unknown"
        
        def process_updates():
            try:
                while True:
                    # Check for updates without blocking
                    try:
                        software_name, status = update_queue.get_nowait()
                        if software_name in self.software_items:
                            item = self.software_items[software_name]
                            self.software_tree.set(item, "Status", status)
                        update_queue.task_done()
                    except queue.Empty:
                        break
                    
                # Schedule next update if executor is still running
                if not executor._shutdown:
                    self.root.after(100, process_updates)
            except Exception as e:
                print(f"Error in UI update: {str(e)}")
        
        # Create a list of all software to check
        tasks = []
        for category, software_dict in self.SOFTWARE_CATEGORIES.items():
            for software_name in software_dict:
                tasks.append((category, software_name))
        
        # Clear current status
        for software_name in self.software_items:
            item = self.software_items[software_name]
            self.software_tree.set(item, "Status", "Checking...")
        
        # Use ThreadPoolExecutor to run checks in parallel
        executor = ThreadPoolExecutor(max_workers=10)
        futures = [executor.submit(update_status, category, software_name) 
                  for category, software_name in tasks]
        
        # Start processing UI updates
        self.root.after(100, process_updates)
        
        # Start a separate thread to handle completion
        def cleanup():
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in thread: {str(e)}")
            executor.shutdown()
        
        threading.Thread(target=cleanup, daemon=True).start()
    
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
                description = values[2].lower()
                
                if search_text in software_name or search_text in description:
                    show_category = True
                    break
            
            if show_category:
                self.software_tree.reattach(node, "", "end")
    
    def install_selected_software(self):
        selected = self.software_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select software to install")
            return
        
        for item in selected:
            category, software_name = self.software_tree.item(item)["values"]
            winget_id = self.SOFTWARE_CATEGORIES[category][software_name]
            try:
                subprocess.run(["winget", "install", "-e", "--id", winget_id])
            except Exception as e:
                messagebox.showerror("Installation Error", 
                                   f"Failed to install {software_name}: {str(e)}")
    
    def update_stats(self):
        temp_update_counter = 0     # Counter for temperature updates
        while self.monitoring:
            try:
                # Update CPU usage
                cpu_percent = psutil.cpu_percent()
                
                # Update Memory usage
                memory = psutil.virtual_memory()
                
                # Update Disk usage
                disk = psutil.disk_usage('/')
                
                # Update CPU temperature if available (every 10 seconds)
                temp_update_counter += 1
                if hasattr(self, 'wmi_hardware') and self.wmi_hardware and temp_update_counter >= 10:
                    try:
                        temperature_infos = self.wmi_hardware.Sensor()
                        for sensor in temperature_infos:
                            if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                                if hasattr(self, 'cpu_temp_label'):
                                    self.cpu_temp_label.configure(text=f"{sensor.Value:.1f}°C")
                                    self.cpu_temp_progress['value'] = sensor.Value
                                break
                        temp_update_counter = 0
                    except Exception:
                        # Silently handle temperature reading errors
                        if hasattr(self, 'cpu_temp_label'):
                            self.cpu_temp_label.configure(text="N/A")
                            self.cpu_temp_progress['value'] = 0
                
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
    
    def toggle_network_fields(self):
        state = "disabled" if self.network_type_var.get() == "dhcp" else "normal"
        for entry in [self.ip_entry, self.subnet_entry, self.gateway_entry, self.dns_entry]:
            entry.configure(state=state)
    
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
        
        # App name
        app_name = ttk.Label(left_frame, text="MTech WinTool", 
                           font=("Segoe UI", 24, "bold"))
        app_name.pack(pady=(0, 10))
        
        # Version
        version = ttk.Label(left_frame, text="Beta Version 0.0.1a", 
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
        self.root.mainloop()

    def on_closing(self):
        try:
            # Stop monitoring thread if running
            if hasattr(self, '_monitoring_thread') and self._monitoring_thread and self._monitoring_thread.is_alive():
                self._stop_monitoring = True
                self._monitoring_thread.join(timeout=1.0)
            
            # Stop any running processes
            if hasattr(self, 'ohm_process') and self.ohm_process:
                try:
                    self.ohm_process.terminate()
                    self.ohm_process.wait(timeout=1.0)
                except:
                    pass
            
            # Destroy the root window
            if self.root:
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            # Force quit if cleanup fails
            if self.root:
                self.root.destroy()

if __name__ == "__main__":
    app = MTechWinTool()
    app.run()