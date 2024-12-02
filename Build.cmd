@echo off
echo Building MTechWinTool...

REM Clean previous build
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"

REM Build executable
python -m PyInstaller MTechWinTool.spec

echo Build complete! Executable is in the dist folder.
pause