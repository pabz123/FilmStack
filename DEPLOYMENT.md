# MovieFlix Deployment Guide

## 📦 Building the Executable

### Quick Build (Recommended)
Simply run:
```batch
build_exe.bat
```

This will:
1. Install PyInstaller
2. Clean old builds
3. Create MovieFlix.exe (takes 2-5 minutes)
4. Place it in the dist\MovieFlix folder

---

## 📁 Distribution Package

The dist\MovieFlix folder will contain:
```
MovieFlix/
├── MovieFlix.exe       # Main executable
├── backend/            # Backend modules
├── app/                # UI components  
├── VLC/                # VLC libraries (if exists)
├── .env                # Configuration
└── library/            # (You'll create this)
```

---

## 🚀 Deployment Steps

### Option 1: Single PC Install
1. Copy the entire `dist\MovieFlix` folder to desired location
2. Create a `library` folder inside
3. Run `MovieFlix.exe`

### Option 2: Create Installer (Advanced)
Use Inno Setup to create an installer:
1. Install Inno Setup (https://jrsoftware.org/isinfo.php)
2. Create installer script (see below)
3. Compile to create Setup.exe

---

## 📝 Inno Setup Script (Optional)

Create `MovieFlix_Installer.iss`:

```inno
[Setup]
AppName=MovieFlix
AppVersion=1.0
DefaultDirName={autopf}\MovieFlix
DefaultGroupName=MovieFlix
OutputDir=installer
OutputBaseFilename=MovieFlix_Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\MovieFlix\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\MovieFlix"; Filename: "{app}\MovieFlix.exe"
Name: "{autodesktop}\MovieFlix"; Filename: "{app}\MovieFlix.exe"

[Run]
Filename: "{app}\MovieFlix.exe"; Description: "Launch MovieFlix"; Flags: postinstall nowait
```

---

## ⚙️ Requirements

### For Building:
- Python 3.11+ with venv
- All dependencies installed
- PyInstaller (auto-installed by build script)

### For Running:
- Windows 10/11
- VLC installed (or included in package)
- No Python required!

---

## 🐛 Troubleshooting

### Build fails?
1. Make sure venv is activated: `venv\Scripts\activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Run build_exe.bat again

### Exe won't start?
1. Check if antivirus is blocking it
2. Run from command line to see errors: `MovieFlix.exe`
3. Make sure VLC folder is included

### Missing VLC?
If VLC folder doesn't exist, users need VLC installed on their PC, or:
- Download VLC portable
- Extract to MovieFlix folder as "VLC"

---

## 📤 Sharing

### Zip for Distribution:
1. Compress `dist\MovieFlix` folder
2. Name it: `MovieFlix_v1.0_Portable.zip`
3. Share with users

### What to Include:
- ✅ dist\MovieFlix folder (entire)
- ✅ README.txt with instructions
- ✅ Sample .env file
- ❌ Don't include: build/, __pycache__, venv/

---

## 📋 User Instructions (Include in README.txt)

```
MovieFlix - Personal Streaming Library
======================================

Installation:
1. Extract all files to a folder (e.g., C:\MovieFlix)
2. Create a "library" folder inside
3. Add your movies and series to the library folder
4. Run MovieFlix.exe

Usage:
- Movies: Just .mp4, .mkv, .avi files
- Series: Name like "Show.S01E01.mkv"
- Scan: User menu → Scan Library
- Play: Click any card to watch

Enjoy! 🎬
```

---

## ✅ Final Checklist

Before distributing:
- [ ] Test exe on clean Windows install
- [ ] Verify VLC integration works
- [ ] Test scanning movies/series
- [ ] Test TMDB poster fetching
- [ ] Check external drive detection
- [ ] Verify database creation works
- [ ] Test all menu options
- [ ] Include user documentation

---

Happy Deploying! 🚀
