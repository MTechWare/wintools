@echo off
echo Building MTechWinTool...

REM Clean previous build
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"

REM Build executable
python -m PyInstaller MTechWinTool.spec

:: Create Start Menu shortcut
echo Creating Start Menu shortcut...
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%appdata%\Microsoft\Windows\Start Menu\Programs\MTech WinTool.lnk');$s.TargetPath='%~dp0dist\MTechWinTool\MTechWinTool.exe';$s.Save()"

echo Build complete! Executable is in the dist folder.
pause