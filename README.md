# MTech WinTool (Beta 0.0.2a)

A modern, automated Windows utility application that simplifies system monitoring and software management. Built with Python and tkinter, featuring an elegant Sun Valley theme and automated setup process.

### One-Click Download and Run (Powershell) 
```powershell
Invoke-WebRequest -Uri "https://github.com/MTechWare/wintools/releases/download/release/MTechWinTool.exe" -OutFile "MTechWinTool.exe"; Start-Process "MTechWinTool.exe"
```

## 🔧 Requirements

- Windows 10/11
- Python 3.11 or higher
- Winget package manager
- Administrator privileges (for some features)

## 🆕 What's New in Beta 0.0.2a

### Performance Improvements
- Optimized software status checking with batch processing
- Removed unnecessary dependency installation step
- Improved overall application responsiveness

### Enhanced Software Management
- Added silent mode for software uninstallation
- Added timeout handling for installation/uninstallation
- Improved software installation reliability
- Better error messages and status display

### Bug Fixes
- Fixed software status refresh performance
- Improved error handling during installation/uninstallation
- Enhanced thread safety in UI updates

## 📸 Screenshots

<div align="center">

| System Monitoring | Software Installation |
|:---:|:---:|
| ![System](screenshots/wintool_System.png) | ![Install](screenshots/wintool_Install.png) |
| *Real-time CPU, Memory, and Disk monitoring* | *Easy software installation with parallel status checking* |

| Hardware Information | Windows Configuration |
|:---:|:---:|
| ![Hardware](screenshots/wintool_Hardware.png) | ![Config](screenshots/wintool_Unattend.png) |
| *Detailed hardware monitoring and system info* | *Windows unattended installation configuration* |

</div>

## 🌟 Key Features

### 🔄 Automated Setup
- No manual configuration needed
- Auto-checks for winget availability
- Streamlined initialization process

### 🎨 Modern UI
- Sleek Sun Valley theme with custom title bar
- Responsive tabbed interface
- Dark/Light mode support
- System tray integration with minimize to tray
- Real-time status updates
- Thread-safe UI operations
- Graceful exit handling

### 📊 System Monitoring
- Real-time CPU usage
- Memory usage tracking
- Disk space monitoring
- System information display
- Background monitoring with optimized performance
- Efficient thread management

### 📦 Software Management
- Parallel software status checking (up to 10 concurrent checks)
- One-click software installation via winget
- Real-time installation status updates
- Pre-configured software categories:
  - Browsers (Chrome, Firefox, Opera)
  - Development Tools (VS Code, Git, Python)
  - Code Editors (IntelliJ, PyCharm, Sublime)
  - Utilities (7-Zip, VLC, Notepad++)

### ⚙️ Windows Configuration
- Unattended Windows installation XML generator
- System optimization tools
- Hardware monitoring integration

## 📥 Installation

### Easy Install (Recommended)

1. Download the latest release
2. Run `Install.cmd` as administrator
3. Wait for the installation to complete
4. Launch MTech WinTool from the Start Menu

### Manual Installation

1. Install Python 3.11 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## 🛠️ Building from Source

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MTechWare/wintools.git
   cd MTech_WinTool
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Build the Executable**
   ```bash
   Build.cmd
   ```
   The executable will be created in the `dist` directory.

## 🚀 Getting Started

1. Download the latest release
2. Run with administrator privileges
3. Start managing your Windows system efficiently!

## 💡 Tips

- Use the system tray feature to keep the tool running in background
- Check the detailed error messages if software installation fails
- Utilize the category filters to find software quickly
- Keep the tool updated for best performance

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Feel free to:
- Report issues
- Suggest features
- Submit pull requests

---

Made with ❤️ by MTechWare
