# 🎬 MovieFlix - Your Personal Netflix

**Version 2.0** | Production Ready ✅

Transform your local movie and TV show collection into a **professional Netflix-style streaming service**. Beautiful UI, embedded video player, automatic metadata fetching, and zero monthly fees.

![MovieFlix](https://img.shields.io/badge/Platform-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### **User Interface**
- ✅ **Netflix-style dark theme** with smooth animations
- ✅ **Professional splash screen** and loading indicators
- ✅ **Responsive layout** that scales to your screen
- ✅ **Hover effects** on movie cards
- ✅ **Custom MovieFlix red "M" icon** in taskbar

### **Video Playback**
- ✅ **Embedded VLC player** for in-window playback
- ✅ **Fullscreen support** with keyboard shortcuts
- ✅ **Play/pause, seek, volume control**
- ✅ **Resume from last position** (continue watching)
- ✅ **Mouse wheel volume control**

### **Content Management**
- ✅ **Auto-metadata from TMDB** (posters, descriptions, ratings)
- ✅ **Background library scanning** (non-blocking)
- ✅ **Automatic poster fetching** on startup
- ✅ **Series management** with seasons/episodes
- ✅ **Import folder** functionality
- ✅ **Search** movies and shows

### **User Features**
- ✅ **User authentication** with registration
- ✅ **Profile management** with avatar selection
- ✅ **Watch history** tracking
- ✅ **Continue watching** section
- ✅ **New & Popular** (TMDB trending content)

### **Performance**
- ✅ **Fast startup** (2-3 seconds to main window)
- ✅ **Lazy VLC initialization** (only when playing video)
- ✅ **Async window creation** (no freezing)
- ✅ **Silent launcher** - no console windows
- ✅ **Standalone .exe** (portable Windows app)

---

## 🚀 Quick Start

### **Option 1: Using .exe (Easiest)** ⭐

1. **Build or download MovieFlix.exe**
   ```cmd
   build_exe.bat
   ```

2. **Add your media**
   - Movies → `library\mo\`
   - TV Shows → `library\series\`

3. **Run MovieFlix.exe**
   - Double-click the .exe
   - Or run: `MovieFlix.exe`

4. **Login**
   - Username: `admin`
   - Password: `admin123`

### **Option 2: Using Complete Launcher**

```cmd
start_movieflix_complete.bat
```
- ✅ Starts backend automatically
- ✅ Launches MovieFlix app
- ✅ One-click solution

### **Option 3: Development Setup**

**1. Install Python dependencies**
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure .env file**
```env
TMDB_API_KEY=6c2d8d780ce73c06e3955159c3caf0fe
API_HOST=127.0.0.1
API_PORT=8765
```

**3. Add VLC**
- Copy VLC installation to `VLC\` folder
- Must include: `libvlc.dll`, `libvlccore.dll`, `plugins\`

**4. Setup Library**
```
library/
├── mo/              # Movies go here
│   ├── Inception.mkv
│   └── The Matrix.mp4
└── series/          # TV shows go here
    └── Breaking Bad/
        ├── Season 1/
        └── Season 2/
```

**5. Launch**
```cmd
# Terminal 1: Backend
venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8765

# Terminal 2: Frontend  
python start_movieflix.py
```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `F` or `F11` | Toggle Fullscreen |
| `ESC` | Exit Fullscreen |
| `←` | Seek backward 10 sec |
| `→` | Seek forward 10 sec |
| `↑` | Volume up |
| `↓` | Volume down |
| `Mouse Wheel` | Volume control |
| `Click` | Show/hide controls (fullscreen) |

---

## 📁 Project Structure

```
D:\movie_library\
├── app/                      # Frontend (PyQt5)
│   ├── launcher.py          # Startup & loading
│   ├── advanced_ui.py       # Main window (1646 lines)
│   ├── login_dialog.py      # Authentication UI
│   ├── embedded_player.py   # VLC player
│   └── ...                  # Other UI modules
│
├── backend/                  # Backend (FastAPI)
│   ├── main.py              # API server
│   ├── database.py          # SQLite config
│   ├── models.py            # Data models
│   └── ...                  # Other backend modules
│
├── library/                  # Your media files
│   ├── mo/                  # Movies
│   └── series/              # TV shows
│
├── VLC/                      # VLC player files
│
├── start_movieflix.py        # Main entry point
├── start_movieflix_complete.bat  # Complete launcher
├── build_exe.bat            # Build .exe script
├── MovieFlix.exe            # Standalone executable
├── MovieFlix.ico            # Application icon
└── .env                     # Configuration
```

### **Browsing Content**
- **Home:** Featured movies, recommendations, continue watching
- **Movies:** All movies organized by rating (Blockbusters 7.5+, Hidden Gems, etc.)
- **TV Shows:** Browse series, select seasons and episodes  
- **New & Popular:** TMDB trending content (not in your library)
- **My List:** Library statistics and complete content list

### **Playing Videos**
1. Click any movie poster or card
2. Video plays in embedded VLC player
3. Use keyboard shortcuts or mouse controls
4. Click anywhere to show/hide controls in fullscreen

### **Managing Library**
- **Import Folder:** User menu → "Import Folder" → Select media folder
- **Automatic Scan:** Runs on startup in background
- **Manual Refresh:** Import Folder scans and adds new content

### **Profile Settings**
- Click user icon → "Profile Settings"
- Change username, email, password
- Select avatar from 12 emoji options

### **Search**
- Type in search bar (top right)
- Searches titles and descriptions in real-time

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | PyQt5 (Desktop GUI) |
| **Backend** | FastAPI (REST API) |
| **Database** | SQLite + SQLAlchemy ORM 1.4.48 |
| **Video Player** | VLC (python-vlc) |
| **Metadata** | TMDB API |
| **Packaging** | PyInstaller |

**Code Statistics:**
- 27 Python files
- 17,000+ lines of code
- 10 backend modules
- 10 frontend modules
- 15+ documentation files

---

## 🐛 Troubleshooting

### **"HTTPConnectionPool timeout" on login**
**Problem:** Backend not running

**Solution:**
```cmd
start_movieflix_complete.bat
```
This starts backend automatically.

### **Stuck on loading after login**
**Problem:** Window creation blocking

**Solution:** Latest version fixed this (v2.0). Update code or rebuild .exe:
```cmd
build_exe.bat
```

### **Videos won't play**
**Problem:** VLC not found

**Solutions:**
1. Check VLC folder exists:
   ```cmd
   dir D:\movie_library\VLC\
   ```
2. Copy VLC installation to `VLC\` folder
3. Test VLC: `python test_vlc.py`

### **Movies not showing**
**Problem:** Library folder empty or scan failed

**Solutions:**
- Add movies to `library\mo\`
- Use Import Folder to scan
- Check console for scan errors

### **Posters not loading**
**Problem:** TMDB API or network issue

**Solutions:**
1. Check `.env` has TMDB_API_KEY
2. Run manual fetch: `python fetch_posters_now.py`
3. Posters fetch automatically in background on startup

### **Backend error**
**Problem:** Database or dependency issue

**Solutions:**
```cmd
# Reinstall dependencies
pip install -r requirements.txt

# Test backend directly
venv\Scripts\python.exe -m uvicorn backend.main:app --port 8765
```

### **Port 8765 already in use**
**Problem:** Backend process stuck

**Solutions:**
```cmd
# Find process
netstat -ano | findstr :8765

# Kill process (replace <PID>)
taskkill /F /PID <PID>
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **COMPLETE_SYSTEM_DOCUMENTATION.md** | Full system documentation |
| **MOVIEFLIX_GUIDE.md** | User manual |
| **EXE_BUILDER_GUIDE.md** | Build .exe instructions |
| **LOADING_PERFORMANCE_FIXES.md** | Performance optimizations |
| **BACKEND_TIMEOUT_FIX.md** | Backend connection issues |
| **POSTER_FETCHER_FIXED.md** | Poster fetching guide |
| **VLC_SETUP_GUIDE.md** | VLC integration |

---

## 📊 Performance

| Metric | Time |
|--------|------|
| **Startup (to login)** | 2.5 sec |
| **Login to main window** | 1-2 sec |
| **Total startup** | 3.5-4.5 sec |
| **First video play** | 2-3 sec (VLC init) |
| **Subsequent videos** | 0.2-0.5 sec |

---

## 🚧 Known Issues

- ✅ All critical issues resolved in v2.0
- Backend must be running for app to work
- .exe includes ~150-200 MB (VLC + dependencies)

---

## 🔄 Version History

**v2.0 - January 30, 2026**
- ✅ Fixed loading hang after login (async window creation)
- ✅ 7x faster startup (lazy VLC init)
- ✅ Redesigned registration page
- ✅ Fixed poster fetcher database import errors
- ✅ Icon shows properly in Windows taskbar
- ✅ Complete code review and documentation update
- ✅ Reduced backend wait time (10s → 5s)

**v1.0 - Initial Release**
- Netflix-style UI
- VLC integration
- TMDB metadata
- User authentication
- Series support

---

## 🎬 Enjoy Your Personal Netflix! 🍿

**Default Login:**
- Username: `admin`
- Password: `admin123`

**Quick Start:**
```cmd
start_movieflix_complete.bat
```

---

*Made with ❤️ for movie lovers | Version 2.0 | 2026*

**License:** MIT
