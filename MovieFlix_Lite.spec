# -*- mode: python ; coding: utf-8 -*-
"""
MovieFlix Lite DEBUG Build Configuration
Creates build WITH console window to see errors
"""
import os
import sys
from pathlib import Path

block_cipher = None
project_dir = os.path.abspath('.')

print("=" * 50)
print("  Building MovieFlix Lite DEBUG")
print("  Console window ENABLED for debugging")
print("=" * 50)

# Prepare datas list (NO VLC folder)
datas_list = [
    ('backend', 'backend'),
    ('app', 'app'),
    ('MovieFlix.ico', '.'),
    ('.env', '.'),
]

# Add multipart package as data files
import site
site_packages = site.getsitepackages()[0]
multipart_path = os.path.join(site_packages, 'multipart')
if os.path.exists(multipart_path):
    datas_list.append((multipart_path, 'multipart'))
    print(f"✓ Added multipart from: {multipart_path}")
else:
    print(f"⚠️ Warning: multipart not found at {multipart_path}")

a = Analysis(
    ['start_movieflix.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        # Uvicorn (Backend server)
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        # FastAPI
        'fastapi',
        'fastapi.responses',
        'fastapi.routing',
        'fastapi.applications',
        'fastapi.exceptions',
        'fastapi.params',
        'fastapi.security',
        'fastapi.dependencies',
        'fastapi.dependencies.utils',
        # Multipart (critical for FastAPI forms)
        'multipart',
        'multipart.multipart',
        'python_multipart',
        # Starlette (FastAPI dependency)
        'starlette',
        'starlette.applications',
        'starlette.routing',
        'starlette.responses',
        'starlette.middleware',
        'starlette.middleware.cors',
        # Backend modules
        'backend',
        'backend.main',
        'backend.database',
        'backend.models',
        'backend.scanner',
        'backend.metadata',
        'backend.auth',
        # PyQt5 (UI)
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        # VLC (bindings only, not VLC itself)
        'vlc',
        # Database
        'sqlalchemy',
        'sqlalchemy.ext',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.orm',
        'sqlalchemy.orm.session',
        'sqlalchemy.sql',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.pool',
        'sqlalchemy.engine',
        # Utilities
        'requests',
        'PIL',
        'PIL.Image',
        'PIL.ImageQt',
        'packaging',
        'packaging.version',
        'dotenv',
        'python_dotenv',
        # Windows-specific
        'win32api',
        'win32con',
        'win32com',
        'pythoncom',
        'pywintypes',
        # HTTP/Async
        'h11',
        'httptools',
        'websockets',
        'wsproto',
        'anyio',
        'sniffio',
        'click',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'tkinter',
        'jupyter',
        'notebook',
    ],
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
    debug=False,  # Production mode
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # NO CONSOLE WINDOW - PRODUCTION
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='MovieFlix.ico' if os.path.exists('MovieFlix.ico') else None,
    version_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='MovieFlix',
)
