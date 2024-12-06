"""
MTechWinTool - Windows System Utility
Version: Beta 0.0.4a

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
            self.status_label.configure(text=f"❌ Installation failed: PowerShell error", foreground="red")
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
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
            
        self.root.title("MTech WinTool")
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
        style.configure("AboutTitle.TLabel", font=("Segoe UI", 14, "bold"), foreground='#ff9800')  # Orange color
        style.configure("Dashboard.TFrame", padding=10)
        style.configure("DashboardTitle.TLabel", font=("Segoe UI", 16, "bold"), foreground='#ff9800')  # Orange color
        style.configure("DashboardSubtitle.TLabel", font=("Segoe UI", 12))
        style.configure("DashboardCard.TFrame", padding=15)
        style.configure("DashboardMetric.TLabel", font=("Segoe UI", 24, "bold"))
        style.configure("DashboardText.TLabel", font=("Segoe UI", 10))
        style.configure("DashboardSubtext.TLabel", font=("Segoe UI", 9))
        style.configure("DashboardAction.TButton", padding=10)
        
        # Configure tag colors for treeview
        self.tree_tags = {
            'installed': 'green',
            'not_installed': 'white',
            'needs_update': 'orange'
        }
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.setup_dashboard_tab()  # Add dashboard as first tab
        self.setup_packages_tab()
        self.setup_monitor_tab()
        self.setup_tools_tab()
        self.setup_unattend_tab()
        self.setup_about_tab()

    def setup_packages_tab(self):
        packages_tab = ttk.Frame(self.notebook, padding="20 10 20 10")
        self.notebook.add(packages_tab, text=" 📦 Winget Packages ")
        
        # Header frame with status
        header_frame = ttk.Frame(packages_tab)
        header_frame.pack(fill=tk.X, pady=(10, 20))
        
        title_label = ttk.Label(header_frame, text="WinGet Package Manager", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Status frame
        self.status_frame = ttk.Frame(header_frame)
        self.status_frame.pack(side=tk.RIGHT)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", style="Status.TLabel")
        self.status_label.pack(side=tk.RIGHT)
        
        self.progress_bar = ttk.Progressbar(self.status_frame, mode='indeterminate', length=100)
        
        # Search frame with modern styling
        search_frame = ttk.Frame(packages_tab, style="Search.TFrame")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_label = ttk.Label(search_frame, text="🔍", font=("Segoe UI", 12))
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
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
        self.notebook.add(monitor_tab, text=" 📊 System Monitor ")

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
        self.notebook.add(tools_tab, text=" 🛠️ Tools ")

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
        self.notebook.add(unattend_tab, text=" 📝 Unattend ")

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
        self.notebook.add(about_tab, text=" ℹ️ About ")

        # Create main content frame
        content_frame = ttk.Frame(about_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # App title and version
        title_label = ttk.Label(content_frame, text="MTech WinTool", style="AboutTitle.TLabel")
        title_label.pack(pady=(0, 10))

        version_label = ttk.Label(content_frame, text="Beta Version 0.0.4a", style="About.TLabel")
        version_label.pack(pady=(0, 20))

        # Features frame
        features_frame = ttk.LabelFrame(content_frame, text="Features", padding=15)
        features_frame.pack(fill=tk.X, pady=(0, 20))

        features_text = """📦 Package Management with Winget Integration
🖥️ System Monitoring and Performance Metrics
🛠️ System Tools and Utilities
📝 Windows Unattend File Creation
🌙 Dark Mode Support"""

        features_label = ttk.Label(features_frame, text=features_text, style="About.TLabel", justify=tk.LEFT)
        features_label.pack(anchor="w", padx=10)

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

        credits_text = """👨‍💻 Created by: MTechware
🎨 Theme: Sun Valley (sv-ttk)
🎯 Icons: Segoe Fluent Icons"""

        credits_label = ttk.Label(credits_frame, text=credits_text, style="About.TLabel", justify=tk.LEFT)
        credits_label.pack(anchor="w", padx=10)

    def on_tab_changed(self, event):
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
        self.auto_logon_count.set(self.unattend_creator.settings['auto_logon_count'])

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
        package_name = self.get_selected_package()
        if not package_name:
            messagebox.showwarning("No Package Selected", "Please select a package to install.")
            return
            
        if self.pkg_ops.installation_status.get(package_name, False):
            messagebox.showinfo("Already Installed", f"{package_name} is already installed.")
            return
            
        threading.Thread(target=self.pkg_ops.install_package, args=(package_name, self.update_status), daemon=True).start()

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

    def setup_dashboard_tab(self):
        dashboard_tab = ttk.Frame(self.notebook, padding="20 10 20 10", style="Dashboard.TFrame")
        self.notebook.add(dashboard_tab, text=" 🏠 Dashboard ")
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

        # Create main content frame with grid layout
        content_frame = ttk.Frame(dashboard_tab)
        content_frame.pack(fill=tk.BOTH, expand=True)
        for i in range(2):
            content_frame.grid_columnconfigure(i, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

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
        self.activity_text = tk.Text(activity_frame, height=8, wrap=tk.WORD, font=("Segoe UI", 10))
        self.activity_text.pack(fill=tk.BOTH, expand=True)
        self.activity_text.tag_configure("timestamp", foreground="#666666")
        self.activity_text.tag_configure("message", foreground="#000000")
        self.activity_text.insert(tk.END, "Welcome to MTech WinTool!\n")
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

if __name__ == "__main__":
    root = tk.Tk()
    winget_installer = WinGetInstaller(root)
    winget_installer.run()
