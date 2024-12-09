"""
MTechWinTool - Windows System Utility
Version: Beta 0.0.5a

A modern Windows utility for system monitoring and software management.
This application might require administrative privileges for certain operations:
- System monitoring (CPU, Memory, Disk usage)
- Software installation via winget

Note: This application may be flagged by antivirus software due to its
system monitoring capabilities. This is a false positive. The source code
is open and can be verified for safety.

Author: MTechWare
License: MIT
Repository: https://github.com/MTechWare/wintools
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sv_ttk
import threading
import queue
from package_operations import PackageOperations
from system_health import SystemHealth
from system_tools import SystemTools
from unattend_creator import UnattendCreator
import os
import sys
import platform
from datetime import datetime
import subprocess
from system_tweaks import (
    SystemTweaks, PerformanceTweaks, PrivacyTweaks, DesktopTweaks,
    GamingTweaks, PowerTweaks, NetworkTweaks, MaintenanceTweaks
)
import ctypes
import logging
import webbrowser

class WinGetInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("Initializing")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)  # Make window stay on top
        
        # Handle icon path for both development and bundled executable
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(base_path, 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Set window size and center it
        window_width = 400
        window_height = 250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Apply Sun Valley theme
        sv_ttk.set_theme("dark")
        self.style = ttk.Style()
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(self.root, padding="15 15 15 15")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Title label with custom font and orange color
        self.title_label = ttk.Label(
            self.main_frame,
            text="MTech WinTool Setup",
            font=("Segoe UI", 14, "bold"),
            foreground="#ff6b00"
        )
        self.title_label.grid(row=0, column=0, pady=(0, 15), sticky="n")
        
        # Subtitle with description
        self.subtitle = ttk.Label(
            self.main_frame,
            text="Installing WinGet Package Manager",
            font=("Segoe UI", 10),
            wraplength=350
        )
        self.subtitle.grid(row=1, column=0, pady=(0, 5), sticky="n")
        
        # Status frame
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.grid(row=2, column=0, pady=20, sticky="nsew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        # Status label with icon
        self.status_label = ttk.Label(
            self.status_frame,
            text="🔍 Checking WinGet installation...",
            font=("Segoe UI", 10),
            foreground="#ff6b00"
        )
        self.status_label.grid(row=0, column=0, pady=(0, 10), sticky="n")
        
        # Progress bar with custom style
        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#2b2b2b',
            background='#ff6b00',
            darkcolor='#ff6b00',
            lightcolor='#ff6b00'
        )
        self.progress = ttk.Progressbar(
            self.status_frame,
            mode="indeterminate",
            style="Custom.Horizontal.TProgressbar",
            length=250
        )
        self.progress.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        
        # Info text
        self.info_text = ttk.Label(
            self.main_frame,
            text="This setup will install the Windows Package Manager (WinGet)\nrequired for MTech WinTool to function properly.",
            font=("Segoe UI", 9),
            justify="center",
            wraplength=350
        )
        self.info_text.grid(row=3, column=0, pady=(0, 15), sticky="n")
        
        # Start checking WinGet
        self.check_winget()
    
    def check_winget(self):
        """Check if WinGet is installed"""
        try:
            subprocess.run(['winget', '--version'], capture_output=True, text=True)
            self.winget_found()
        except FileNotFoundError:
            self.winget_not_found()
    
    def winget_found(self):
        """Called when WinGet is found"""
        self.progress.stop()
        self.progress.grid_forget()
        self.status_label.configure(text="✅ WinGet is installed", foreground="green")
        # Wait
        self.root.after(100, self.continue_to_app)
        
    def winget_not_found(self):
        """Called when WinGet is not found"""
        self.progress.stop()
        self.progress.grid_forget()
        self.status_label.configure(text="⚠️ WinGet not found. Installing...", foreground="orange")
        self.progress.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        self.progress.start()
        threading.Thread(target=self.install_winget, daemon=True).start()
    
    def install_winget(self):
        """Install WinGet"""
        try:
            # PowerShell script to download and install WinGet
            ps_script = '''
            $progressPreference = 'silentlyContinue'
            $latestWinGet = Invoke-RestMethod https://api.github.com/repos/microsoft/winget-cli/releases/latest
            $latestWinGetMsixBundleUri = $latestWinGet.assets.browser_download_url | Where-Object { $_.EndsWith(".msixbundle") }
            
            # Download WinGet
            Write-Host "Downloading WinGet..."
            Invoke-WebRequest -Uri $latestWinGetMsixBundleUri -OutFile "$env:TEMP\Microsoft.DesktopAppInstaller.msixbundle"
            
            # Download required dependencies
            Write-Host "Downloading dependencies..."
            $vcLibsUri = "https://aka.ms/Microsoft.VCLibs.x64.14.00.Desktop.appx"
            $uiLibsUri = "https://github.com/microsoft/microsoft-ui-xaml/releases/download/v2.7.3/Microsoft.UI.Xaml.2.7.x64.appx"
            
            Invoke-WebRequest -Uri $vcLibsUri -OutFile "$env:TEMP\Microsoft.VCLibs.x64.14.00.Desktop.appx"
            Invoke-WebRequest -Uri $uiLibsUri -OutFile "$env:TEMP\Microsoft.UI.Xaml.2.7.appx"
            
            # Install dependencies first
            Write-Host "Installing dependencies..."
            Add-AppxPackage -Path "$env:TEMP\Microsoft.VCLibs.x64.14.00.Desktop.appx"
            Add-AppxPackage -Path "$env:TEMP\Microsoft.UI.Xaml.2.7.appx"
            
            # Install WinGet
            Write-Host "Installing WinGet..."
            Add-AppxPackage -Path "$env:TEMP\Microsoft.DesktopAppInstaller.msixbundle"
            Write-Host "Installation complete"
            '''
            
            self.status_label.configure(text="⬇Downloading WinGet and dependencies...")
            # Save script to temp file and execute
            script_path = os.path.join(os.environ['TEMP'], 'install_winget.ps1')
            with open(script_path, 'w') as f:
                f.write(ps_script)
            
            # Run PowerShell with execution policy bypass
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            subprocess.run([
                'powershell.exe',
                '-ExecutionPolicy', 'Bypass',
                '-NoProfile',
                '-WindowStyle', 'Hidden',
                '-File', script_path
            ], capture_output=True, text=True, check=True, startupinfo=startupinfo)
            
            # Clean up temp files
            os.remove(script_path)
            
            # Check if installation was successful
            self.root.after(500, self.check_winget)
            
        except subprocess.CalledProcessError as e:
            self.progress.stop()
            self.progress.grid_forget()
            error_msg = e.stderr if e.stderr else str(e)
            self.status_label.configure(text="❌ Installation failed: PowerShell error", foreground="red")
            print(f"PowerShell Error: {error_msg}")  # For debugging
            # Try again after 3 seconds
            self.root.after(3000, self.check_winget)
        except Exception as e:
            self.progress.stop()
            self.progress.grid_forget()
            self.status_label.configure(text=f"❌ Installation failed: {str(e)}", foreground="red")
            print(f"Error: {str(e)}")  # For debugging
            # Try again after 3 seconds
            self.root.after(3000, self.check_winget)
    
    def continue_to_app(self):
        """Continue to main application"""
        # Remove all widgets from root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Start main application with same root
        app = WinTool(self.root)
        app.run()
    
    def run(self):
        self.root.mainloop()

class WinTool:
    def __init__(self, root=None):
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
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
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
            
        self.root.title("MTech WinTool")
        self.root.attributes('-topmost', False)  # Make window stay on top
        self.root.overrideredirect(True)  # Remove default title bar
        
        # Create custom title bar
        title_bar = ttk.Frame(self.root)
        title_bar.pack(fill=tk.X, expand=False)

        # Configure styles
        style = ttk.Style()
        style.configure('TitleButton.TButton', 
                       font=("Segoe UI", 10),
                       padding=0,
                       background='#1c1c1c',
                       foreground='white')
        
        #title_label = ttk.Label(title_bar, text=" MTech WinTool | Version Beta 0.0.5a | https://mtech.glitch.me/wintool.html", font=("Segoe UI", 10, "bold"), foreground='#ff6b00')
        #title_label.pack(side=tk.LEFT, padx=(2, 5))
        
        # Bind dragging events to title label
        #title_label.bind('<Button-1>', self.start_move)
        #title_label.bind('<B1-Motion>', self.on_move)
        
        # Add minimize and close buttons with matching background
        close_button = tk.Button(title_bar, text="✕", width=2, 
                               command=self.root.destroy,
                               font=("Segoe UI", 10),
                               fg='white',
                               bg='#1c1c1c',
                               relief='flat',
                               bd=0)
        close_button.pack(side=tk.RIGHT, padx=(0, 2))
        
        # Add hover effect for close button
        def on_enter(e):
            close_button.config(fg='red')
        def on_leave(e):
            close_button.config(fg='white')
        
        close_button.bind('<Enter>', on_enter)
        close_button.bind('<Leave>', on_leave)
        
        minimize_button = tk.Button(title_bar, text="─", width=2,
                                  command=self.root.iconify,
                                  font=("Segoe UI", 10),
                                  fg='white',
                                  bg='#1c1c1c',
                                  relief='flat',
                                  bd=0)
        minimize_button.pack(side=tk.RIGHT, padx=(0, 0))
        
        # Make window draggable
        title_bar.bind('<Button-1>', self.start_move)
        title_bar.bind('<B1-Motion>', self.do_move)
        
        # Configure style for custom title bar
        style.configure('TitleBar.TFrame', background='#1c1c1c')
        style.configure('TitleBar.TLabel', background='#1c1c1c', foreground='white')
        style.configure('TitleBar.TButton', padding=0)
        
        # Handle icon path for both development and bundled executable
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(base_path, 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Set window size and center it
        window_width = 1000
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.root.minsize(800, 600)
        
        # Apply Sun Valley theme
        sv_ttk.set_theme("dark")
        
        # Initialize components
        self.pkg_ops = PackageOperations()
        self.sys_health = SystemHealth(self.update_dashboard_metrics)
        self.sys_tools = SystemTools()
        self.unattend_creator = UnattendCreator()
        self.status_queue = queue.Queue()
        self.tweak_frames = []  # Initialize tweak_frames list
        
        # Initialize tweak components
        self.performance_tweaks = PerformanceTweaks()
        self.privacy_tweaks = PrivacyTweaks()
        self.desktop_tweaks = DesktopTweaks()
        self.power_tweaks = PowerTweaks()
        self.gaming_tweaks = GamingTweaks()
        self.network_tweaks = NetworkTweaks()
        self.maintenance_tweaks = MaintenanceTweaks()
        
        # Dictionary to store tweak functions
        self.tweak_functions = {}
        
        # Setup UI first
        self.setup_ui()
        
        # Start system health monitoring
        self.sys_health.start_monitoring()
        
        # Start the queue processor
        self.process_queue()
        
        # Load packages asynchronously
        threading.Thread(target=self.initial_package_load, daemon=True).start()

    def setup_ui(self):
        # Create style
        style = ttk.Style()
        style.configure("Search.TFrame", padding=10)
        style.configure("Content.TFrame", padding=10)
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 10))
        style.configure("Category.Treeview", rowheight=30)
        style.configure("Action.TButton", padding=5)
        style.configure("Tool.TButton", padding=10)
        style.configure("Installed.TLabel", foreground="green")
        style.configure("NotInstalled.TLabel", foreground="gray")
        style.configure("NeedsUpdate.TLabel", foreground="orange")
        style.configure("About.TLabel", font=("Segoe UI", 10))
        style.configure("AboutTitle.TLabel", font=("Segoe UI", 14, "bold"), foreground='#ff6b00')  # Orange color
        style.configure("Dashboard.TFrame", padding=10)
        style.configure("DashboardTitle.TLabel", font=("Segoe UI", 16, "bold"), foreground='#ff6b00')  # Match the orange color
        style.configure("DashboardSubtitle.TLabel", font=("Segoe UI", 12))
        style.configure("DashboardCard.TFrame", padding=15)
        style.configure("DashboardMetric.TLabel", font=("Segoe UI", 24, "bold"))
        style.configure("DashboardText.TLabel", font=("Segoe UI", 10))
        style.configure("DashboardSubtext.TLabel", font=("Segoe UI", 9))
        style.configure("DashboardAction.TButton", padding=10)
        
        # Configure notebook tab style for better width and appearance
        style.configure('TNotebook.Tab', padding=(12, 5))
        style.layout('TNotebook.Tab', [('Notebook.tab', {'sticky': 'nswe', 'children':
            [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
                [('Notebook.label', {'side': 'top', 'sticky': ''})],
            })],
        })])
        
        # Configure tag colors for treeview
        self.tree_tags = {
            'installed': 'green',
            'not_installed': 'white',
            'needs_update': 'orange'
        }
        
        # Add gradient header
        header_frame = tk.Frame(self.root, height=40, bg='#1c1c1c')
        header_frame.pack(fill=tk.X)
        
        # Make header draggable
        header_frame.bind('<Button-1>', self.start_move)
        header_frame.bind('<B1-Motion>', self.on_move)
        
        header_label = ttk.Label(header_frame, 
                               text="MTech Windows Utility",
                               font=("Segoe UI", 16, "bold"),
                               foreground='white',
                               background='#1c1c1c')
        header_label.pack(pady=(5, 0))
        
        # Make header label draggable
        header_label.bind('<Button-1>', self.start_move)
        header_label.bind('<B1-Motion>', self.on_move)
        
        subtitle_label = ttk.Label(header_frame,
                                text="MTech WinTool | Version Beta 0.0.5a | https://mtech.glitch.me/wintool.html",
                                font=("Segoe UI", 9),
                                foreground='#ff6b00',
                                background='#1c1c1c')
        subtitle_label.pack(pady=(0, 5))
        
        # Make subtitle label draggable
        subtitle_label.bind('<Button-1>', self.start_move)
        subtitle_label.bind('<B1-Motion>', self.on_move)
        
        # Add separator under header
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill=tk.X)
        
        # Create main content frame with draggable background
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Make content frame draggable
        self.content_frame.bind('<Button-1>', self.start_move)
        self.content_frame.bind('<B1-Motion>', self.on_move)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)  # Remove padding
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # Create tabs
        self.setup_dashboard_tab()  # Add dashboard as first tab
        self.setup_packages_tab()
        self.setup_tweaks_tab()
        self.setup_monitor_tab()
        self.setup_tools_tab()
        self.setup_unattend_tab()
        self.setup_about_tab()

    def setup_packages_tab(self):
        packages_tab = ttk.Frame(self.notebook, padding="20 10 20 10")
        self.notebook.add(packages_tab, text="📦 Packages")
        
        # Header frame with status
        header_frame = ttk.Frame(packages_tab)
        header_frame.pack(fill=tk.X, pady=(10, 20))
        
        title_label = ttk.Label(header_frame, text="WinGet Package Manager (Hold Ctrl + Left Click to select)", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Make title label draggable
        title_label.bind('<Button-1>', self.start_move)
        title_label.bind('<B1-Motion>', self.on_move)
        
        # Status frame
        self.status_frame = ttk.Frame(header_frame)
        self.status_frame.pack(side=tk.RIGHT)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", style="Status.TLabel")
        self.status_label.pack(side=tk.RIGHT)
        
        # Make status label draggable
        self.status_label.bind('<Button-1>', self.start_move)
        self.status_label.bind('<B1-Motion>', self.on_move)
        
        self.progress_bar = ttk.Progressbar(self.status_frame, mode='indeterminate', length=100)
        
        # Search frame with modern styling
        search_frame = ttk.Frame(packages_tab, style="Search.TFrame")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_label = ttk.Label(search_frame, text="🔍", font=("Segoe UI", 12))
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Make search label draggable
        search_label.bind('<Button-1>', self.start_move)
        search_label.bind('<B1-Motion>', self.on_move)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_packages)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 10))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add category filter dropdown
        category_frame = ttk.Frame(search_frame)
        category_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT, padx=(0, ))
        self.category_var = tk.StringVar(value="All")
        self.category_dropdown = ttk.Combobox(category_frame, textvariable=self.category_var, state="readonly", width=15)
        self.category_dropdown.pack(side=tk.LEFT)
        self.category_dropdown.bind('<<ComboboxSelected>>', self.filter_packages)
        
        # Stats frame
        stats_frame = ttk.Frame(packages_tab)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="", style="Header.TLabel")
        self.stats_label.pack(side=tk.LEFT)
        
        # Make stats label draggable
        self.stats_label.bind('<Button-1>', self.start_move)
        self.stats_label.bind('<B1-Motion>', self.on_move)
        
        # Package list with improved styling
        list_frame = ttk.Frame(packages_tab, style="Content.TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview with columns
        self.tree = ttk.Treeview(list_frame, show='tree headings', style="Category.Treeview")
        self.tree['columns'] = ('status', 'description')
        self.tree.heading('status', text='Status')
        self.tree.heading('description', text='Description')
        self.tree.column('status', width=100)
        self.tree.column('description', width=300)
        
        # Configure tag colors
        for tag, color in self.tree_tags.items():
            self.tree.tag_configure(tag, foreground=color)
            
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Grid layout for better organization
        self.tree.grid(row=0, column=0, sticky='nsew')
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Action buttons frame with modern styling
        button_frame = ttk.Frame(packages_tab)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Left-side buttons
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        install_btn = ttk.Button(left_buttons, text="📦 Install", command=self.install_package, style="Action.TButton", width=15)
        install_btn.pack(side=tk.LEFT, padx=5)
        
        uninstall_btn = ttk.Button(left_buttons, text="❌ Uninstall", command=self.uninstall_package, style="Action.TButton", width=15)
        uninstall_btn.pack(side=tk.LEFT, padx=5)
        
        update_btn = ttk.Button(left_buttons, text="🔄 Update", command=self.update_package, style="Action.TButton", width=15)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # Right-side buttons
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        refresh_btn = ttk.Button(right_buttons, text="🔄 Refresh", command=self.refresh_packages, style="Action.TButton", width=15)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Bind events
        self.tree.bind('<<TreeviewOpen>>', self.on_category_open)
        self.tree.bind('<<TreeviewClose>>', self.on_category_close)
        self.tree.bind('<Double-1>', self.on_item_double_click)

    def setup_monitor_tab(self):
        monitor_tab = ttk.Frame(self.notebook, padding="20 10 20 10")
        self.notebook.add(monitor_tab, text="📊 Monitor")
        
        # Resource Usage Frame
        resource_frame = ttk.LabelFrame(monitor_tab, text="💻 Resource Usage", padding="15")
        resource_frame.pack(fill=tk.X, pady=(0, 15))

        # CPU Frame
        cpu_frame = ttk.LabelFrame(resource_frame, text="🔲 CPU", padding="10")
        cpu_frame.pack(fill=tk.X, pady=(0, 10))
        
        # CPU Usage
        cpu_usage_frame = ttk.Frame(cpu_frame)
        cpu_usage_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(cpu_usage_frame, text="⚡ Usage:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.cpu_progress = ttk.Progressbar(cpu_usage_frame, mode='determinate', length=200)
        self.cpu_progress.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.cpu_label = ttk.Label(cpu_usage_frame, text="0%", width=8)
        self.cpu_label.pack(side=tk.LEFT, padx=5)

        # CPU Details
        cpu_details_frame = ttk.Frame(cpu_frame)
        cpu_details_frame.pack(fill=tk.X)
        self.cpu_details_label = ttk.Label(cpu_details_frame, text="🔄 Cores: -- | ⚡ Frequency: -- GHz")
        self.cpu_details_label.pack(side=tk.LEFT, padx=5)
        
        # Memory Frame
        memory_frame = ttk.LabelFrame(resource_frame, text="🧠 Memory", padding="10")
        memory_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Memory Usage
        memory_usage_frame = ttk.Frame(memory_frame)
        memory_usage_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(memory_usage_frame, text="📊 Usage:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.memory_progress = ttk.Progressbar(memory_usage_frame, mode='determinate', length=200)
        self.memory_progress.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.memory_label = ttk.Label(memory_usage_frame, text="0%", width=8)
        self.memory_label.pack(side=tk.LEFT, padx=5)

        # Memory Details
        memory_details_frame = ttk.Frame(memory_frame)
        memory_details_frame.pack(fill=tk.X)
        self.memory_details_label = ttk.Label(memory_details_frame, text="💾 Total: -- GB | 📈 Used: -- GB | 📉 Available: -- GB")
        self.memory_details_label.pack(side=tk.LEFT, padx=5)
        
        # Disk Frame
        disk_frame = ttk.LabelFrame(resource_frame, text="💿 Disk", padding="10")
        disk_frame.pack(fill=tk.X)
        
        # Disk Activity
        disk_usage_frame = ttk.Frame(disk_frame)
        disk_usage_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(disk_usage_frame, text="📊 Activity:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.disk_progress = ttk.Progressbar(disk_usage_frame, mode='determinate', length=200)
        self.disk_progress.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.disk_label = ttk.Label(disk_usage_frame, text="0%", width=8)
        self.disk_label.pack(side=tk.LEFT, padx=5)

        # Disk Details
        disk_details_frame = ttk.Frame(disk_frame)
        disk_details_frame.pack(fill=tk.X)
        self.disk_details_label = ttk.Label(disk_details_frame, text="💽 Total: -- GB | 📈 Used: -- GB | 📉 Free: -- GB")
        self.disk_details_label.pack(side=tk.LEFT, padx=5)

        # System Info Frame
        system_frame = ttk.LabelFrame(monitor_tab, text="ℹ️ System Information", padding="15")
        system_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas with scrollbar for system info
        canvas = tk.Canvas(system_frame)
        scrollbar = ttk.Scrollbar(system_frame, orient="vertical", command=canvas.yview)
        self.system_info_frame = ttk.Frame(canvas)

        self.system_info_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.system_info_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_tools_tab(self):
        tools_tab = ttk.Frame(self.notebook, padding="20 10 20 10")
        self.notebook.add(tools_tab, text="🔧 Tools")
        
        # Create a frame for the tools grid
        tools_frame = ttk.LabelFrame(tools_tab, text="🔧 System Tools", padding="15")
        tools_frame.pack(fill=tk.BOTH, expand=True)

        # Create grid of tool buttons
        # Row 1
        self.create_tool_button(tools_frame, "🗑️ Empty Recycle Bin", self.empty_recycle_bin, 0, 0)
        self.create_tool_button(tools_frame, "📊 Task Manager", self.open_task_manager, 0, 1)
        self.create_tool_button(tools_frame, "⚙️ Control Panel", self.open_control_panel, 0, 2)

        # Row 2
        self.create_tool_button(tools_frame, "🖥️ System Settings", self.open_system_settings, 1, 0)
        self.create_tool_button(tools_frame, "🔌 Device Manager", self.open_device_manager, 1, 1)
        self.create_tool_button(tools_frame, "🧹 Disk Cleanup", self.open_disk_cleanup, 1, 2)

        # Row 3
        self.create_tool_button(tools_frame, "🔧 Services", self.open_services, 2, 0)

        # Configure grid
        for i in range(3):
            tools_frame.grid_columnconfigure(i, weight=1)
        for i in range(3):
            tools_frame.grid_rowconfigure(i, weight=1)

        # System cleanup info frame
        cleanup_frame = ttk.LabelFrame(tools_tab, text="🧹 System Cleanup Info", padding="15")
        cleanup_frame.pack(fill=tk.X, pady=(15, 0))

        self.cleanup_label = ttk.Label(cleanup_frame, text="Calculating cleanup size...", justify=tk.LEFT)
        self.cleanup_label.pack(fill=tk.X, padx=5, pady=5)

        # Start updating system info
        self.update_system_info()

    def setup_unattend_tab(self):
        unattend_tab = ttk.Frame(self.notebook, padding="20 10 20 10")
        self.notebook.add(unattend_tab, text="📝 Unattend")
        
        # Create notebook for settings categories
        self.settings_notebook = ttk.Notebook(unattend_tab)
        self.settings_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create all frames first
        self.system_frame = self.create_system_tab()
        self.regional_frame = self.create_regional_tab()
        self.account_frame = self.create_account_tab()
        self.privacy_frame = self.create_privacy_tab()
        self.apps_frame = self.create_apps_tab()

        # Add frames to notebook
        self.settings_notebook.add(self.system_frame, text="💻 System")
        self.settings_notebook.add(self.regional_frame, text="🌍 Regional")
        self.settings_notebook.add(self.account_frame, text="👤 User Account")
        self.settings_notebook.add(self.privacy_frame, text="🔒 Privacy")
        self.settings_notebook.add(self.apps_frame, text="📦 Apps")

        # Navigation buttons frame at the bottom
        nav_frame = ttk.Frame(unattend_tab)
        nav_frame.pack(fill=tk.X, padx=5, pady=10)

        # Back button (hidden initially)
        self.back_btn = ttk.Button(nav_frame, text="← Back", command=self.prev_tab, style='Secondary.TButton')
        self.back_btn.pack(side=tk.LEFT, padx=5)
        self.back_btn.pack_forget()  # Hide initially

        # Next/Finish button
        self.next_btn = ttk.Button(nav_frame, text="Next →", command=self.next_tab, style='Accent.TButton')
        self.next_btn.pack(side=tk.RIGHT, padx=5)

        # Save button (hidden initially)
        self.save_btn = ttk.Button(nav_frame, text="Save Unattend File", command=self.save_unattend, style='Accent.TButton')
        self.save_btn.pack(side=tk.RIGHT, padx=5)
        self.save_btn.pack_forget()  # Hide initially

        # Bind tab change event
        self.settings_notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

    def setup_about_tab(self):
        about_tab = ttk.Frame(self.notebook, padding="20 10 20 10")
        self.notebook.add(about_tab, text="ℹ️ About")
        
        # Create main content frame
        content_frame = ttk.Frame(about_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # App title and version
        title_label = ttk.Label(content_frame, text="MTech WinTool", style="AboutTitle.TLabel")
        title_label.pack(pady=(0, 10))

        version_frame = ttk.Frame(content_frame)
        version_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Features frame
        features_frame = ttk.LabelFrame(content_frame, text="✨ Features", padding=15)
        features_frame.pack(fill=tk.X, pady=(0, 20))

        # Create features with icons
        features_text = [
            "📦 Packages - Software management with WinGet integration",
            "⚡ Tweaks - Performance optimization and privacy settings",
            "📊 Monitor - Real-time system resource tracking",
            "🔧 Tools - Quick access to Windows utilities",
            "📝 Unattend - Custom Windows setup configuration"
        ]

        for feature in features_text:
            feature_label = ttk.Label(features_frame, text=feature, wraplength=400)
            feature_label.pack(anchor=tk.W, pady=2)
        
        # System info frame
        system_frame = ttk.LabelFrame(content_frame, text="System Information", padding=15)
        system_frame.pack(fill=tk.X)

        system_info = f"""💻 OS: {os.name.upper()}
🐍 Python Version: {sys.version.split()[0]}
⚙️ Architecture: {platform.machine()}
🖥️ Platform: {platform.platform()}"""

        system_label = ttk.Label(system_frame, text=system_info, style="About.TLabel", justify=tk.LEFT)
        system_label.pack(anchor="w", padx=10)

        # Credits frame
        credits_frame = ttk.LabelFrame(content_frame, text="Credits", padding=15)
        credits_frame.pack(fill=tk.X, pady=(20, 0))

        # Creator info with link
        creator_frame = ttk.Frame(credits_frame)
        creator_frame.pack(fill=tk.X)
        
        creator_label = ttk.Label(creator_frame, text="Created by: MTechware", font=("Segoe UI", 9))
        creator_label.pack(side=tk.LEFT, padx=(0, 5))
        
        link_label = ttk.Label(creator_frame, 
                             text="Visit Website", 
                             font=("Segoe UI", 9, "underline"),
                             foreground='#ff6b00',
                             cursor="hand2")
        link_label.pack(side=tk.LEFT)
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/MTechWare"))

        # Additional credits
        additional_credits = """Special thanks to:
• ChrisTitusTech for the Winget Applications
• Sun Valley ttk theme"""
        credits_label = ttk.Label(credits_frame, text=additional_credits, style="About.TLabel", justify=tk.LEFT)
        credits_label.pack(anchor="w", padx=10, pady=(10, 0))

    def on_tab_changed(self, event):
        try:
            # Get the widget that triggered the event
            widget = event.widget
            
            # If it's the main notebook
            if widget == self.notebook:
                current_tab = self.notebook.select()
                if not current_tab:  # If no tab is selected, do nothing
                    return
                    
                tab_text = self.notebook.tab(current_tab, "text")
                
                if tab_text.strip() == "⚡ Tweaks":
                    if not ctypes.windll.shell32.IsUserAnAdmin():
                        result = messagebox.askyesno(
                            "Administrator Rights Required",
                            "The Tweaks tab requires administrator rights to function properly. Do you want to restart the application as administrator?"
                        )
                        if result:
                            # Start the elevated process
                            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                            # Destroy the root window and exit
                            self.root.destroy()
                            sys.exit(0)
                        else:
                            # Safely switch back to the dashboard tab
                            self.notebook.select(0)  # Select dashboard tab
                            return
                        
            # If it's the settings notebook (for unattend tab)
            elif hasattr(self, 'settings_notebook') and widget == self.settings_notebook:
                current_tab = self.settings_notebook.select()
                tab_id = self.settings_notebook.index(current_tab)
                total_tabs = self.settings_notebook.index('end')

                # Show/hide back button
                if tab_id > 0:
                    self.back_btn.pack(side=tk.LEFT, padx=5)
                else:
                    self.back_btn.pack_forget()

                # Update next button text and show/hide save button
                if tab_id == total_tabs - 1:  # Last tab
                    self.next_btn.pack_forget()
                    self.save_btn.pack(side=tk.RIGHT, padx=5)
                else:
                    self.save_btn.pack_forget()
                    self.next_btn.pack(side=tk.RIGHT, padx=5)
        except Exception as e:
            print(f"Error in tab change: {e}")
            # Safely switch to dashboard tab if there's an error
            try:
                self.notebook.select(0)
            except:
                pass

    def next_tab(self):
        current_tab = self.settings_notebook.select()
        current_idx = self.settings_notebook.index(current_tab)
        next_idx = current_idx + 1
        if next_idx < self.settings_notebook.index('end'):
            self.settings_notebook.select(next_idx)

    def prev_tab(self):
        current_tab = self.settings_notebook.select()
        current_idx = self.settings_notebook.index(current_tab)
        prev_idx = current_idx - 1
        if prev_idx >= 0:
            self.settings_notebook.select(prev_idx)

    def create_system_tab(self):
        system_frame = ttk.Frame(self.settings_notebook)
        
        system_settings = ttk.LabelFrame(system_frame, text="System Settings", padding="10")
        system_settings.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(system_settings, text="Computer Name:").pack(anchor='w')
        self.computer_name = ttk.Entry(system_settings)
        self.computer_name.pack(fill=tk.X, pady=(0, 5))
        self.computer_name.insert(0, self.unattend_creator.settings['computer_name'])

        ttk.Label(system_settings, text="Organization:").pack(anchor='w')
        self.organization = ttk.Entry(system_settings)
        self.organization.pack(fill=tk.X, pady=(0, 5))
        self.organization.insert(0, self.unattend_creator.settings['organization'])

        ttk.Label(system_settings, text="Owner:").pack(anchor='w')
        self.owner = ttk.Entry(system_settings)
        self.owner.pack(fill=tk.X, pady=(0, 5))
        self.owner.insert(0, self.unattend_creator.settings['owner'])

        ttk.Label(system_settings, text="Product Key:").pack(anchor='w')
        self.product_key = ttk.Entry(system_settings)
        self.product_key.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(system_settings, text="Windows Edition:").pack(anchor='w')
        self.windows_edition = ttk.Combobox(system_settings, values=UnattendCreator.get_windows_editions())
        self.windows_edition.pack(fill=tk.X, pady=(0, 5))
        self.windows_edition.set(self.unattend_creator.settings['windows_edition'])

        return system_frame

    def create_regional_tab(self):
        regional_frame = ttk.Frame(self.settings_notebook)

        regional_settings = ttk.LabelFrame(regional_frame, text="Regional Settings", padding="10")
        regional_settings.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(regional_settings, text="Time Zone:").pack(anchor='w')
        self.timezone = ttk.Combobox(regional_settings, values=UnattendCreator.get_available_timezones())
        self.timezone.pack(fill=tk.X, pady=(0, 5))
        self.timezone.set(self.unattend_creator.settings['timezone'])

        ttk.Label(regional_settings, text="Language:").pack(anchor='w')
        languages = list(UnattendCreator.get_available_languages().values())
        self.language = ttk.Combobox(regional_settings, values=languages)
        self.language.pack(fill=tk.X, pady=(0, 5))
        self.language.set(UnattendCreator.get_available_languages()[self.unattend_creator.settings['language']])

        ttk.Label(regional_settings, text="Keyboard Layout:").pack(anchor='w')
        keyboard_layouts = list(UnattendCreator.get_keyboard_layouts().values())
        self.keyboard_layout = ttk.Combobox(regional_settings, values=keyboard_layouts)
        self.keyboard_layout.pack(fill=tk.X, pady=(0, 5))
        self.keyboard_layout.set(UnattendCreator.get_keyboard_layouts()[self.unattend_creator.settings['keyboard_layout']])

        return regional_frame

    def create_account_tab(self):
        account_frame = ttk.Frame(self.settings_notebook)

        account_settings = ttk.LabelFrame(account_frame, text="User Account Settings", padding="10")
        account_settings.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(account_settings, text="Username:").pack(anchor='w')
        self.username = ttk.Entry(account_settings)
        self.username.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(account_settings, text="Password:").pack(anchor='w')
        self.password = ttk.Entry(account_settings, show="*")
        self.password.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(account_settings, text="Account Type:").pack(anchor='w')
        self.account_type = ttk.Combobox(account_settings, values=['Administrator', 'Standard'])
        self.account_type.pack(fill=tk.X, pady=(0, 5))
        self.account_type.set('Administrator')

        self.auto_logon = tk.BooleanVar(value=False)
        ttk.Checkbutton(account_settings, text="Enable Auto Logon", variable=self.auto_logon).pack(anchor='w', pady=2)

        ttk.Label(account_settings, text="Auto Logon Count:").pack(anchor='w')
        self.auto_logon_count = ttk.Spinbox(account_settings, from_=1, to=999, width=10)
        self.auto_logon_count.pack(fill=tk.X, pady=(0, 5))

        self.disable_admin = tk.BooleanVar(value=False)
        ttk.Checkbutton(account_settings, text="Disable Administrator Account", variable=self.disable_admin).pack(anchor='w', pady=2)

        self.enable_guest = tk.BooleanVar(value=False)
        ttk.Checkbutton(account_settings, text="Enable Guest Account", variable=self.enable_guest).pack(anchor='w', pady=2)

        return account_frame

    def create_privacy_tab(self):
        privacy_frame = ttk.Frame(self.settings_notebook)

        privacy_settings = ttk.LabelFrame(privacy_frame, text="Privacy Settings", padding="10")
        privacy_settings.pack(fill=tk.X, padx=5, pady=5)

        self.disable_telemetry = tk.BooleanVar(value=True)
        ttk.Checkbutton(privacy_settings, text="Disable Telemetry", variable=self.disable_telemetry).pack(anchor='w', pady=2)

        self.disable_cortana = tk.BooleanVar(value=True)
        ttk.Checkbutton(privacy_settings, text="Disable Cortana", variable=self.disable_cortana).pack(anchor='w', pady=2)

        self.disable_consumer = tk.BooleanVar(value=True)
        ttk.Checkbutton(privacy_settings, text="Disable Consumer Features", variable=self.disable_consumer).pack(anchor='w', pady=2)

        self.disable_tips = tk.BooleanVar(value=True)
        ttk.Checkbutton(privacy_settings, text="Disable Windows Tips", variable=self.disable_tips).pack(anchor='w', pady=2)

        self.disable_suggestions = tk.BooleanVar(value=True)
        ttk.Checkbutton(privacy_settings, text="Disable App Suggestions", variable=self.disable_suggestions).pack(anchor='w', pady=2)

        return privacy_frame

    def create_apps_tab(self):
        apps_frame = ttk.Frame(self.settings_notebook)

        apps_settings = ttk.LabelFrame(apps_frame, text="App Settings", padding="10")
        apps_settings.pack(fill=tk.X, padx=5, pady=5)

        self.remove_inbox = tk.BooleanVar(value=True)
        ttk.Checkbutton(apps_settings, text="Remove Inbox Apps", variable=self.remove_inbox).pack(anchor='w', pady=2)

        self.install_winget = tk.BooleanVar(value=True)
        ttk.Checkbutton(apps_settings, text="Install Winget", variable=self.install_winget).pack(anchor='w', pady=2)

        self.install_chocolatey = tk.BooleanVar(value=False)
        ttk.Checkbutton(apps_settings, text="Install Chocolatey", variable=self.install_chocolatey).pack(anchor='w', pady=2)

        self.install_office = tk.BooleanVar(value=False)
        ttk.Checkbutton(apps_settings, text="Install Microsoft Office", variable=self.install_office).pack(anchor='w', pady=2)

        ttk.Label(apps_settings, text="Office Edition:").pack(anchor='w')
        self.office_edition = ttk.Combobox(apps_settings, values=UnattendCreator.get_office_editions())
        self.office_edition.pack(fill=tk.X, pady=(0, 5))
        self.office_edition.set(self.unattend_creator.settings['office_edition'])

        return apps_frame

    def create_tool_button(self, parent, text, command, row, col):
        btn = ttk.Button(parent, text=text, command=command, style="Tool.TButton", width=20)
        btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def empty_recycle_bin(self):
        success, message = self.sys_tools.empty_recycle_bin()
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
        self.update_system_info()

    def open_task_manager(self):
        success, message = self.sys_tools.open_task_manager()
        if not success:
            messagebox.showerror("Error", message)

    def open_control_panel(self):
        success, message = self.sys_tools.open_control_panel()
        if not success:
            messagebox.showerror("Error", message)

    def open_system_settings(self):
        success, message = self.sys_tools.open_system_settings()
        if not success:
            messagebox.showerror("Error", message)

    def open_device_manager(self):
        success, message = self.sys_tools.open_device_manager()
        if not success:
            messagebox.showerror("Error", message)

    def open_disk_cleanup(self):
        success, message = self.sys_tools.open_disk_cleanup()
        if not success:
            messagebox.showerror("Error", message)

    def open_services(self):
        success, message = self.sys_tools.open_services()
        if not success:
            messagebox.showerror("Error", message)

    def update_system_info(self):
        # Update cleanup info
        success, cleanup_info = self.sys_tools.get_disk_cleanup_size()
        if success:
            temp_size = cleanup_info['temp_size'] / (1024 * 1024)  # Convert to MB
            recycle_size = cleanup_info['recycle_bin_size'] / (1024 * 1024)  # Convert to MB
            total_size = cleanup_info['total_size'] / (1024 * 1024)  # Convert to MB
            
            cleanup_text = f"Potential space to clean:\n"
            cleanup_text += f"🗑️ Recycle Bin: {recycle_size:.2f} MB\n"
            cleanup_text += f"📁 Temp Files: {temp_size:.2f} MB\n"
            cleanup_text += f"💾 Total: {total_size:.2f} MB"
            
            self.cleanup_label.configure(text=cleanup_text)

        # Schedule next update
        self.root.after(30000, self.update_system_info)  # Update every 30 seconds

    def update_dashboard_metrics(self, stats):
        """Update the dashboard metrics with current system stats"""
        if not stats:
            return
            
        try:
            # Update CPU
            cpu_percent = stats['cpu_percent']
            cpu_cores = stats['cpu_cores']
            cpu_freq = stats['cpu_frequency'] / 1000  # Convert MHz to GHz
            
            self.dash_cpu_label.configure(text=f"{cpu_percent:.1f}%")
            self.cpu_label.configure(text=f"{cpu_percent:.1f}%")
            self.cpu_progress['value'] = cpu_percent
            self.cpu_details_label.configure(
                text=f"🔄 Cores: {cpu_cores} | ⚡ Frequency: {cpu_freq:.2f} GHz"
            )
            
            # Update Memory
            memory_percent = stats['memory_percent']
            memory_used = stats['memory_used']
            memory_total = stats['memory_total']
            used_gb = memory_used / (1024**3)
            total_gb = memory_total / (1024**3)
            available_gb = (memory_total - memory_used) / (1024**3)
            
            self.dash_memory_label.configure(text=f"{memory_percent:.1f}%")
            self.memory_label.configure(text=f"{memory_percent:.1f}%")
            self.memory_progress['value'] = memory_percent
            self.memory_details_label.configure(
                text=f"💾 Total: {total_gb:.1f} GB | 📈 Used: {used_gb:.1f} GB | 📉 Available: {available_gb:.1f} GB"
            )
            
            # Update Disk
            disk_percent = stats['disk_percent']
            disk_used = stats['disk_used']
            disk_total = stats['disk_total']
            disk_free = stats['disk_free']
            
            # Convert to GB and round to 1 decimal place
            disk_used_gb = round(disk_used / (1024**3), 1)
            disk_total_gb = round(disk_total / (1024**3), 1)
            disk_free_gb = round(disk_free / (1024**3), 1)
            
            self.dash_disk_label.configure(text=f"{disk_percent:.1f}%")
            self.disk_label.configure(text=f"{disk_percent:.1f}%")
            self.disk_progress['value'] = disk_percent
            self.disk_details_label.configure(
                text=f"💽 Total: {disk_total_gb} GB | 📈 Used: {disk_used_gb} GB | 📉 Free: {disk_free_gb} GB"
            )
            
        except Exception as e:
            print(f"Error updating dashboard metrics: {e}")

    def update_status(self, message, show_progress=False):
        """Update the status bar message and progress indicator"""
        self.status_queue.put(("status", message))
        if show_progress:
            self.status_queue.put(("show_progress", None))
        else:
            self.status_queue.put(("hide_progress", None))

    def check_status_updates(self):
        """Check and process any pending status updates"""
        try:
            while True:
                action, data = self.status_queue.get_nowait()
                if action == "status":
                    self.status_label.configure(text=data)
                elif action == "show_progress":
                    self.progress_bar.pack(side=tk.RIGHT, padx=(0, 10))
                    self.progress_bar.start(10)
                elif action == "hide_progress":
                    self.progress_bar.stop()
                    self.progress_bar.pack_forget()
                elif action == "populate_initial":
                    self.filter_packages()
                elif action == "update_package":
                    package_name, is_installed, needs_updating = data
                    self.pkg_ops.installation_status[package_name] = is_installed
                    self.pkg_ops.update_status_dict[package_name] = needs_updating
                    self.filter_packages()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_status_updates)

    def get_selected_package(self):
        selection = self.tree.selection()
        if not selection:
            return None
            
        item = self.tree.item(selection[0])
        if not item:
            return None
            
        # If a category is selected, return None
        parent = self.tree.parent(selection[0])
        if not parent:
            return None
            
        return item['text']

    def install_package(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Package Selected", "Please select one or more packages to install.")
            return
            
        # Get all selected packages that are not categories
        packages_to_install = []
        for item in selected_items:
            # Skip if it's a category (no parent)
            if not self.tree.parent(item):
                continue
                
            package_name = self.tree.item(item)['text']
            # Skip already installed packages
            if self.pkg_ops.installation_status.get(package_name, False):
                messagebox.showinfo("Already Installed", f"{package_name} is already installed.")
                continue
                
            packages_to_install.append(package_name)
            
        if not packages_to_install:
            return
            
        # Confirm installation
        if len(packages_to_install) == 1:
            msg = f"Do you want to install {packages_to_install[0]}?"
        else:
            msg = f"Do you want to install these {len(packages_to_install)} packages?\n\n" + "\n".join(packages_to_install)
            
        if not messagebox.askyesno("Confirm Installation", msg):
            return
            
        # Queue each package for installation
        total_packages = len(packages_to_install)
        current_package = 0
        
        def update_status_with_progress(message, show_progress=False):
            current_nonlocal = getattr(update_status_with_progress, 'current', 0)
            if "Successfully installed" in message:
                current_nonlocal += 1
                setattr(update_status_with_progress, 'current', current_nonlocal)
                progress = int((current_nonlocal / total_packages) * 100)
                self.update_status(f"Installing packages... ({current_nonlocal}/{total_packages}) {progress}% - {message}")
            else:
                self.update_status(message, show_progress)
        
        setattr(update_status_with_progress, 'current', 0)
        
        # Queue installations
        for package in packages_to_install:
            self.pkg_ops.install_package(package, update_status_with_progress)

    def uninstall_package(self):
        package_name = self.get_selected_package()
        if not package_name:
            messagebox.showwarning("No Package Selected", "Please select a package to uninstall.")
            return
            
        if not self.pkg_ops.installation_status.get(package_name, False):
            messagebox.showinfo("Not Installed", f"{package_name} is not installed.")
            return
            
        if messagebox.askyesno("Confirm Uninstall", f"Are you sure you want to uninstall {package_name}?"):
            threading.Thread(target=self.pkg_ops.uninstall_package, args=(package_name, self.update_status), daemon=True).start()

    def update_package(self):
        package_name = self.get_selected_package()
        if not package_name:
            messagebox.showwarning("No Package Selected", "Please select a package to update.")
            return
            
        if not self.pkg_ops.installation_status.get(package_name, False):
            messagebox.showinfo("Not Installed", f"{package_name} is not installed.")
            return
            
        if not self.pkg_ops.update_status_dict.get(package_name, False):
            messagebox.showinfo("No Update Available", f"{package_name} is already up to date.")
            return
            
        threading.Thread(target=self.pkg_ops.update_package, args=(package_name, self.update_status), daemon=True).start()

    def refresh_packages(self):
        """Refresh the package list"""
        self.pkg_ops.refresh_packages(self.update_status, self.status_queue)
        
        # Update category dropdown with available categories
        categories = list(self.pkg_ops.categories.keys())
        categories.sort()
        categories.insert(0, "All")
        self.category_dropdown['values'] = categories

    def on_category_open(self, event):
        item = self.tree.selection()[0]
        self.tree.item(item, open=True)

    def on_category_close(self, event):
        item = self.tree.selection()[0]
        self.tree.item(item, open=False)

    def on_item_double_click(self, event):
        package_name = self.get_selected_package()
        if package_name:
            if not self.pkg_ops.installation_status.get(package_name, False):
                self.install_package()
            elif self.pkg_ops.update_status_dict.get(package_name, False):
                self.update_package()

    def process_queue(self):
        try:
            while True:
                action, data = self.status_queue.get_nowait()
                if action == "status":
                    self.status_label.configure(text=data)
                elif action == "show_progress":
                    self.progress_bar.pack(side=tk.RIGHT, padx=(0, 10))
                    self.progress_bar.start(10)
                elif action == "hide_progress":
                    self.progress_bar.stop()
                    self.progress_bar.pack_forget()
                elif action == "populate_initial":
                    self.filter_packages()
                elif action == "update_package":
                    package_name, is_installed, needs_updating = data
                    self.pkg_ops.installation_status[package_name] = is_installed
                    self.pkg_ops.update_status_dict[package_name] = needs_updating
                    self.filter_packages()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)

    def save_unattend(self):
        self.update_unattend_settings()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
            title="Save Unattend File"
        )
        if file_path:
            success, message = self.unattend_creator.save_unattend_file(file_path)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def update_unattend_settings(self):
        # Get the language code from the display name
        language_dict = UnattendCreator.get_available_languages()
        selected_language = self.language.get()
        language_code = next(code for code, name in language_dict.items() if name == selected_language)

        # Get the keyboard layout code from the display name
        keyboard_dict = UnattendCreator.get_keyboard_layouts()
        selected_layout = self.keyboard_layout.get()
        keyboard_code = next(code for code, name in keyboard_dict.items() if name == selected_layout)

        self.unattend_creator.settings.update({
            # System Settings
            'computer_name': self.computer_name.get(),
            'organization': self.organization.get(),
            'owner': self.owner.get(),
            'product_key': self.product_key.get(),
            'windows_edition': self.windows_edition.get(),
            
            # Regional Settings
            'timezone': self.timezone.get(),
            'language': language_code,
            'input_locale': language_code,
            'system_locale': language_code,
            'user_locale': language_code,
            'keyboard_layout': keyboard_code,
            
            # User Account Settings
            'user_account': self.username.get(),
            'user_password': self.password.get(),
            'user_account_type': self.account_type.get(),
            'auto_logon': self.auto_logon.get(),
            'auto_logon_count': int(self.auto_logon_count.get()),
            'disable_admin_account': self.disable_admin.get(),
            'enable_guest_account': self.enable_guest.get(),
            
            # Privacy Settings
            'disable_telemetry': self.disable_telemetry.get(),
            'disable_cortana': self.disable_cortana.get(),
            'disable_consumer_features': self.disable_consumer.get(),
            'disable_windows_tips': self.disable_tips.get(),
            'disable_app_suggestions': self.disable_suggestions.get(),
            
            # App Settings
            'remove_inbox_apps': self.remove_inbox.get(),
            'install_winget': self.install_winget.get(),
            'install_chocolatey': self.install_chocolatey.get(),
            'install_office': self.install_office.get(),
            'office_edition': self.office_edition.get()
        })

    def create_scrollable_frame(self, parent):
        # Create a canvas and scrollbar
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Configure canvas scrolling with mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind mouse enter/leave events to manage mousewheel scrolling
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scrollable_frame

    def setup_tweaks_tab(self):
        tweaks_tab = ttk.Frame(self.notebook, padding="20 10 20 10")
        self.notebook.add(tweaks_tab, text="⚡ Tweaks")
        
        # Create top frame for search (fixed at top)
        top_frame = ttk.Frame(tweaks_tab)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add search box
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        search_var = tk.StringVar()
        search_var.trace('w', lambda *args: self.filter_tweaks(search_var.get()))
        
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.insert(0, "Search tweaks...")
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0, tk.END) if search_entry.get() == "Search tweaks..." else None)
        search_entry.bind('<FocusOut>', lambda e: search_entry.insert(0, "Search tweaks...") if search_entry.get() == "" else None)
        
        # Add buttons
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT)
        
        refresh_button = ttk.Button(button_frame, text="Refresh States", command=self.refresh_tweak_states)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(tweaks_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tweaks_tab, orient="vertical", command=canvas.yview)
        
        # Create main frame inside canvas
        main_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window in canvas
        canvas_frame = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        # Bind events
        main_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_width)
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Store references to all tweak frames for filtering
        self.tweak_frames = []
        
        # Create sections for different types of tweaks
        sections = [
            ("🚀 Performance Optimization", [
                ("Set Services to Manual", "set_services_manual", "Set selected Windows services to manual startup", "service"),
                ("Disable Visual Effects", "disable_visual_effects", "Optimize Windows for better performance", "performance"),
                ("Disable Transparency", "disable_transparency", "Turn off transparency effects", "performance"),
                ("Disable Animations", "disable_animations", "Turn off animation effects", "performance"),
                ("Optimize Processor Scheduling", "optimize_processor_scheduling", "Adjust for best performance of programs", "performance"),
                ("Disable Background Apps", "disable_background_apps", "Prevent apps from running in background", "performance"),
                ("Disable Startup Delay", "disable_startup_delay", "Remove delay for startup programs", "performance"),
                ("Clear Page File at Shutdown", "clear_page_file", "Secure but slower shutdown", "performance"),
                ("Optimize SSD", "optimize_ssd", "Enable TRIM and disable defrag for SSDs", "performance")
            ]),
            ("🔒 Privacy & Security", [
                ("Disable Telemetry", "disable_telemetry", "Reduce data collection by Windows", "privacy"),
                ("Disable Cortana", "disable_cortana", "Turn off Cortana assistant", "privacy"),
                ("Disable Activity History", "disable_activity_history", "Stop Windows from tracking activities", "privacy"),
                ("Disable Location Tracking", "disable_location_tracking", "Turn off location services", "privacy"),
                ("Disable Advertising ID", "disable_advertising_id", "Stop personalized ads", "privacy"),
                ("Disable Windows Tips", "disable_windows_tips", "Stop Windows suggestions", "privacy"),
                ("Disable Timeline", "disable_timeline", "Turn off Windows Timeline feature", "privacy"),
                ("Disable Cloud Clipboard", "disable_cloud_clipboard", "Stop syncing clipboard to cloud", "privacy"),
                ("Disable Diagnostic Data", "disable_diagnostic_data", "Minimize diagnostic data collection", "privacy"),
                ("Disable Feedback", "disable_feedback", "Turn off feedback notifications", "privacy")
            ]),
            ("🖥️ Desktop & Explorer", [
                ("Show File Extensions", "show_file_extensions", "Display all file extensions", "desktop"),
                ("Show Hidden Files", "show_hidden_files", "Show hidden files and folders", "desktop"),
                ("Disable Quick Access", "disable_quick_access", "Clean up File Explorer sidebar", "desktop"),
                ("Classic Context Menu", "classic_context_menu", "Use Windows 10 style context menu", "desktop"),
                ("Disable Search Highlights", "disable_search_highlights", "Remove search highlights", "desktop"),
                ("Enable Dark Mode", "enable_dark_mode", "Enable system-wide dark theme", "desktop")
            ]),
            ("⚡ Power & Battery", [
                ("High Performance", "set_high_performance", "Set power plan to high performance", "power"),
                ("Disable USB Power Saving", "disable_usb_power_saving", "Prevent USB selective suspend", "power"),
                ("Disable Sleep Timeout", "disable_sleep", "Prevent system from sleeping", "power")
            ]),
            ("🎮 Gaming Optimization", [
                ("Game Mode", "enable_game_mode", "Enable Windows Game Mode", "gaming"),
                ("Hardware Acceleration", "enable_hardware_acceleration", "Enable GPU scheduling", "gaming"),
                ("Disable Game Bar", "disable_game_bar", "Remove Xbox Game Bar", "gaming")
            ]),
            ("🌐 Network & Internet", [
                ("Optimize Network", "optimize_network", "Optimize network settings", "network"),
                ("Use Fast DNS", "set_dns_servers", "Use faster DNS servers", "network")
            ]),
            ("🔧 System Maintenance", [
                ("Clean Temp Files", "clean_temp_files", "Remove unnecessary files", "maintenance"),
                ("Optimize Search", "optimize_windows_search", "Windows Search indexer", "maintenance"),
                ("Optimize Prefetch", "optimize_prefetch", "Optimize Windows Prefetch settings", "maintenance"),
                ("Optimize Disk Cleanup", "optimize_disk_cleanup", "Configure disk cleanup settings", "maintenance"),
                ("Optimize System Restore", "optimize_system_restore", "Configure system restore settings", "maintenance")
            ])
        ]
        
        # Create sections
        for i, (section_title, tweaks) in enumerate(sections):
            # Section label
            section_label = ttk.Label(main_frame, text=section_title, font=("Segoe UI", 12, "bold"))
            section_label.grid(row=i*10, column=0, columnspan=2, sticky="w", pady=(20 if i > 0 else 0, 10))
            
            # Make section label draggable
            section_label.bind('<Button-1>', self.start_move)
            section_label.bind('<B1-Motion>', self.on_move)
            
            # Create tweaks
            for j, (tweak_name, func_name, description, category) in enumerate(tweaks):
                col = j % 2
                row = (i * 10) + (j // 2) + 1
                
                # Create frame for each tweak
                tweak_frame = ttk.Frame(main_frame)
                tweak_frame.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
                
                # Add switch
                switch_var = tk.BooleanVar()
                switch = ttk.Checkbutton(
                    tweak_frame, 
                    text=tweak_name,
                    variable=switch_var,
                    command=lambda n=func_name, v=switch_var: self.on_tweak_toggled(n, v)
                )
                switch.pack(side=tk.LEFT, padx=(0, 5))
                
                # Add description
                desc_label = ttk.Label(tweak_frame, text=description, foreground="gray")
                desc_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Store references for filtering and state management
                self.tweak_frames.append({
                    'frame': tweak_frame,
                    'name': tweak_name,
                    'description': description,
                    'section': section_title.lower()
                })
                
                # Store function references and variables
                self.tweak_functions[func_name] = {
                    'var': switch_var,
                    'category': category
                }
        
        # Refresh tweak states after UI setup
        self.root.after(100, self.refresh_tweak_states)

    def filter_tweaks(self, search_text):
        """Filter tweaks based on search text"""
        search_text = search_text.lower()
        if search_text == "search tweaks...":
            search_text = ""
            
        for tweak in self.tweak_frames:
            if (search_text in tweak['name'].lower() or 
                search_text in tweak['description'].lower() or 
                search_text in tweak['section'].lower()):
                tweak['frame'].grid()
            else:
                tweak['frame'].grid_remove()

    def on_tweak_toggled(self, tweak_name, var):
        """Handle tweak checkbox toggle"""
        try:
            # Get the appropriate tweak class based on category
            category = self.tweak_functions[tweak_name]['category']
            tweak_class = None
            if category == 'performance':
                tweak_class = self.performance_tweaks
            elif category == 'privacy':
                tweak_class = self.privacy_tweaks
            elif category == 'desktop':
                tweak_class = self.desktop_tweaks
            elif category == 'power':
                tweak_class = self.power_tweaks
            elif category == 'gaming':
                tweak_class = self.gaming_tweaks
            elif category == 'network':
                tweak_class = self.network_tweaks
            elif category == 'maintenance':
                tweak_class = self.maintenance_tweaks

            # Get the tweak function
            if hasattr(tweak_class, tweak_name):
                tweak_func = getattr(tweak_class, tweak_name)
                success = tweak_func(var.get())
                if success:
                    self.show_notification(f"Successfully {'applied' if var.get() else 'reverted'} {tweak_name}")
                    self.logger.info(f"Successfully {'applied' if var.get() else 'reverted'} tweak: {tweak_name}")
                else:
                    self.show_notification(f"Failed to {'apply' if var.get() else 'revert'} {tweak_name}", "error")
                    self.logger.error(f"Failed to apply tweak: {tweak_name}")
                    # Reset the checkbox to its previous state
                    var.set(not var.get())
            else:
                self.show_notification(f"Function {tweak_name} not found", "error")
                self.logger.error(f"Function {tweak_name} not found")
                var.set(not var.get())
        except Exception as e:
            self.show_notification(f"Error applying {tweak_name}: {str(e)}", "error")
            self.logger.error(f"Error applying tweak {tweak_name}: {str(e)}")
            var.set(not var.get())

    def show_notification(self, message, type="info"):
        """Show a small notification in the UI"""
        style = "success.TLabel" if type == "success" else "error.TLabel" if type == "error" else "info.TLabel"
        
        # Create and configure notification styles if they don't exist
        self.root.tk.call("ttk::style", "configure", "success.TLabel", "-foreground", "green")
        self.root.tk.call("ttk::style", "configure", "error.TLabel", "-foreground", "red")
        self.root.tk.call("ttk::style", "configure", "info.TLabel", "-foreground", "blue")
        
        notification = ttk.Label(self.root, text=message, style=style)
        notification.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")
        
        # Schedule the notification to be removed after 3 seconds
        self.root.after(3000, notification.destroy)

    def refresh_tweak_states(self):
        """Check and update the state of all tweaks"""
        try:
            for func_name, data in self.tweak_functions.items():
                try:
                    # Get the appropriate tweak class based on category
                    category = data['category']
                    tweak_class = None
                    if category == 'performance':
                        tweak_class = self.performance_tweaks
                    elif category == 'privacy':
                        tweak_class = self.privacy_tweaks
                    elif category == 'desktop':
                        tweak_class = self.desktop_tweaks
                    elif category == 'power':
                        tweak_class = self.power_tweaks
                    elif category == 'gaming':
                        tweak_class = self.gaming_tweaks
                    elif category == 'network':
                        tweak_class = self.network_tweaks
                    elif category == 'maintenance':
                        tweak_class = self.maintenance_tweaks

                    # Get the check function
                    check_name = f"check_{func_name}"
                    if hasattr(tweak_class, check_name):
                        check_func = getattr(tweak_class, check_name)
                        is_enabled = check_func()
                        data['var'].set(is_enabled)
                        self.logger.info(f"State of {func_name}: {is_enabled}")
                    else:
                        self.logger.warning(f"No check function found: {check_name}")
                except Exception as e:
                    self.logger.error(f"Error checking state for {func_name}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error refreshing tweak states: {str(e)}")
            
    def setup_dashboard_tab(self):
        dashboard_tab = ttk.Frame(self.notebook, padding="20 10 20 10", style="Dashboard.TFrame")
        self.notebook.add(dashboard_tab, text="🏠 Home")
        self.notebook.select(0)  # Make dashboard the default tab

        # Welcome header with gradient-like effect
        header_frame = ttk.Frame(dashboard_tab, style="Header.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_frame, text="Welcome to MTech WinTool", style="DashboardTitle.TLabel")
        title_label.pack(anchor="w")
        subtitle_label = ttk.Label(title_frame, text="Your Windows System Management Hub", style="DashboardSubtitle.TLabel")
        subtitle_label.pack(anchor="w")

        # Make title and subtitle labels draggable
        title_label.bind('<Button-1>', self.start_move)
        title_label.bind('<B1-Motion>', self.on_move)
        subtitle_label.bind('<Button-1>', self.start_move)
        subtitle_label.bind('<B1-Motion>', self.on_move)
        
        # Create main content frame with grid layout
        content_frame = ttk.Frame(dashboard_tab)
        content_frame.pack(fill=tk.BOTH, expand=True)
        for i in range(2):
            content_frame.grid_columnconfigure(i, weight=1)
        content_frame.grid_rowconfigure(0, weight=3)  # Give more weight to top row
        content_frame.grid_rowconfigure(1, weight=2)  # Less weight to bottom row

        # System Health Card with modern metrics
        health_frame = ttk.LabelFrame(content_frame, text="💻 System Health", padding=15, style="DashboardCard.TFrame")
        health_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # CPU Usage with progress ring
        cpu_frame = ttk.Frame(health_frame)
        cpu_frame.pack(fill=tk.X, pady=5)
        
        self.dash_cpu_label = ttk.Label(cpu_frame, text="0%", style="DashboardMetric.TLabel")
        self.dash_cpu_label.pack(side=tk.LEFT)
        
        cpu_info_frame = ttk.Frame(cpu_frame)
        cpu_info_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(cpu_info_frame, text="CPU Usage", style="DashboardText.TLabel").pack(anchor="w")
        self.cpu_details_label = ttk.Label(cpu_info_frame, text="", style="DashboardSubtext.TLabel")
        self.cpu_details_label.pack(anchor="w")

        ttk.Separator(health_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        # Memory Usage with visual bar
        memory_frame = ttk.Frame(health_frame)
        memory_frame.pack(fill=tk.X, pady=5)
        
        self.dash_memory_label = ttk.Label(memory_frame, text="0%", style="DashboardMetric.TLabel")
        self.dash_memory_label.pack(side=tk.LEFT)
        
        memory_info_frame = ttk.Frame(memory_frame)
        memory_info_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(memory_info_frame, text="Memory Usage", style="DashboardText.TLabel").pack(anchor="w")
        self.memory_details_label = ttk.Label(memory_info_frame, text="", style="DashboardSubtext.TLabel")
        self.memory_details_label.pack(anchor="w")

        ttk.Separator(health_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        # Disk Usage
        disk_frame = ttk.Frame(health_frame)
        disk_frame.pack(fill=tk.X, pady=5)
        
        self.dash_disk_label = ttk.Label(disk_frame, text="0%", style="DashboardMetric.TLabel")
        self.dash_disk_label.pack(side=tk.LEFT)
        
        disk_info_frame = ttk.Frame(disk_frame)
        disk_info_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(disk_info_frame, text="Disk Activity", style="DashboardText.TLabel").pack(anchor="w")
        self.disk_details_label = ttk.Label(disk_info_frame, text="", style="DashboardSubtext.TLabel")
        self.disk_details_label.pack(anchor="w")

        # Make disk details label draggable
        self.disk_details_label.bind('<Button-1>', self.start_move)
        self.disk_details_label.bind('<B1-Motion>', self.on_move)
        
        # Quick Actions Card with modern buttons
        actions_frame = ttk.LabelFrame(content_frame, text="⚡ Quick Actions", padding=15, style="DashboardCard.TFrame")
        actions_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Action buttons with icons and descriptions
        self.create_action_button(actions_frame, "🧹 System Cleanup", 
                                "Clean temporary files and free up space", 
                                self.open_disk_cleanup)
        
        self.create_action_button(actions_frame, "🔄 Update Check", 
                                "Check for system and package updates", 
                                self.refresh_packages)
        
        self.create_action_button(actions_frame, "⚙️ System Settings", 
                                "Configure system preferences", 
                                self.open_system_settings)
        
        self.create_action_button(actions_frame, "🛡️ Task Manager", 
                                "Monitor system performance and tasks", 
                                self.open_task_manager)

        # Recent Activity Card with improved styling
        activity_frame = ttk.LabelFrame(content_frame, text="📋 Recent Activity", padding=15, style="DashboardCard.TFrame")
        activity_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Activity list with custom styling
        self.activity_text = tk.Text(activity_frame, height=6, wrap=tk.WORD, font=("Segoe UI", 10), 
                                   borderwidth=0, highlightthickness=0, 
                                   background='#1c1c1c', relief="flat")  # Match dark theme
        self.activity_text.pack(fill=tk.BOTH, expand=True)
        self.activity_text.tag_configure("title", font=("Segoe UI", 12, "bold"), foreground="#ff6b00")
        self.activity_text.tag_configure("feature", font=("Segoe UI", 10), foreground="#FFFFFF")
        
        # Insert formatted welcome text
        welcome_text = (
            "Welcome to the Dashboard! 🚀\n\n"
            "• Take control of your Windows system with ease and efficiency\n"
            "• Access to Package Management, Tweaks, Monitoring, and so much more!\n"
        )
        
        self.activity_text.insert(tk.END, welcome_text.split('\n')[0], "title")
        self.activity_text.insert(tk.END, '\n\n')
        for line in welcome_text.split('\n')[2:]:
            self.activity_text.insert(tk.END, line + '\n', "feature")
            
        self.activity_text.config(state=tk.DISABLED)

    def create_action_button(self, parent, text, description, command):
        """Create a modern action button with description"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        
        btn = ttk.Button(button_frame, text=text, command=command, style="DashboardAction.TButton")
        btn.pack(fill=tk.X)
        
        desc_label = ttk.Label(button_frame, text=description, style="DashboardSubtext.TLabel")
        desc_label.pack(fill=tk.X)

    def add_activity(self, message):
        """Add a new activity message to the dashboard with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_text.config(state=tk.NORMAL)
        self.activity_text.insert(1.0, f"[{timestamp}] {message}\n")
        self.activity_text.config(state=tk.DISABLED)

    def update_stats(self):
        total_packages = sum(len(packages) for packages in self.pkg_ops.categories.values())
        total_categories = len(self.pkg_ops.categories)
        self.stats_label.configure(text=f" 📦 {total_packages} WinGet Packages in {total_categories} Categories")
        
    def filter_packages(self, *args):
        search_term = self.search_var.get().lower()
        selected_category = self.category_var.get()
        self.tree.delete(*self.tree.get_children())
        
        for category, packages in self.pkg_ops.categories.items():
            # Skip if a specific category is selected and this isn't it
            if selected_category != "All" and category != selected_category:
                continue
                
            category_visible = False
            category_id = self.tree.insert('', 'end', text=category)
            
            for package_name in packages:
                if search_term in package_name.lower() or search_term in self.pkg_ops.get_package_info(package_name).get('description', '').lower():
                    package_data = self.pkg_ops.get_package_info(package_name)
                    description = package_data.get('description', '')
                    
                    is_installed = self.pkg_ops.installation_status.get(package_name, False)
                    needs_update = self.pkg_ops.update_status_dict.get(package_name, False)
                    
                    if needs_update:
                        status = "Update Available"
                        tag = 'needs_update'
                    elif is_installed:
                        status = "Updated"
                        tag = 'installed'
                    else:
                        status = "Not Installed"
                        tag = 'not_installed'
                    
                    self.tree.insert(category_id, 'end', text=package_name, values=(status, description), tags=(tag,))
                    category_visible = True
            
            if not category_visible:
                self.tree.delete(category_id)
            else:
                # Open the category by default
                self.tree.item(category_id, open=True)
        
        self.update_stats()

    def initial_package_load(self):
        """Initial load of packages and update UI"""
        self.pkg_ops.load_packages_async(self.update_status, self.status_queue)
        self.root.after(100, self.check_and_update_categories)
    
    def check_and_update_categories(self):
        """Check if categories are loaded and update dropdown"""
        if self.pkg_ops.categories:
            categories = list(self.pkg_ops.categories.keys())
            categories.sort()
            categories.insert(0, "All")
            self.category_dropdown['values'] = categories
            self.filter_packages()
        else:
            # Check again in 100ms
            self.root.after(100, self.check_and_update_categories)

    def run(self):
        self.root.mainloop()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    winget_installer = WinGetInstaller(root)
    winget_installer.run()
