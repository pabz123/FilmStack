# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MovieFlix
Creates a standalone .exe with embedded icon and VLC support
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Print status messages during build
print("=" * 50)
print("  Building MovieFlix.exe")
print("=" * 50)

# Check for required files
required_files = ['start_movieflix.py', 'MovieFlix.ico']
missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    print("\nERROR: Missing required files:")
    for f in missing_files:
        print(f"  - {f}")
    print("\nPlease ensure all required files exist before building.")
    sys.exit(1)

# Get all necessary data files - only add if they exist
datas = []

# Required files
if os.path.exists('MovieFlix.ico'):
    datas.append(('MovieFlix.ico', '.'))
    print("✓ Found MovieFlix.ico")
else:
    print("✗ WARNING: MovieFlix.ico not found")

# Optional files
if os.path.exists('.env'):
    datas.append(('.env', '.'))
    print("✓ Found .env file")
else:
    print("  Note: .env file not found (optional)")

# Required folders
if os.path.exists('backend') and os.path.isdir('backend'):
    datas.append(('backend', 'backend'))
    print("✓ Found backend folder")
else:
    print("✗ WARNING: backend folder not found")

if os.path.exists('app') and os.path.isdir('app'):
    datas.append(('app', 'app'))
    print("✓ Found app folder")
else:
    print("✗ WARNING: app folder not found")

# Optional VLC folder
if os.path.exists('VLC') and os.path.isdir('VLC'):
    datas.append(('VLC', 'VLC'))
    print("✓ Found VLC folder (embedded player)")
else:
    print("  Note: VLC folder not found (will use system VLC if available)")

print("\n" + "=" * 50)
print(f"Including {len(datas)} data items in build")
print("=" * 50 + "\n")

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
    'backend',
    'backend.version',
    'backend.update_checker',
    'app.update_dialog',
    'packaging',
    'packaging.version',
]

a = Analysis(
    ['start_movieflix.py'],
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
    console=False,
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