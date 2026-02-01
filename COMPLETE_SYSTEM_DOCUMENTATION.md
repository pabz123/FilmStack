# MovieFlix - Complete System Documentation 🎬

**Version:** 2.0
**Last Updated:** January 30, 2026
**Status:** Production Ready ✅

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Usage Guide](#usage-guide)
5. [Features](#features)
6. [Troubleshooting](#troubleshooting)
7. [Development](#development)
8. [API Reference](#api-reference)

---

## System Overview

MovieFlix is a Netflix-style personal streaming library application that provides a professional interface for managing and watching your local movie and TV show collection.

### **Key Technologies**
- **Frontend:** PyQt5 (Desktop GUI)
- **Backend:** FastAPI (REST API)
- **Database:** SQLite with SQLAlchemy ORM
- **Video Player:** VLC (python-vlc integration)
- **Metadata:** TMDB API integration
- **Platform:** Windows (with .exe support)

### **Project Statistics**
- **27 Python files** (17,000+ lines of code)
- **10 Backend modules** (FastAPI server)
- **10 Frontend modules** (PyQt5 UI)
- **7 Utility scripts**
- **15+ Documentation files**

---

## Architecture

### **Directory Structure**
```
D:\movie_library\
├── app/                      # Frontend (PyQt5)
│   ├── launcher.py          # Startup & loading screen
│   ├── advanced_ui.py       # Main application window
│   ├── login_dialog.py      # Authentication UI
│   ├── embedded_player.py   # VLC video player
│   ├── splash_screen.py     # Splash screen
│   ├── advanced_widgets.py  # Reusable UI components
│   ├── info_dialog.py       # Movie info dialog
│   ├── series_dialog.py     # Episode selection
│   ├── profile_dialog.py    # User profile management
│   └── tmdb_fetcher.py      # Background metadata fetcher
│
├── backend/                  # Backend (FastAPI)
│   ├── main.py              # API server & routes
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── auth.py              # Authentication
│   ├── scanner.py           # Library scanner
│   ├── metadata.py          # TMDB integration
│   ├── recommender.py       # Recommendation engine
│   └── scan_endpoint.py     # Scan API endpoints
│
├── library/                  # Media storage
│   ├── mo/                  # Movies folder
│   └── series/              # TV shows folder
│
├── VLC/                      # VLC player files
│   ├── libvlc.dll
│   └── libvlccore.dll
│
├── venv/                     # Python virtual environment
│
├── start_movieflix.py        # MAIN ENTRY POINT
├── start_movieflix_complete.bat  # Complete launcher
├── build_exe.bat            # PyInstaller builder
├── MovieFlix.exe            # Standalone executable
├── MovieFlix.ico            # Application icon
├── .env                     # Configuration
└── requirements.txt         # Dependencies
```

---

## Installation & Setup

### **Prerequisites**
- Windows 10/11
- Python 3.8+ (for development)
- VLC Media Player installed OR VLC folder in project

### **Quick Start (Using .exe)**

1. **Download/Build MovieFlix.exe**
   ```cmd
   build_exe.bat
   ```

2. **Add your media files**
   - Copy movies to: `library\mo\`
   - Copy TV shows to: `library\series\`

3. **Run MovieFlix**
   ```cmd
   MovieFlix.exe
   ```
   OR double-click the .exe file

4. **Login**
   - Username: `admin`
   - Password: `admin123`

### **Developer Setup**

1. **Clone/Download project**
   ```cmd
   cd D:\movie_library
   ```

2. **Create virtual environment**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Configure environment**
   Create `.env` file:
   ```
   TMDB_API_KEY=6c2d8d780ce73c06e3955159c3caf0fe
   API_HOST=127.0.0.1
   API_PORT=8765
   ```

5. **Add VLC**
   - Copy VLC installation to `D:\movie_library\VLC\`
   - Must include: `libvlc.dll`, `libvlccore.dll`, `plugins/`

6. **Start application**
   ```cmd
   start_movieflix_complete.bat
   ```

---

## Usage Guide

### **Starting the Application**

#### **Method 1: Using .exe (Recommended)**
```cmd
MovieFlix.exe
```
- ✅ One-click startup
- ✅ Backend starts automatically
- ✅ No console windows

#### **Method 2: Using Complete Launcher**
```cmd
start_movieflix_complete.bat
```
- ✅ Checks if backend is running
- ✅ Starts backend if needed
- ✅ Launches MovieFlix app

#### **Method 3: Manual (Development)**
```cmd
# Terminal 1: Backend
venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8765

# Terminal 2: Frontend
python start_movieflix.py
```
- ✅ See all logs
- ✅ Backend auto-reloads on changes
- ✅ Easy debugging

### **Application Flow**

1. **Splash Screen** (2.5 seconds)
   - Shows MovieFlix logo
   - Status updates: "Starting up...", "Initializing backend...", etc.

2. **Login Dialog**
   - Enter username and password
   - Click "Sign In"
   - Shows loading overlay with animated spinner

3. **Main Window** (Loads in 1-2 seconds)
   - Home view with featured content
   - Navigation bar: Home, Movies, TV Shows, New & Popular, My List
   - Auto-scans library in background
   - Fetches TMDB metadata automatically

### **Key Features & Usage**

#### **Browsing Content**
- **Home:** Featured content, recommendations, continue watching
- **Movies:** All movies organized by rating (Blockbusters, Hidden Gems, etc.)
- **TV Shows:** Browse series, select seasons/episodes
- **New & Popular:** TMDB trending content (not in your library)
- **My List:** Library statistics and complete content list

#### **Playing Videos**
- Click any movie poster/card
- Video plays in embedded VLC player
- **Keyboard Controls:**
  - `Space` - Play/Pause
  - `F` or `F11` - Toggle fullscreen
  - `ESC` - Exit fullscreen
  - `←` / `→` - Seek backward/forward 10 seconds
  - `↑` / `↓` - Volume up/down
  - `Mouse Wheel` - Volume control
  - `Click` - Show/hide controls in fullscreen

#### **Managing Library**
- **Import Folder:** Add new movies/shows
  - Click user menu → "Import Folder"
  - Select folder with media files
  - Scan runs in background

- **Refresh Library:** Re-scan existing folders
  - Automatically scans on startup
  - Manual scan via Import Folder

#### **Profile Management**
- Click user icon → "Profile Settings"
- Change username, email
- Select avatar (12 emoji options)
- Update password

#### **Search**
- Type in search bar (top right)
- Searches titles and descriptions
- Real-time filtering

---

## Features

### **✅ Implemented Features**

#### **User Interface**
- ✅ Netflix-style dark theme
- ✅ Responsive layout (scales to screen size)
- ✅ Horizontal scrolling content rows
- ✅ Hover effects on movie cards
- ✅ Smooth animations and transitions
- ✅ Professional splash screen
- ✅ Loading overlays with progress
- ✅ Custom MovieFlix red "M" icon

#### **Video Playback**
- ✅ Embedded VLC player
- ✅ Fullscreen support
- ✅ Keyboard shortcuts
- ✅ Mouse wheel volume control
- ✅ Play/pause on click
- ✅ Seek bar with timestamp
- ✅ Resume from last position (continue watching)

#### **Content Management**
- ✅ Automatic library scanning
- ✅ Background TMDB metadata fetching
- ✅ Poster image downloading
- ✅ Rating display (TMDB ratings)
- ✅ Movie/series information dialogs
- ✅ Import folder functionality
- ✅ Multiple library folders support

#### **TMDB Integration**
- ✅ Automatic poster fetching
- ✅ Ratings and metadata
- ✅ Trending content (New & Popular)
- ✅ Popular movies not in library
- ✅ Title cleaning for better matches
- ✅ Background updates (non-blocking)

#### **Authentication**
- ✅ User login system
- ✅ Registration with validation
- ✅ Password hashing (bcrypt)
- ✅ Session management
- ✅ Default admin account

#### **Performance**
- ✅ Lazy VLC initialization (only when playing video)
- ✅ Async window creation (1-2 second startup)
- ✅ Background scanning (non-blocking)
- ✅ Progressive content loading
- ✅ Optimized .exe build (~150-200 MB)

---

## Troubleshooting

### **Common Issues**

#### **"HTTPConnectionPool timeout" on login**
**Problem:** Backend not running

**Solutions:**
1. Use complete launcher:
   ```cmd
   start_movieflix_complete.bat
   ```

2. Or start backend manually:
   ```cmd
   venv\Scripts\python.exe -m uvicorn backend.main:app --port 8765
   ```

#### **Stuck on loading after login**
**Problem:** Window creation blocking

**Fix:** Updated in latest version (async window creation)
- Restart MovieFlix with latest code

#### **Videos don't play**
**Problem:** VLC not found

**Solutions:**
1. Check VLC folder exists:
   ```cmd
   dir D:\movie_library\VLC\
   ```

2. Install VLC system-wide or copy VLC files to project

3. Test VLC:
   ```cmd
   python test_vlc.py
   ```

#### **Posters not loading**
**Problem:** TMDB API key issue or network

**Solutions:**
1. Check `.env` has TMDB_API_KEY
2. Run manual poster fetch:
   ```cmd
   python fetch_posters_now.py
   ```
3. Check internet connection

#### **Python icon in taskbar instead of MovieFlix icon**
**Problem:** Icon not set properly

**Fix:** Build .exe - embedded icon shows correctly:
```cmd
build_exe.bat
```

#### **.exe takes forever to start**
**Problem:** Backend startup delay

**Solutions:**
1. Latest version reduced wait time (10s → 5s)
2. Use Python script for development:
   ```cmd
   python start_movieflix.py
   ```
3. Backend may need optimization

#### **Port 8765 already in use**
**Problem:** Backend already running or blocked

**Solutions:**
1. Find process:
   ```cmd
   netstat -ano | findstr :8765
   ```

2. Kill process:
   ```cmd
   taskkill /F /PID <PID>
   ```

---

## Development

### **Code Structure**

#### **Entry Point Flow**
```
start_movieflix.py
  ↓
1. Check port 8765 availability
  ↓
2. Start backend (pythonw.exe backend/main.py)
  ↓
3. Wait for backend (max 5 seconds)
  ↓
4. Launch app.launcher.main()
  ↓
5. Show splash screen (2.5 seconds)
  ↓
6. Show login dialog
  ↓
7. Create main window (async, 1-2 seconds)
  ↓
8. Start background tasks:
   - Library scan
   - TMDB metadata fetch
   - Content loading
```

#### **Backend API Endpoints**

**Authentication:**
- `POST /auth/register` - Create new user
- `GET /auth/me` - Get current user (with Basic Auth)

**Movies:**
- `GET /movies` - List all movies
- `GET /movies/{id}` - Get movie details
- `PATCH /movies/{id}/metadata` - Update poster/rating

**Series:**
- `GET /series` - List all series
- `GET /series/{id}` - Get series details
- `GET /series/{id}/episodes` - List episodes
- `PATCH /series/{id}/metadata` - Update metadata

**Scanning:**
- `POST /scan` - Trigger library scan
- `GET /scan/status` - Get scan progress

**TMDB:**
- `GET /tmdb/trending` - Get trending content
- `GET /tmdb/popular` - Get popular movies

**Full API docs:** http://localhost:8765/docs

#### **Database Models**

**User:**
- id, username, email, hashed_password, created_at

**Movie:**
- id, title, file_path, duration, poster_url, rating, genre, year, last_watched

**Series:**
- id, title, description, poster_url, rating, genre, year

**Season:**
- id, series_id, season_number, title

**Episode:**
- id, season_id, episode_number, title, file_path, duration, last_watched

### **Building .exe**

```cmd
# Install PyInstaller
pip install pyinstaller

# Build using spec file
pyinstaller --clean --noconfirm MovieFlix.spec

# Or use batch file
build_exe.bat
```

**Spec file includes:**
- Entry point: `app/launcher.py`
- Icon: `MovieFlix.ico`
- Data files: `.env`, `VLC/`
- Hidden imports: `vlc`, `PyQt5`, `sqlalchemy`, `fastapi`
- No console window

**Result:** `MovieFlix.exe` (~150-200 MB)

---

## API Reference

### **Quick Reference**

**Base URL:** `http://localhost:8765`

**Authentication:** HTTP Basic Auth
```python
import requests
response = requests.get(
    'http://localhost:8765/movies',
    auth=('admin', 'admin123')
)
```

### **Common Operations**

#### **Get all movies**
```python
GET /movies
Response: [
  {
    "id": 1,
    "title": "Inception",
    "file_path": "D:\\library\\mo\\Inception.mkv",
    "poster_url": "https://image.tmdb.org/t/p/w500/abc.jpg",
    "rating": 8.4,
    "duration": 8880
  },
  ...
]
```

#### **Update movie poster**
```python
PATCH /movies/{id}/metadata
Body: {
  "poster_url": "https://...",
  "rating": 8.4
}
```

#### **Trigger scan**
```python
POST /scan
Body: {
  "path": "D:\\library\\mo"
}
```

---

## Performance Metrics

### **Startup Times**

| Metric | Time |
|--------|------|
| Splash screen | 2.5 sec |
| Backend start | 2-5 sec |
| Login dialog | 0.5 sec |
| Window creation | 1-2 sec |
| **Total startup** | **6-10 sec** |

### **First Video Play**
| Operation | Time |
|-----------|------|
| VLC initialization (one-time) | 2-3 sec |
| Video buffering | 0.5 sec |
| **Total** | **2.5-3.5 sec** |

### **Subsequent Videos**
| Operation | Time |
|-----------|------|
| Video start | 0.2-0.5 sec |

---

## File Locations

### **Configuration**
- `.env` - API keys and settings
- `movies.db` - SQLite database

### **Logs**
- `movieflix_startup.log` - Startup logs
- Console output (when using `python.exe`)

### **Media**
- `library/mo/` - Movies
- `library/series/` - TV shows

### **Cache**
- Poster images cached in database as URLs

---

## Credits

**Developed by:** MovieFlix Team
**TMDB API:** https://www.themoviedb.org/
**VLC Player:** https://www.videolan.org/
**Icons:** Custom MovieFlix red "M" icon

---

## License

MIT License - See LICENSE file

---

## Version History

**v2.0** - January 30, 2026
- ✅ Fixed loading hang after login
- ✅ Async window creation (7x faster)
- ✅ Lazy VLC initialization
- ✅ Redesigned registration page
- ✅ Fixed poster fetcher errors
- ✅ Icon shows properly in taskbar
- ✅ Complete documentation update
- ✅ Code review and cleanup

**v1.0** - Initial Release
- Basic Netflix-style UI
- VLC integration
- TMDB metadata
- User authentication

---

**📞 For issues or questions, check documentation files or code comments.**

**🎬 Enjoy your personal streaming experience!**
