# MovieFlix - Your Personal Streaming Library

Transform your movie and TV show collection into a Netflix-style streaming experience!

## 🎬 Features

- **Netflix-Style Interface**: Beautiful, modern UI with movie posters and descriptions
- **Automatic Organization**: Scans your folders and automatically organizes content
- **Smart Metadata**: Fetches movie posters, descriptions, and ratings from TMDB
- **Resume Playback**: Continue watching from where you left off
- **Series Tracking**: Automatically detects seasons and episodes
- **External Drive Support**: Scan USB drives and external hard drives
- **Auto-Next Episode**: Automatically plays the next episode (Netflix-style)
- **Built-in Player**: Integrated VLC player with full controls

## 📋 System Requirements

- **OS**: Windows 10 or Windows 11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB for application + space for your media
- **Internet**: Required for fetching movie posters (optional)

## 🚀 Installation Options

### Option 1: Installer (Recommended)
1. Run `MovieFlix_Setup_v1.0.0.exe`
2. Follow the installation wizard
3. Choose where to install
4. Choose your library location
5. Click Install and wait
6. Launch MovieFlix from Start Menu or Desktop

### Option 2: Portable Version
1. Extract `MovieFlix_Portable.zip` to any folder
2. Open the extracted folder
3. Create a `library` folder inside (if it doesn't exist)
4. Run `MovieFlix.exe`

## 📁 Setting Up Your Library

### For Movies:
```
library/
├── Inception (2010).mkv
├── The Matrix (1999).mp4
├── Interstellar (2014).mkv
└── ...
```

### For TV Series:
```
library/
└── Breaking Bad/
    ├── Breaking.Bad.S01E01.mkv
    ├── Breaking.Bad.S01E02.mkv
    ├── Breaking.Bad.S02E01.mkv
    └── ...
```

**Supported formats**: MP4, MKV, AVI, MOV, and more

## 🎯 Quick Start Guide

1. **First Launch**
   - Create an account (stored locally)
   - Login with your credentials

2. **Add Content**
   - Option A: Copy movies to the `library` folder
   - Option B: Use "Scan External Drive" to import from USB/HDD
   - Option C: Use "Scan PC" to find movies anywhere on your computer

3. **Scan Library**
   - Click user menu → "Scan Library"
   - Wait for scanning to complete
   - Posters will load automatically in background

4. **Watch**
   - Click any movie/episode poster
   - Player opens in separate window
   - Use controls: Play/Pause, Seek, Volume, Fullscreen
   - Close player anytime - progress is saved!

5. **Browse**
   - Featured Movie: Large banner at top
   - Continue Watching: Resume your shows
   - All Movies: Your entire collection
   - New & Popular: Trending from TMDB

## ⚙️ Configuration

### Settings Location
- **Installed**: `C:\Users\YourName\AppData\Local\MovieFlix\`
- **Portable**: Same folder as MovieFlix.exe

### Environment Variables (.env)
```env
API_URL=http://localhost:8000
TMDB_API_KEY=your_api_key_here
LIBRARY_PATH=C:\Users\YourName\Documents\MovieFlix Library
```

### Get TMDB API Key (Free)
1. Visit https://www.themoviedb.org/
2. Create free account
3. Go to Settings → API → Request API Key
4. Copy API key to .env file
5. Restart MovieFlix

## 🎮 Keyboard Shortcuts

### Main Window
- `Ctrl+S` - Scan Library
- `Ctrl+Q` - Quit

### Video Player
- `Space` - Play/Pause
- `F` - Fullscreen
- `→` - Skip Forward 10s
- `←` - Skip Backward 10s
- `↑` - Volume Up
- `↓` - Volume Down
- `M` - Mute
- `Esc` - Exit Fullscreen

## 🔧 Troubleshooting

### App won't start
- **Check**: Windows Defender may block it
  - Right-click → Properties → Unblock
- **Check**: Antivirus software
  - Add MovieFlix.exe to exclusions
- **Run as Administrator**: Right-click → Run as administrator

### No video playback
- **VLC Required**: If VLC folder wasn't bundled
  - Download VLC: https://www.videolan.org/
  - Install it
  - Restart MovieFlix

### Posters not loading
- **Check internet connection**
- **Add TMDB API Key** (see Configuration above)
- **Wait**: Posters load automatically every 30 seconds

### Database errors
- **Reset Database**:
  1. Close MovieFlix
  2. Delete `backend\movies.db`
  3. Start MovieFlix
  4. Scan library again

### Can't find movies
- **Check file names**: Must have proper extensions (.mp4, .mkv, etc.)
- **For series**: Use format: `Show.Name.S01E01.mkv`
- **Rescan**: User menu → Scan Library

## 📊 File Organization Tips

### Best Practices
✅ **Good**:
```
Movies/
├── Inception (2010).mkv
├── The Dark Knight (2008).mp4
└── Interstellar (2014).mkv

Series/
└── Breaking Bad/
    └── Season 1/
        ├── Breaking.Bad.S01E01.mkv
        └── Breaking.Bad.S01E02.mkv
```

❌ **Avoid**:
```
Movies/
├── movie1.mp4  (no name)
├── test.mkv  (unclear)
└── New Folder/  (too nested)
```

### Series Naming
Supported patterns:
- `Show.S01E01.mkv`
- `Show.1x01.mkv`
- `Show - 01x01.mkv`
- `Show - s01e01.mkv`

## 🆘 Support

### Common Issues
1. **Slow scanning**: Normal for large libraries (1000+ files)
2. **Missing posters**: Will load automatically, be patient
3. **External drive not detected**: Must have movies/series in root
4. **Duplicate content**: Delete and rescan

### Getting Help
- Check this README first
- Check the log files:
  - `movieflix_startup.log`
  - `backend_error.log`
- Create a GitHub issue with log files attached

## 📝 License

MovieFlix is free personal software. Not for commercial use.

## 🙏 Credits

- **TMDB**: Movie metadata and posters (https://www.themoviedb.org/)
- **VLC**: Video playback engine (https://www.videolan.org/)
- **PyQt5**: User interface framework
- **FastAPI**: Backend server

## 🔄 Updates

Check for updates at: [Your GitHub/Website]

---

**Enjoy your personal streaming library! 🍿**

For questions or issues, contact: [your-email@domain.com]
