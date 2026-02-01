# 🎬 MovieFlix - Personal Netflix-Style Streaming Library

A beautiful, feature-rich personal movie streaming application with a Netflix-inspired UI, built with PyQt5 and FastAPI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)

## ✨ Features

### 🎥 Enhanced Video Player
- **VLC-powered playback** - All video formats supported
- **Skip controls** - Jump forward/backward 10 seconds
- **Subtitle support** - Auto-detect .srt files or load external subtitles
- **Audio track selection** - Switch between multiple audio tracks
- **Playback speed control** - Watch at 0.5x to 2.0x speed
- **Next episode** - Binge-watch series seamlessly
- **Keyboard shortcuts** - Full keyboard control

### 🎨 Beautiful UI
- **Netflix-style interface** - Modern, sleek design
- **Movie posters** - Auto-fetched from TMDB (94% coverage)
- **Smooth animations** - Hover effects and transitions
- **Responsive layout** - Maximized window fits your screen perfectly
- **Dark theme** - Easy on the eyes

### 🚀 Smart Features
- **Auto library scanning** - Detects movies and series automatically
- **TMDB metadata** - Fetches posters, ratings, and descriptions
- **Watch history** - Tracks what you've watched
- **Resume playback** - Continue where you left off
- **Series management** - Organized by seasons and episodes
- **Smart navigation** - Returns to exact position after watching

### 🎯 User Experience
- **Silent startup** - No console windows, professional app experience
- **Desktop shortcut** - One-click launch with custom icon
- **Fullscreen mode** - Immersive viewing that covers entire screen

## 📋 Requirements

- **Python 3.8+**
- **VLC Media Player** (bundled in VLC/ folder)
- **Windows** (Linux/macOS compatible with minor adjustments)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup TMDB API (Optional, for posters)
Create a `.env` file:
```env
TMDB_API_KEY=your_api_key_here
API_PORT=8765
API_HOST=127.0.0.1
```
Get a free API key from [TMDB](https://www.themoviedb.org/settings/api)

### 3. Create Desktop Shortcut
```bash
create_desktop_shortcut.bat
```

### 4. Launch MovieFlix
Double-click the **MovieFlix** icon on your desktop!

**Default Login:**
- Username: `admin`
- Password: `admin123`

## 📂 Project Structure

```
movie_library/
├── app/                          # Frontend (PyQt5)
│   ├── advanced_ui.py           # Main UI
│   ├── embedded_player.py       # VLC video player
│   ├── advanced_widgets.py      # Movie cards
│   └── launcher.py              # Startup
├── backend/                      # API (FastAPI)
│   ├── main.py                  # Endpoints
│   ├── models.py                # Database
│   ├── scanner.py               # Library scanner
│   └── metadata.py              # TMDB integration
├── library/                      # Your movies go here
├── VLC/                          # VLC player
├── start_movieflix.py           # Main entry
├── create_desktop_shortcut.bat  # Desktop icon
└── update_tmdb_metadata.py      # Fetch posters
```

## 🎮 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `F` | Fullscreen |
| `←` / `→` | Skip ±10s |
| `↑` / `↓` | Volume |
| `M` | Mute |
| `S` | Subtitles |
| `A` | Audio tracks |
| `N` | Next episode |
| `Esc` | Exit fullscreen |

## 🎬 Usage

### Adding Movies
1. Place video files in `library/` folder
2. For series: `library/SeriesName/Season 1/episode.mp4`
3. MovieFlix auto-scans on startup

### Fetching Posters
```bash
venv\Scripts\python.exe update_tmdb_metadata.py
```

## 🛠️ Tech Stack

- **Frontend:** PyQt5
- **Backend:** FastAPI + SQLAlchemy
- **Database:** SQLite
- **Video:** python-vlc
- **Metadata:** TMDB API

## 🐛 Troubleshooting

### Backend won't start
```bash
kill_port_8765.bat
```

### No posters
1. Add `TMDB_API_KEY` to `.env`
2. Run `update_tmdb_metadata.py`

### Debug mode
```bash
debug_startup.bat
```

## 📊 Status

✅ All core features working  
✅ 31/33 movies with posters (94%)  
✅ Enhanced video player  
✅ Silent desktop launcher  
✅ Smart navigation  

## 📄 License

MIT License

---

**Made with ❤️ for movie lovers**

Version 2.1 | February 2026
