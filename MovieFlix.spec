# MovieFlix.spec

# -*- mode: python -*-
block_cipher = None

a = Analysis([
    'MovieFlix.py',
],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False)

pyz = PYZ(a.pure, a.zipped,
           cipher=block_cipher)

exe = EXE(pyz,
           a.scripts,
           [],
           exclude_binaries=True,
           name='MovieFlix',
           debug=False,
           bootloader_ignore_signals=False,
           strip=False,
           upx=True,
           console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[])
