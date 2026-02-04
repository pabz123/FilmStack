# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MovieFlix
Creates a standalone .exe with embedded icon and VLC support
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get all necessary data files
datas = [
    ('MovieFlix.ico', '.'),  # Icon file
    ('.env', '.'),  # Environment variables
    ('backend', 'backend'),  # Backend folder
    ('app', 'app'),  # App folder
]

# Add VLC if exists
if os.path.exists('VLC'):
    datas.append(('VLC', 'VLC'))

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
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'dotenv',
    'PIL',
    'PIL.Image',
    'win32api',
    'win32file',
    'pywintypes',
]

a = Analysis(
    ['start_movieflix.py'],  # Main entry point
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'tensorflow'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MovieFlix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='MovieFlix.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MovieFlix',
)
