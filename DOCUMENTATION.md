# MovieFlix - Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Backend Documentation](#backend-documentation)
3. [Frontend Documentation](#frontend-documentation)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Code Organization](#code-organization)
7. [Development Guide](#development-guide)

---

## Architecture Overview

MovieFlix follows a client-server architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│           Frontend (PyQt5)                  │
│  ┌──────────────────────────────────────┐  │
│  │  launcher.py - Loading Screen        │  │
│  │  advanced_ui.py - Main Window        │  │
│  │  embedded_player.py - VLC Player     │  │
│  │  advanced_widgets.py - UI Components │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                      │
                   HTTP/REST
                      │
┌─────────────────────────────────────────────┐
│          Backend (FastAPI)                  │
│  ┌──────────────────────────────────────┐  │
│  │  main.py - API Server                │  │
│  │  scanner.py - File System Scanner    │  │
│  │  metadata.py - TMDB Integration      │  │
│  │  auth.py - Authentication            │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                      │
                   SQLite
                      │
┌─────────────────────────────────────────────┐
│          Database (SQLite)                  │
│  - movies.db                                │
│  - Tables: movies, series, seasons,         │
│    episodes, users                          │
└─────────────────────────────────────────────┘
```

### Communication Flow

1. **Startup**: Launcher checks VLC → Backend → Loads UI
2. **Authentication**: Login → API validates → Session created
3. **Content Loading**: UI requests → API queries DB → Returns JSON
4. **Playback**: UI → VLC player → Direct file access
5. **Scanning**: UI triggers → API scans filesystem → Updates DB

---

## Backend Documentation

### Main Components

#### 1. main.py - FastAPI Application
**Purpose**: Main API server that handles all HTTP requests

**Key Functions**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI)
    """Handles app startup and shutdown"""
    # - Initializes database
    # - Creates default admin user
    # - Sets up connections
```

**Endpoints**:
- `/movies` - List all movies
- `/series` - List all TV shows
- `/library/scan` - Scan library folders
- `/library/scan_folder` - Scan custom folder
- `/auth/login` - User authentication
- `/tmdb/*` - TMDB integration endpoints

**Configuration**:
```python
API_HOST = os.getenv('API_HOST', '127.0.0.1')
API_PORT = int(os.getenv('API_PORT', 8765))
```

---

#### 2. scanner.py - File System Scanner
**Purpose**: Discovers and parses media files

**Functions**:

```python
def scan_movies(movies_dir: str) -> list
    """
    Scans directory for movie files.
    
    Process:
    1. Walks directory tree recursively
    2. Filters by video extensions
    3. Cleans title (removes year, quality tags)
    4. Returns list of {title, path} dicts
    
    Title Cleaning:
    - Removes years (1990-2099)
    - Removes quality tags (720p, BluRay, etc.)
    - Replaces dots/underscores with spaces
    """
```

```python
def scan_series(series_dir: str) -> list
    """
    Scans directory for TV series episodes.
    
    Handles Multiple Patterns:
    - S01E01, S1E1 (standard)
    - Episode 01, Episode 1
    - Numeric (001.mkv, 1.mkv)
    
    Folder Structures:
    - Series/Season 01/Episode.mkv
    - Series/S01E01.mkv (flat)
    
    Returns:
    List of dicts with series_title, season_number,
    episode_number, and path
    """
```

**Supported Formats**:
```python
VIDEO_EXTENSIONS = (
    ".mp4", ".mkv", ".avi", ".mov",
    ".flv", ".wmv", ".webm"
)
```

---

#### 3. metadata.py - TMDB Integration
**Purpose**: Fetches movie/series metadata from TMDB API

**Functions**:

```python
def fetch_movie_metadata(title: str) -> dict
    """
    Fetches metadata for a movie.
    
    Returns:
    {
        'title': str,
        'overview': str,
        'vote_average': float,
        'poster_url': str,  # Full URL
        'backdrop_url': str,
        'release_date': str
    }
    
    API: https://api.themoviedb.org/3/search/movie
    """
```

**Configuration**:
```python
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
```

**Error Handling**:
- Returns None if movie not found
- Logs errors without crashing
- Validates API key on startup

---

#### 4. auth.py - Authentication System
**Purpose**: User authentication and session management

**Security Features**:
- SHA256 password hashing
- HTTP Basic Auth
- Session-based authentication
- Admin role support

**Functions**:

```python
def hash_password(password: str) -> str
    """
    Hashes password using SHA256.
    
    Note: In production, use bcrypt or argon2
    """
```

```python
def verify_credentials(username: str, password: str, db: Session) -> User
    """
    Verifies username and password.
    
    Returns:
    User object if valid, None if invalid
    """
```

**Database Model**:
```python
class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)  # SHA256 hashed
    is_admin = Column(Integer, default=0)
```

---

#### 5. models.py - Database Models
**Purpose**: SQLAlchemy ORM models for database

**Models**:

```python
class Movie(Base):
    """
    Movie model with metadata.
    
    Relationships: None
    Indexes: id (primary), path (unique)
    """
    id = Column(Integer, primary_key=True)
    title = Column(String)
    path = Column(String, unique=True)
    overview = Column(Text)
    rating = Column(Float)
    poster = Column(String)  # Full URL
    watched = Column(Boolean, default=False)
    last_position = Column(Integer, default=0)


class Series(Base):
    """
    TV Series model.
    
    Relationships: Has many Season
    """
    id = Column(Integer, primary_key=True)
    title = Column(String)
    overview = Column(Text)
    poster = Column(String)


class Season(Base):
    """
    Season model.
    
    Relationships: 
    - Belongs to Series
    - Has many Episode
    """
    id = Column(Integer, primary_key=True)
    series_id = Column(Integer, ForeignKey('series.id'))
    season_number = Column(Integer)


class Episode(Base):
    """
    Episode model.
    
    Relationships: Belongs to Season
    """
    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey('seasons.id'))
    episode_number = Column(Integer)
    path = Column(String, unique=True)
    title = Column(String)
```

**Important Note**: 
```python
# SQLAlchemy version MUST be 1.4.48
# Version 2.0+ breaks due to Mapped[] types
sqlalchemy==1.4.48
```

---

## Frontend Documentation

### Main Components

#### 1. launcher.py - Application Launcher
**Purpose**: Loading screen with system checks

**Classes**:

```python
class StartupThread(QThread):
    """
    Performs startup checks in background.
    
    Checks:
    1. VLC availability (python-vlc)
    2. Backend connection (API server)
    3. UI component loading
    
    Signals:
    - progress(int, str): Progress percentage and message
    - finished(): All checks passed
    - error(str): Check failed with error message
    """
```

```python
class LoadingScreen(QWidget):
    """
    Modern splash screen with progress bar.
    
    Features:
    - Gradient background
    - Animated progress bar
    - Status messages
    - Error handling
    """
```

**Flow**:
```
Launch → Show LoadingScreen → StartupThread checks
→ Success: Launch main app
→ Error: Show message and exit
```

---

#### 2. advanced_ui.py - Main Application Window
**Purpose**: Main application interface

**Classes**:

```python
class AdvancedMovieLibrary(QMainWindow):
    """
    Main application window.
    
    Architecture:
    - NavigationBar: Top navigation
    - QStackedWidget: View container
        ├── Home View (scroll area)
        ├── Movies View (scroll area)
        ├── Series View (scroll area)
        └── Player View (embedded VLC)
    
    State:
    - scanner: BackgroundScanner instance
    - video_player: EmbeddedVideoPlayer instance
    - nav_bar: NavigationBar instance
    """
```

**Key Methods**:

```python
def switch_view(self, view_name: str):
    """
    Switches between different views.
    
    Args:
        view_name: 'home', 'movies', 'series', 
                   'new_popular', 'watchlist'
    
    Process:
    1. Update navigation button states
    2. Switch QStackedWidget widget
    3. Load content if needed
    """
```

```python
def load_movies_view(self):
    """
    Loads movies view with progressive loading.
    
    Uses QTimer to prevent UI freezing:
    1. Clear existing widgets (QTimer 10ms)
    2. Load new data (QTimer 100ms)
    3. Add to layout progressively
    """
```

```python
def play_movie(self, movie: dict):
    """
    Plays a movie using embedded VLC player.
    
    Args:
        movie: Dict with 'id', 'title', 'path'
    
    Process:
    1. Validate file path
    2. Switch to player view
    3. Initialize VLC playback
    4. Mark as watched via API
    """
```

---

#### 3. embedded_player.py - VLC Player Widget
**Purpose**: Embedded VLC video player

**Class**:

```python
class EmbeddedVideoPlayer(QWidget):
    """
    Netflix-style embedded video player.
    
    Components:
    - video_frame: Widget for video output
    - controls: Play/pause, seek, volume, fullscreen
    - position_slider: Seek bar
    - volume_slider: Volume control
    
    VLC Configuration:
    - Hardware decoding enabled
    - Direct3D11 output (Windows)
    - SOXR audio resampler
    - No title show
    """
```

**Key Features**:

```python
def play_media(self, path: str, media_id: int, media_type: str):
    """
    Starts playback.
    
    Args:
        path: File path
        media_id: Database ID
        media_type: 'movie' or 'episode'
    
    VLC Setup:
    1. Stop existing playback
    2. Create media from path
    3. Set video output (hwnd/xwindow)
    4. Start playback
    5. Resume from last position if available
    """
```

**Keyboard Shortcuts**:
```python
def keyPressEvent(self, event):
    """
    Qt event handler for keyboard input.
    
    Shortcuts:
    - Space: Play/Pause
    - F/F11: Fullscreen
    - ESC: Exit player
    - Up/Down: Volume ±5
    - Left/Right: Seek ±10s
    """
```

**Volume Control**:
```python
def eventFilter(self, obj, event):
    """
    Mouse wheel for volume control.
    
    Wheel up: +5 volume
    Wheel down: -5 volume
    Range: 0-100
    """
```

---

#### 4. advanced_widgets.py - UI Components
**Purpose**: Reusable UI components

**Classes**:

```python
class AdvancedMovieCard(QFrame):
    """
    Netflix-style content card.
    
    Features:
    - Poster image loading (network or cache)
    - Hover overlay with buttons
    - Play and Info actions
    - Smooth animations
    
    Signals:
    - play_clicked: Emits movie dict
    - info_clicked: Emits movie dict
    
    Hover Effect:
    enterEvent: Shows overlay, subtle border glow
    leaveEvent: Hides overlay, resets style
    """
```

```python
class CategoryRow(QWidget):
    """
    Horizontal scrolling row of content cards.
    
    Features:
    - Horizontal scroll area
    - Title label
    - "View All" button (optional)
    - Smooth scrolling
    
    Methods:
    - add_card(card): Adds card to row
    - clear(): Removes all cards
    """
```

**Poster Loading**:
```python
def _load_poster(self):
    """
    Loads poster image from URL or cache.
    
    Process:
    1. Check if URL or path
    2. Try cache first
    3. Download if needed
    4. Scale to 200x300
    5. Apply rounded corners
    
    Handles:
    - Network errors
    - Missing images
    - Cache management
    """
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│     Movie       │
├─────────────────┤
│ id (PK)         │
│ title           │
│ path (UNIQUE)   │
│ overview        │
│ rating          │
│ poster          │
│ watched         │
│ last_position   │
└─────────────────┘

┌─────────────────┐         ┌─────────────────┐
│     Series      │         │     Season      │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │◄────┬───│ id (PK)         │
│ title           │     │   │ series_id (FK)  │
│ overview        │     │   │ season_number   │
│ poster          │     │   └─────────────────┘
└─────────────────┘     │            │
                        │            │
                        │   ┌────────┴────────┐
                        │   │    Episode      │
                        │   ├─────────────────┤
                        │   │ id (PK)         │
                        │   │ season_id (FK)  │
                        │   │ episode_number  │
                        │   │ path (UNIQUE)   │
                        │   │ title           │
                        └───┴─────────────────┘

┌─────────────────┐
│      User       │
├─────────────────┤
│ id (PK)         │
│ username(UNIQUE)│
│ password_hash   │
│ is_admin        │
└─────────────────┘
```

### SQL Schema

```sql
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR,
    path VARCHAR UNIQUE,
    overview TEXT,
    rating FLOAT,
    poster VARCHAR,
    watched BOOLEAN DEFAULT 0,
    last_position INTEGER DEFAULT 0
);

CREATE TABLE series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR,
    overview TEXT,
    poster VARCHAR
);

CREATE TABLE seasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER,
    season_number INTEGER,
    FOREIGN KEY (series_id) REFERENCES series(id)
);

CREATE TABLE episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id INTEGER,
    episode_number INTEGER,
    path VARCHAR UNIQUE,
    title VARCHAR,
    FOREIGN KEY (season_id) REFERENCES seasons(id)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR UNIQUE,
    password_hash VARCHAR,
    is_admin INTEGER DEFAULT 0
);
```

---

## API Endpoints

### Complete API Reference

#### Movies

```http
GET /movies
Returns all movies

Response: 200 OK
[
    {
        "id": 1,
        "title": "Inception",
        "path": "/path/to/inception.mkv",
        "overview": "A thief who steals...",
        "rating": 8.8,
        "poster": "https://image.tmdb.org/t/p/w500/...",
        "watched": false,
        "last_position": 0
    }
]
```

```http
POST /movies/{movie_id}/watch
Marks movie as watched

Response: 200 OK
{"status": "watched"}
```

#### Series

```http
GET /series
Returns all TV series

Response: 200 OK
[
    {
        "id": 1,
        "title": "Breaking Bad",
        "overview": "A high school chemistry...",
        "poster": "https://..."
    }
]
```

```http
GET /series/{series_id}/episodes
Returns all episodes for a series

Response: 200 OK
[
    {
        "id": 1,
        "season_number": 1,
        "episode_number": 1,
        "title": "Episode 1",
        "path": "/path/to/episode.mkv"
    }
]
```

#### Library Management

```http
POST /library/scan
Scans default library folders

Response: 200 OK
{
    "movies_added": 10,
    "series_added": 5,
    "episodes_added": 50,
    "errors": []
}
```

```http
POST /library/scan_folder
Scans custom folder

Request Body:
{
    "path": "/custom/path",
    "type": "movies"  // or "series"
}

Response: 200 OK
{
    "added": 10,
    "errors": []
}
```

#### TMDB Integration

```http
GET /tmdb/trending
Returns trending movies from TMDB (not in library)

Response: 200 OK
[
    {
        "title": "Movie Title",
        "overview": "Description",
        "rating": 8.5,
        "release_date": "2024-01-01",
        "poster": "https://..."
    }
]
```

```http
GET /tmdb/new-releases
Returns new releases (last 3 months, not in library)
```

#### Authentication

```http
POST /auth/login
User authentication

Headers:
Authorization: Basic base64(username:password)

Response: 200 OK
{
    "message": "Login successful",
    "user": "admin",
    "is_admin": true
}
```

---

## Code Organization

### Naming Conventions

**Files**: `snake_case.py`
**Classes**: `PascalCase`
**Functions**: `snake_case()`
**Constants**: `UPPER_SNAKE_CASE`
**Variables**: `snake_case`

### Import Order

```python
# 1. Standard library
import os
import sys

# 2. Third-party packages
from PyQt5.QtWidgets import QWidget
import requests

# 3. Local imports
from app.widgets import MovieCard
from backend.models import Movie
```

### Documentation Standards

**Module Docstrings**:
```python
"""
Module Name - Brief Description
================================

Detailed description of module purpose and functionality.

Classes:
    ClassName: Brief description

Functions:
    function_name: Brief description

Example:
    >>> from module import function
    >>> function()
"""
```

**Function Docstrings**:
```python
def function_name(arg1: type, arg2: type) -> return_type:
    """
    Brief description.
    
    Detailed description of what the function does.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception is raised
        
    Example:
        >>> function_name(value1, value2)
        result
    """
```

---

## Development Guide

### Setting Up Development Environment

```bash
# 1. Clone repository
git clone <repository-url>
cd movie_library

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install pytest black pylint mypy

# 5. Configure environment
cp .env.example .env
# Edit .env with your settings

# 6. Initialize database
python backend/database.py

# 7. Run backend
python backend/main.py

# 8. Run frontend
python app/launcher.py
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_scanner.py

# Run with coverage
pytest --cov=backend --cov=app

# Run type checking
mypy backend/ app/
```

### Code Style

```bash
# Format code
black backend/ app/

# Lint code
pylint backend/ app/

# Check imports
isort backend/ app/
```

### Adding New Features

1. **Create Feature Branch**
```bash
git checkout -b feature/feature-name
```

2. **Write Tests First** (TDD)
```python
# tests/test_new_feature.py
def test_new_feature():
    assert new_feature() == expected_result
```

3. **Implement Feature**
```python
# backend/new_feature.py
def new_feature():
    """
    Docstring with description
    """
    # Implementation
```

4. **Document Feature**
- Add docstrings
- Update README.md
- Update DOCUMENTATION.md

5. **Test and Commit**
```bash
pytest
black .
git add .
git commit -m "Add: Feature description"
git push origin feature/feature-name
```

### Debugging

**Backend Debugging**:
```python
# main.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use debugger
import pdb; pdb.set_trace()
```

**Frontend Debugging**:
```python
# advanced_ui.py
import sys
print(f"DEBUG: {variable}", file=sys.stderr)

# Or use Qt debugger
from PyQt5.QtCore import pyqtRemoveInputHook
import pdb; pyqtRemoveInputHook(); pdb.set_trace()
```

**Common Issues**:

1. **Import Errors**: Check `sys.path` and `PYTHONPATH`
2. **Database Locked**: Close all connections, delete `.db-journal`
3. **VLC Not Found**: Verify `python-vlc` installation
4. **Port Already In Use**: Change `API_PORT` in `.env`

---

## Performance Optimization

### Backend

1. **Database Indexing**
```python
# Add indexes for frequently queried fields
Index('idx_movie_title', Movie.title)
Index('idx_series_title', Series.title)
```

2. **Query Optimization**
```python
# Use joins instead of multiple queries
db.query(Episode).join(Season).join(Series).filter(...)

# Limit results
db.query(Movie).limit(100).all()

# Use pagination
db.query(Movie).offset(page * per_page).limit(per_page).all()
```

3. **Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_movie_metadata(title):
    # Expensive operation
    return fetch_from_tmdb(title)
```

### Frontend

1. **Progressive Loading**
```python
# Use QTimer for non-blocking loads
QTimer.singleShot(10, clear_function)
QTimer.singleShot(100, load_function)
```

2. **Image Caching**
```python
# Cache poster images
cache_dir = os.path.join(tempfile.gettempdir(), 'movieflix_cache')
```

3. **Thread for Heavy Operations**
```python
class HeavyOperationThread(QThread):
    def run(self):
        # Heavy operation in background
        pass
```

---

## Security Considerations

### Current Implementation

1. **Password Hashing**: SHA256 (⚠️ Not production-ready)
2. **API Authentication**: HTTP Basic Auth
3. **Session Management**: In-memory (lost on restart)

### Production Recommendations

1. **Use bcrypt or argon2 for passwords**
```python
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

2. **Implement JWT tokens**
```python
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

3. **Use HTTPS in production**
```python
# Use reverse proxy (nginx) with SSL certificate
# Or use uvicorn with SSL
uvicorn.run(app, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
```

4. **Environment Variables Security**
```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use secrets management in production
# AWS Secrets Manager, Azure Key Vault, etc.
```

5. **Input Validation**
```python
from pydantic import BaseModel, validator

class ScanRequest(BaseModel):
    path: str
    type: str
    
    @validator('path')
    def validate_path(cls, v):
        if not os.path.exists(v):
            raise ValueError('Path does not exist')
        return v
```

---

## Troubleshooting Guide

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Import Error | Wrong Python path | Check `sys.path`, activate venv |
| Database Locked | Multiple connections | Close all, delete journal file |
| VLC Init Error | VLC not installed | Install python-vlc: `pip install python-vlc` |
| Port In Use | Another app using port | Change API_PORT in .env |
| No Posters | No TMDB API key | Add key to .env |
| UI Freezing | Blocking operations | Use QTimer or QThread |
| Series Not Found | Wrong folder structure | Check scanner.py patterns |

---

**End of Documentation**

For questions or contributions, please refer to the README.md file.
