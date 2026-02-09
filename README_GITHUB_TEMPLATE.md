# 🎬 MovieFlix - Personal Netflix-Style Movie Library

Transform your local movie and TV show collection into a beautiful, Netflix-style streaming experience!

![MovieFlix](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey)
![License](https://img.shields.io/badge/license-Personal%20Use-green)

## ✨ Features

🎨 **Netflix-Style Interface**
- Beautiful card-based UI with movie posters
- Featured movie banner
- Continue watching section
- Smooth scrolling and animations

📊 **Smart Library Management**
- Automatic movie and TV series detection
- Episode tracking with season/episode numbers
- Resume playback from where you left off
- Watch history and recommendations

🎬 **Integrated Video Player**
- Standalone player window (VLC-based)
- Full playback controls
- Keyboard shortcuts
- Fullscreen support

📡 **Metadata & Posters**
- Automatic poster fetching from TMDB
- Movie descriptions and ratings
- Background poster loading (every 30 seconds)
- Trending movies and series

🔄 **Auto-Next Episode**
- Netflix-style countdown overlay
- Smart credit detection
- Automatic episode progression
- Cancel option to watch credits

💾 **External Drive Support**
- Auto-detect connected drives
- Quick import from USB/external HDDs
- Full PC scanning capability

## 📥 Download

### Latest Release: v1.0.0

**🎯 Recommended for Most Users:**

**[📦 Download Full Installer (250MB)](YOUR_GOOGLE_DRIVE_LINK)**
- Everything included (VLC bundled)
- One-click installation
- Start menu integration
- Automatic uninstaller

**[📦 Download Portable Version (250MB)](YOUR_GOOGLE_DRIVE_LINK)**
- No installation required
- Run from anywhere (USB drive compatible)
- Includes VLC player

---

**💡 Lightweight Option:**

**[📦 Download Lite Version (90MB)](https://github.com/yourusername/movieflix/releases/latest)**
- Smaller download size
- Requires VLC installed separately
- [Download VLC here](https://www.videolan.org/vlc/)

---

**📦 Optional Downloads:**

**[VLC Portable (70MB)](YOUR_GOOGLE_DRIVE_LINK)**
- For use with Lite version
- Extract to MovieFlix folder

---

## 🚀 Quick Start

### Using Installer (Recommended)
1. Download `MovieFlix_Setup_v1.0.0.exe`
2. Run the installer
3. Choose installation location
4. Choose library location
5. Launch MovieFlix
6. Create account and login
7. Scan your library!

### Using Portable Version
1. Download and extract `MovieFlix_Full_v1.0.zip`
2. Open the extracted folder
3. Run `MovieFlix.exe`
4. Create account and login
5. Add movies to the `library` folder
6. Click "Scan Library" in user menu

### Using Lite Version
1. Install [VLC Media Player](https://www.videolan.org/vlc/)
2. Download and extract `MovieFlix_Lite_v1.0.zip`
3. Run `MovieFlix.exe`
4. Follow setup wizard

📖 **[Full User Guide →](USER_README.txt)**

## 🎯 System Requirements

### Minimum
- **OS**: Windows 10 64-bit or Windows 11
- **RAM**: 4GB
- **Storage**: 500MB for application
- **Display**: 1280x720 minimum

### Recommended
- **OS**: Windows 11
- **RAM**: 8GB or more
- **Storage**: 1GB for application + space for media
- **Display**: 1920x1080 or higher
- **Internet**: For poster fetching

### Dependencies
- **VLC Media Player** (included in full versions)
- No Python required
- No other dependencies needed

## 📂 Library Organization

### Movies
```
library/
├── Inception (2010).mkv
├── The Matrix (1999).mp4
├── Interstellar (2014).mkv
└── Avatar (2009).avi
```

### TV Series
```
library/
└── Breaking Bad/
    ├── Breaking.Bad.S01E01.mkv
    ├── Breaking.Bad.S01E02.mkv
    ├── Breaking.Bad.S02E01.mkv
    └── Breaking.Bad.S02E02.mkv
```

**Supported Formats**: MP4, MKV, AVI, MOV, WMV, FLV, and more

**Naming Patterns for Series**:
- `Show.S01E01.mkv`
- `Show.1x01.mkv`
- `Show - 01x01.mkv`

## 🎮 Keyboard Shortcuts

### Main Window
- `Ctrl+S` - Scan Library
- `Ctrl+Q` - Quit Application

### Video Player
- `Space` - Play/Pause
- `F` - Toggle Fullscreen
- `→` - Skip Forward 10s
- `←` - Skip Backward 10s
- `↑` - Volume Up
- `↓` - Volume Down
- `M` - Mute/Unmute
- `Esc` - Exit Fullscreen

## 🛠️ For Developers

### Prerequisites
- Python 3.11+
- Git

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/yourusername/movieflix.git
cd movieflix

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run application
python start_movieflix.py
```

### Build Executable

**Portable + Installer:**
```bash
deploy_complete.bat
```

**Split Packages (for GitHub):**
```bash
build_split_packages.bat
```

**Check if ready to build:**
```bash
check_deployment_ready.bat
```

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed build instructions.

## 📁 Project Structure

```
movieflix/
├── app/                    # Frontend UI components
│   ├── advanced_ui.py     # Main UI
│   ├── standalone_player.py  # Video player
│   └── ...
├── backend/               # Backend API
│   ├── main.py           # FastAPI server
│   ├── scanner.py        # Library scanner
│   ├── metadata.py       # TMDB integration
│   └── ...
├── VLC/                   # VLC portable (bundled)
├── library/               # User's media library
├── MovieFlix.spec         # PyInstaller config
├── requirements.txt       # Python dependencies
└── start_movieflix.py    # Application launcher
```

## 🔧 Configuration

### TMDB API Key (Optional but Recommended)
MovieFlix uses [The Movie Database (TMDB)](https://www.themoviedb.org/) for posters and metadata.

1. Create free account at https://www.themoviedb.org/
2. Go to Settings → API → Request API Key
3. Copy your API key
4. Edit `.env` file:
   ```env
   TMDB_API_KEY=your_api_key_here
   ```
5. Restart MovieFlix

## 🐛 Troubleshooting

### App won't start
- Check Windows Defender (may block unsigned exe)
- Right-click exe → Properties → Unblock
- Try running as Administrator

### No video playback
- **Full version**: VLC is bundled, should work
- **Lite version**: Install VLC from https://www.videolan.org/

### Posters not loading
- Check internet connection
- Add TMDB API key (see Configuration)
- Wait 30 seconds (auto-loads in background)

### Database errors
- Close MovieFlix
- Delete `backend/movies.db`
- Restart and rescan library

**[📖 Full Troubleshooting Guide →](USER_README.txt)**

## 📄 License

This software is for personal use only. See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[The Movie Database (TMDB)](https://www.themoviedb.org/)** - Movie metadata and posters
- **[VLC Media Player](https://www.videolan.org/)** - Video playback engine
- **[PyQt5](https://www.riverbankcomputing.com/software/pyqt/)** - UI framework
- **[FastAPI](https://fastapi.tiangolo.com/)** - Backend framework

## 📧 Support

- 🐛 **[Report bugs](https://github.com/yourusername/movieflix/issues)**
- 💡 **[Request features](https://github.com/yourusername/movieflix/issues)**
- 📖 **[Documentation](USER_README.txt)**

## 🗺️ Roadmap

### v1.1 (Coming Soon)
- [ ] Subtitle support
- [ ] Audio track selection
- [ ] Movie trailers
- [ ] Better search functionality

### v2.0 (Future)
- [ ] Web interface
- [ ] Mobile apps
- [ ] Chromecast support
- [ ] Multi-user profiles
- [ ] Shared libraries

## ⭐ Star This Repo

If you find MovieFlix useful, please give it a star! It helps others discover the project.

---

**Made with ❤️ for movie enthusiasts**

*Transform your movie collection into your personal streaming service!*
