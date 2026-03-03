# -*- mode: python ; coding: utf-8 -*-
"""
MovieFlix Linux Build Configuration
Creates a standalone Linux executable.
VLC is NOT bundled – users install it via their package manager.
"""
import os
import sys
import site

block_cipher = None
project_dir = os.path.abspath('.')

print("=" * 50)
print("  Building MovieFlix for Linux")
print("  VLC NOT bundled (install: sudo apt install vlc)")
print("=" * 50)

# Core data files
datas_list = [
    ('backend', 'backend'),
    ('app', 'app'),
    ('.env', '.'),
]

# Include MovieFlix icon if present
if os.path.exists('MovieFlix.ico'):
    datas_list.append(('MovieFlix.ico', '.'))

# Include python-multipart data
for sp in site.getsitepackages():
    multipart_path = os.path.join(sp, 'multipart')
    if os.path.exists(multipart_path):
        datas_list.append((multipart_path, 'multipart'))
        print(f"✓ Added multipart from: {multipart_path}")
        break

a = Analysis(
    ['start_movieflix.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        # Uvicorn
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
        # Multipart
        'multipart',
        'multipart.multipart',
        'python_multipart',
        # Starlette
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
        # PyQt5
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        # VLC bindings (library itself is system-installed)
        'vlc',
        # SQLAlchemy
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
        # Windows-only – not needed on Linux
        'win32api',
        'win32con',
        'win32com',
        'pythoncom',
        'pywintypes',
    ],
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
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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
