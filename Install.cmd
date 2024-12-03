@echo off
echo Installing MTech WinTool...

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run this installer as Administrator
    pause
    exit /b 1
)

:: Check for winget
winget --version >nul 2>&1
if errorlevel 1 (
    echo Winget not found. Installing App Installer...
    start ms-windows-store://pdp/?ProductId=9NBLGGH4NNS1
    echo Please wait for the Microsoft Store to install App Installer
    echo Then press any key to continue...
    pause
)

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Installing Python 3.11...
    winget install -e --id Python.Python.3.11
    
    :: Update PATH
    echo Updating PATH...
    setx PATH "%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts" /M
    
    echo Python installation complete. Please restart this installer.
    pause
    exit
)

:: Install required packages
echo Installing required packages...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Create Start Menu shortcut
echo Creating Start Menu shortcut...
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%appdata%\Microsoft\Windows\Start Menu\Programs\MTech WinTool.lnk');$s.TargetPath='%~dp0dist\MTechWinTool\MTechWinTool.exe';$s.Save()"

echo Installation complete! You can find MTech WinTool in your Start Menu.
pause
