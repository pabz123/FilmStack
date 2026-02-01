# 🎬 MovieFlix v2.0 - Quick Reference Card

**Last Updated:** January 30, 2026 | **Status:** ✅ Production Ready

---

## 🚀 Quick Start

```cmd
# Easiest: One-click launcher
start_movieflix_complete.bat

# Or run the .exe
MovieFlix.exe

# Or build .exe
build_exe.bat
```

**Default Login:** `admin` / `admin123`

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `F` / `F11` | Fullscreen |
| `ESC` | Exit Fullscreen |
| `←` | Seek -10 sec |
| `→` | Seek +10 sec |
| `↑` | Volume Up |
| `↓` | Volume Down |
| `Click` | Show/Hide Controls |
| `Wheel` | Volume Control |

---

## 📁 File Locations

```
D:\movie_library\
├── library\mo\          # Put movies here
├── library\series\      # Put TV shows here
├── .env                 # API keys
├── movies.db            # Database
└── MovieFlix.exe        # Run this!
```

---

## 🐛 Common Issues

### Stuck on Loading
```cmd
# Latest version fixes this!
# Update code or rebuild .exe
build_exe.bat
```

### Backend Timeout
```cmd
# Use complete launcher
start_movieflix_complete.bat
```

### Videos Won't Play
```cmd
# Check VLC folder exists
dir VLC\
# Must have: libvlc.dll, libvlccore.dll
```

### No Posters
```cmd
# Run manual fetch
python fetch_posters_now.py
# Or wait - auto-fetches in background
```

### Port 8765 In Use
```cmd
# Find process
netstat -ano | findstr :8765
# Kill it (replace PID)
taskkill /F /PID <PID>
```

---

## 📊 Performance

| What | Time |
|------|------|
| **Startup** | 3-5 sec |
| **Login → Main Window** | 1-2 sec |
| **First Video** | 2-3 sec (VLC init) |
| **Next Videos** | 0.2-0.5 sec |

---

## 🔧 Commands

```cmd
# Start everything
start_movieflix_complete.bat

# Start manually (2 terminals)
venv\Scripts\python.exe -m uvicorn backend.main:app --port 8765
python start_movieflix.py

# Build .exe
build_exe.bat

# Fetch posters
python fetch_posters_now.py

# Test VLC
python test_vlc.py

# Backend API docs
http://localhost:8765/docs
```

---

## 📚 Key Documentation

| File | What |
|------|------|
| **README.md** | Quick start |
| **MOVIEFLIX_V2_COMPLETE_REPORT.md** | Full project report |
| **COMPLETE_SYSTEM_DOCUMENTATION.md** | System docs |
| **EXE_BUILDER_GUIDE.md** | Build .exe guide |
| **BACKEND_TIMEOUT_FIX.md** | Connection issues |

---

## ✅ What's Fixed in v2.0

- ✅ Loading hang after login (async window)
- ✅ Slow startup (lazy VLC, 7x faster)
- ✅ Registration page redesigned
- ✅ Poster fetcher errors fixed
- ✅ Icon shows in taskbar
- ✅ Backend auto-starts
- ✅ Complete documentation

---

## 🎯 Features

- ✅ Netflix-style UI
- ✅ Embedded VLC player
- ✅ Auto TMDB metadata
- ✅ Fullscreen playback
- ✅ Continue watching
- ✅ New & Popular
- ✅ Profile management
- ✅ Search
- ✅ Import folders
- ✅ Standalone .exe

---

## 📦 Tech Stack

- **Frontend:** PyQt5
- **Backend:** FastAPI
- **Database:** SQLite
- **Player:** VLC
- **Metadata:** TMDB

---

## 🎬 That's It!

**Start with:** `start_movieflix_complete.bat`

**Enjoy your personal Netflix!** 🍿
