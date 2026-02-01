# VLC Setup Guide for MovieFlix

## Option 1: Use System-Installed VLC (Easiest)

If you already have VLC installed, MovieFlix will automatically find it!

**No action needed** - just make sure VLC is installed:
- Download from: https://www.videolan.org/vlc/
- Install normally
- MovieFlix will detect it automatically

---

## Option 2: Local VLC Directory (Portable/Self-Contained)

For a truly portable MovieFlix with bundled VLC:

### Step 1: Create VLC Directory
```bash
mkdir vlc
```

### Step 2: Copy VLC Files

**From your VLC installation** (usually `C:\Program Files\VideoLAN\VLC\`):

Copy these files to `D:\movie_library\vlc\`:

#### Essential Files:
```
vlc/
├── libvlc.dll                 ← Core VLC library
├── libvlccore.dll             ← Core engine
├── vlc.exe                    ← VLC executable (optional)
├── plugins/                   ← ALL plugin folders
│   ├── access/
│   ├── audio_filter/
│   ├── audio_mixer/
│   ├── audio_output/
│   ├── codec/
│   ├── control/
│   ├── demux/
│   ├── video_output/
│   └── ... (copy ALL plugin folders)
└── locale/                    ← Language files (optional)
```

### Step 3: Quick Copy Command

**Windows PowerShell:**
```powershell
# Copy entire VLC installation
$vlcSource = "C:\Program Files\VideoLAN\VLC"
$vlcDest = "D:\movie_library\vlc"

# Create directory
New-Item -ItemType Directory -Path $vlcDest -Force

# Copy all files
Copy-Item -Path "$vlcSource\*" -Destination $vlcDest -Recurse -Force

Write-Host "VLC copied to local directory!"
```

**Or manually:**
1. Open `C:\Program Files\VideoLAN\VLC\`
2. Select all files and folders
3. Copy to `D:\movie_library\vlc\`

---

## Structure After Setup

```
movie_library/
├── vlc/                        ← Local VLC (optional)
│   ├── libvlc.dll
│   ├── libvlccore.dll
│   ├── plugins/
│   │   ├── access/
│   │   ├── codec/
│   │   ├── video_output/
│   │   └── ... (many more)
│   └── locale/
│
├── app/
├── backend/
├── venv/
└── ...
```

---

## How MovieFlix Finds VLC

**Search Order:**
1. **Local `vlc/` directory** (if exists)
2. `C:\Program Files\VideoLAN\VLC`
3. `C:\Program Files (x86)\VideoLAN\VLC`
4. System PATH

**The embedded_player.py automatically:**
- Searches all these locations
- Adds found paths to environment
- Loads VLC library
- Shows status in console

---

## Verification

### Test if VLC is Found:
```bash
cd D:\movie_library
venv\Scripts\activate
python -c "import vlc; print('VLC version:', vlc.libvlc_get_version().decode())"
```

**Expected output:**
```
✓ Found local VLC directory: D:\movie_library\vlc
✓ VLC module loaded successfully
VLC version: 3.0.21 Vetinari
```

---

## Benefits of Local VLC

### ✅ Advantages:
- **Portable**: Take MovieFlix anywhere
- **No system installation needed**
- **Version control**: Specific VLC version
- **No conflicts**: Isolated from system VLC
- **Self-contained**: Everything in one folder

### ⚠️ Disadvantages:
- Larger folder size (~100-150 MB)
- Need to update manually
- Takes more disk space

---

## Troubleshooting

### VLC Not Found
```bash
# Check if VLC directory exists
dir vlc\libvlc.dll

# If missing, copy from system
Copy-Item "C:\Program Files\VideoLAN\VLC\*" -Destination "vlc\" -Recurse
```

### Python Can't Load VLC
```bash
# Install python-vlc
pip install python-vlc

# Test
python -c "import vlc; print(vlc.libvlc_get_version())"
```

### Missing DLLs Error
```
Error: "libvlc.dll not found"
```

**Solution**: Copy entire VLC folder, not just DLL files.
The `plugins/` folder is essential!

---

## File Sizes Reference

| Component | Size |
|-----------|------|
| libvlc.dll | ~150 KB |
| libvlccore.dll | ~5 MB |
| plugins/ (all) | ~100 MB |
| Total | ~110 MB |

---

## Minimal VLC Setup (Advanced)

For smallest size, copy only these plugins:

### Core Plugins Only:
```
vlc/
├── libvlc.dll
├── libvlccore.dll
└── plugins/
    ├── access/          (file access)
    ├── audio_output/    (audio playback)
    ├── codec/           (video codecs - MP4, MKV, etc.)
    ├── demux/           (file parsing)
    └── video_output/    (video rendering)
```

**Size**: ~50 MB (half the full size)

**Risk**: Some formats may not play

---

## Recommended: Use System VLC

**For most users**, just install VLC normally:
1. Download VLC from https://www.videolan.org/
2. Install it
3. MovieFlix finds it automatically
4. No manual copying needed!

**Only use local VLC if:**
- You want a portable installation
- You need specific VLC version
- You're distributing MovieFlix to others

---

## Quick Commands

### Copy VLC Locally:
```powershell
Copy-Item "C:\Program Files\VideoLAN\VLC\*" -Destination "vlc\" -Recurse -Force
```

### Test VLC:
```bash
python -c "import vlc; print('OK')"
```

### Check MovieFlix VLC Detection:
```bash
python app/embedded_player.py
```

---

**Recommendation**: Start with system VLC. Add local VLC later if needed!
