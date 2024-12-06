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

:: Create directory if it doesn't exist
if not exist "%ProgramFiles%\MTech WinTool" mkdir "%ProgramFiles%\MTech WinTool"

:: Copy files
copy /Y "dist\MTech_WinTool.exe" "%ProgramFiles%\MTech WinTool"
copy /Y "icon.ico" "%ProgramFiles%\MTech WinTool"

:: Create shortcut on desktop
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\MTech WinTool.lnk'); $Shortcut.TargetPath = '%ProgramFiles%\MTech WinTool\MTech_WinTool.exe'; $Shortcut.IconLocation = '%ProgramFiles%\MTech WinTool\icon.ico'; $Shortcut.Save()"

echo Installation complete!
echo A shortcut has been created on your desktop.
pause
