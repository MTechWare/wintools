# MTech WinTool (Beta 0.0.3a)

A modern, automated Windows utility application that simplifies system monitoring and software management. Built with Python and tkinter, featuring an elegant Sun Valley theme and automated setup process.

## 🔧 Requirements

- Windows 10/11
- Python 3.11 or higher
- Winget package manager
- Administrator privileges (for some features)

## 📥 Installation

### Quick Install (PowerShell)

```powershell
Invoke-WebRequest -Uri https://github.com/MTechWare/wintools/releases/download/v0.0.3a/MTechWinTool.exe -OutFile MTechWinTool.exe; Start-Process .\MTechWinTool.exe
```

### Alternative Installation

Download the latest release from [GitHub Releases](https://github.com/MTechWare/wintools/releases) and run the executable.

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

## 🆕 What's New in Beta 0.0.3a

### New Features
- Added Settings tab

### Performance Improvements
- Optimized software status checking with batch processing (major improvement)

### Enhanced Software Management
- Added silent mode for software uninstallation
- Added timeout handling for installation/uninstallation
- Improved software installation reliability

### UI Improvements
- Enhanced minimize to tray behavior with first-time notification
- Improved settings persistence and management

### Bug Fixes
- Fixed software status refresh performance
- Improved error handling during installation/uninstallation
- Enhanced thread safety in UI updates
- When building from source, the executable is smaller

## 💡 Tips

- Use the system tray feature to keep the tool running in background
- Check the detailed error messages if software installation fails
- Utilize the category filters to find software quickly
- Keep the tool updated for best performance

## 🌟 Key Features

### 🔄 Automated Setup
- No manual configuration needed
- Auto-checks for winget availability
- Streamlined initialization process
- Fixed Winget auto-installation

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

### Manual Installation (From Source)

1. Install Python 3.11 or higher
2. Install required packages use install.cmd
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
   install.cmd
   ```

3. **Build the Executable**
   ```bash
   Build.cmd
   ```
   The executable will be created in the `dist` directory.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Feel free to:
- Report issues
- Suggest features
- Submit pull requests

## 📫 Contact

- GitHub Issues: [Report a bug](https://github.com/MTechWare/wintools/issues)

---

Made with ❤️ by MTechWare
