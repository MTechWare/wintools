# MTech WinTool (Beta 0.0.1a)

A modern, automated Windows utility application that simplifies system monitoring and software management. Built with Python and tkinter, featuring an elegant Sun Valley theme and automated setup process.

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
- Auto-extracts and starts OpenHardwareMonitor
- Auto-installs required Python packages
- Auto-checks for winget availability
- No manual configuration needed

### 🎨 Modern UI
- Sleek Sun Valley theme with custom title bar
- Responsive tabbed interface
- Dark/Light mode support
- Real-time status updates
- Thread-safe UI operations
- Graceful exit handling

### 📊 System Monitoring
- Real-time CPU usage and temperature
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

## 🔧 Requirements

- Windows 10/11
- Python 3.11 or higher
- Winget package manager
- Administrator privileges (for some features)

## 📥 Installation

1. **Download the Latest Release**
   - Download `MTechWinTool.exe` from the releases page
   - Or build from source (see below)

2. **Antivirus Notice**
   - Some antivirus software may flag MTechWinTool as suspicious due to its system monitoring capabilities
   - This is a false positive caused by:
     * System monitoring features
     * Administrative privileges requirement
     * Windows registry access
   - The application is completely safe and open source
   - You can verify the safety by:
     * Building from source yourself
     * Checking the source code
     * Using VirusTotal to scan the executable

3. **Run the Application**
   - Double-click `MTechWinTool.exe`
   - Grant administrator privileges when prompted
   - If blocked by antivirus:
     * Add MTechWinTool to your antivirus exclusions
     * Or build from source (see below)
   - The application will handle all setup automatically

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

## 🔍 Technical Details

### Core Components
- **Threading**: Uses ThreadPoolExecutor for parallel operations
- **UI**: Custom tkinter implementation with sv-ttk theme
- **Monitoring**: Integration with OpenHardwareMonitor
- **Package Management**: Winget integration
- **Error Handling**: Comprehensive error handling and logging

### Performance Features
- Parallel software status checking
- Thread-safe UI updates
- Optimized background monitoring
- Graceful thread and process management
- Efficient resource cleanup

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Sun Valley theme for tkinter
- OpenHardwareMonitor for system monitoring
- Winget package manager
- Python community for excellent libraries
