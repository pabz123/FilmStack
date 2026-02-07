# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MovieFlix
Creates a standalone .exe with embedded icon and VLC support
"""

block_cipher = None

# Get all necessary data files
datas = [
    ('MovieFlix.ico', '.'),  # Icon file
    ('.env', '.'),  # Environment variables
    ('VLC', 'VLC'),  # VLC directory (if exists)
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'requests',
    'python-vlc',
    'vlc',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'sqlalchemy',
    'sqlalchemy.orm',
    'sqlalchemy.ext.declarative',
    'fastapi',
    'uvicorn',
    'dotenv',
    'PIL',
    'PIL.Image',
]

a = Analysis(
    ['app\\launcher.py'],  # Main entry point
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas'],  # Exclude unused large packages
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
    name='MovieFlix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='MovieFlix.ico',  # Application icon
)
