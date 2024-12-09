# -*- mode: python ; coding: utf-8 -*-
import os
import sv_ttk

block_cipher = None

# Get sv_ttk package directory
sv_ttk_dir = os.path.dirname(sv_ttk.__file__)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.ico', '.'),
        (sv_ttk_dir, 'sv_ttk'),
        ('system_health.py', '.'),
        ('system_tools.py', '.'),
        ('package_operations.py', '.'),
        ('system_monitor.py', '.'),
        ('unattend_creator.py', '.'),
    ],
    hiddenimports=[
        'sv_ttk',
        'tkinter',
        'tkinter.ttk',
        'psutil',
        'requests',
        'threading',
        'queue',
        'platform',
        'xml.etree.ElementTree',
        'xml.dom.minidom',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MTech_WinTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
    uac_admin=True,
)
