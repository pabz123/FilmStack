# MovieFlix - Production Ready! 🎬

## 🎉 What's New - Major Update!

### Desktop App with Loading Screen
- **Launch with `MovieFlix.bat`** - Professional startup experience
- Loading screen checks VLC, backend connection, and components
- Smooth transitions - no more black screens!

### User Features
- **User Menu** (click avatar icon top-right):
  - ➕ Add folders from anywhere on your PC
  - 🔄 Rescan library
  - 🚪 Sign out

### Content Organization
- **Movies Section**: Shows YOUR library movies
- **New & Popular**: Shows TMDB trending movies NOT in your library yet
- **My List**: Statistics dashboard + all your content

### UI Improvements
- ✨ Subtle glow hover effects (no more ugly red borders)
- 🎬 Embedded VLC player (plays inside the app window)
- 🎨 Professional gradients everywhere
- ⌨️ Keyboard shortcuts in player (Space, F11, Arrow keys)

---

## 🚀 Quick Start

### 1. Create Desktop Shortcut
```powershell
powershell -ExecutionPolicy Bypass -File create_desktop_shortcut.ps1
```

### 2. Start Backend (First Terminal)
```bash
start_backend.bat
```

### 3. Launch MovieFlix
- **Desktop**: Double-click MovieFlix icon
- **Manual**: Run `MovieFlix.bat`

---

## 📖 How to Use

### First Time Setup
1. Backend starts on http://127.0.0.1:8765
2. Loading screen checks everything
3. Login with: **admin / admin123**
4. App automatically scans `/library/mo/` and `/library/se/`

### Adding Content

#### Method 1: Add to Default Folders
- Movies → `D:\movie_library\library\mo\`
- Series → `D:\movie_library\library\se\`
- Click user menu → Rescan

#### Method 2: Add Any Folder
1. Click avatar icon (top-right)
2. Select "➕ Add Folder to Library"
3. Choose Movies or TV Shows
4. Browse to folder
5. Wait for scan to complete

### Navigation
- **Home**: Featured content, continue watching, recommendations
- **Movies**: All YOUR movies organized by rating
- **TV Shows**: All YOUR series with episode selection
- **New & Popular**: TMDB trending movies you don't have yet
- **My List**: Statistics + browse all content

### Playing Content
- Click any movie/show card
- **Embedded player opens inside app**
- **Controls**:
  - **Space**: Play/Pause
  - **F or F11**: Fullscreen
  - **Arrow Up/Down**: Volume
  - **Arrow Left/Right**: Seek ±10s
  - **ESC**: Exit player
  - **X button**: Close player

### Series Playback
1. Click series card
2. Select season and episode
3. Player opens with episode

---

## 🎨 Features Explained

### Loading Screen
- Checks VLC installation
- Verifies backend connection
- Loads UI components
- Shows errors clearly if something's wrong

### User Menu
**Avatar Icon (Top-Right)**
- **Add Folder**: Import movies/series from anywhere
- **Rescan**: Refresh library after manual file changes
- **Sign Out**: Return to login screen

### Hover Effects
- Cards glow subtly on hover
- No position changes (fixed!)
- Info overlay appears

### Error Handling
- Clear error messages
- Connection issues detected on startup
- File not found warnings
- VLC missing guidance

---

## 🐛 Troubleshooting

### "Media player not available"
```bash
pip install python-vlc
```

### "Cannot connect to backend"
- Check `start_backend.bat` is running
- Backend should show: "Uvicorn running on http://127.0.0.1:8765"

### Movies don't show in Movies section
- Check terminal for DEBUG messages
- Verify files are in `/library/mo/`
- Try: User Menu → Rescan Library

### Series show error when playing
- Check file paths in terminal
- Verify episode files exist
- Folder structure: `Series Name/Season 01/Episode.mkv`

### Login keyboard not working
- Click "Skip Login" button
- Will be fixed in next update

### Posters missing
- Check `.env` has valid TMDB_API_KEY
- Delete `movies.db` and rescan
- Posters download during scan

---

## 📁 Project Structure

```
D:\movie_library\
├── MovieFlix.bat              ← Launch app
├── create_desktop_shortcut.ps1 ← Create desktop icon
├── app/
│   ├── launcher.py             ← Loading screen
│   ├── advanced_ui.py          ← Main app
│   ├── advanced_widgets.py     ← UI components
│   ├── embedded_player.py      ← VLC player
│   ├── login_dialog.py         ← Authentication
│   └── ...
├── backend/
│   ├── main.py                 ← FastAPI server
│   ├── scan_endpoint.py        ← Scanning + add folders
│   └── ...
├── library/
│   ├── mo/                     ← Movies go here
│   └── se/                     ← Series go here
└── .env                        ← Configuration
```

---

## ⚙️ Configuration

**`.env` File**
```env
TMDB_API_KEY=6c2d8d780ce73c06e3955159c3caf0fe
MOVIE_LIBRARY_PATH=D:/movie_library/library/mo
SERIES_LIBRARY_PATH=D:/movie_library/library/se
API_HOST=127.0.0.1
API_PORT=8765
API_URL=http://127.0.0.1:8765
```

---

## 🔐 Security Notes

**Default Credentials**: admin / admin123

⚠️ **Change these in production!**

To add users:
```python
# In backend, add to auth.py or use API
```

---

## 🎯 Next Steps

### Recommended Actions:
1. ✅ Create desktop shortcut
2. ✅ Test launcher loading screen
3. ✅ Try adding a folder from elsewhere on PC
4. ✅ Test movie playback in embedded player
5. ✅ Test series episode selection
6. ✅ Check New & Popular for TMDB movies
7. ✅ Verify Movies section shows your library

### Future Enhancements (if needed):
- Auto-download from streaming sites
- Notifications for new releases
- Custom user profiles
- Watch history sync
- Mobile app companion

---

## 📞 Support

If you encounter issues:

1. Check backend terminal for errors
2. Check frontend terminal for DEBUG messages
3. Verify file paths exist
4. Try rescanning library
5. Delete `movies.db` for fresh start

---

**Enjoy your personal Netflix! 🍿**
