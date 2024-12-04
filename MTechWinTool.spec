# -*- mode: python ; coding: utf-8 -*-

import os
import sv_ttk

block_cipher = None

sv_ttk_path = os.path.dirname(sv_ttk.__file__)
theme_path = os.path.join(sv_ttk_path, 'theme')
theme_files = []

# Add main sv.tcl file
sv_tcl = os.path.join(sv_ttk_path, 'sv.tcl')
if os.path.exists(sv_tcl):
    theme_files.append((sv_tcl, 'sv_ttk'))

# Add all theme files
theme_file_list = [
    'dark.tcl',
    'light.tcl',
    'sprites_dark.tcl',
    'sprites_light.tcl',
    'spritesheet_dark.png',
    'spritesheet_light.png',
    'sun-valley.tcl',
]

for theme_file in theme_file_list:
    src = os.path.join(theme_path, theme_file)
    if os.path.exists(src):
        theme_files.append((src, os.path.join('sv_ttk', 'theme')))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=theme_files + [('icon.ico', '.')],
    hiddenimports=['wmi', 'win32api', 'win32con', 'pystray'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Added excludes to remove unused modules
   excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'tk', 'tcl', 'PyQt5', 'PySide2', 'IPython', 
         'notebook', 'jupyter', 'qtpy', 'sphinx', 'pytest', 'wx'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    # Added collect options to minimize included files
    collect_submodules=[],
    collect_data_files=[],
    collect_binaries=[],
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MTechWinTool',
    debug=False,
    bootloader_ignore_signals=False,
    # Enable stripping of binary
    strip=False,
    # Enhanced UPX compression
    upx=True,
    upx_exclude=[],
    upx_args=['--best'],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
    uac_admin=True,
)