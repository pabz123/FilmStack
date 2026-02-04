"""
MovieFlix Main User Interface
=============================

This module implements the main application window with a Netflix-style interface.
It provides a complete streaming experience with content browsing, playback,
and user management.

Architecture:
    - Main Window (AdvancedMovieLibrary)
        ├── Navigation Bar (user menu, search, navigation)
        ├── Hero Banner (featured content)
        ├── Content Views
        │   ├── Home (featured, recommendations, continue watching)
        │   ├── Movies (library movies organized by rating)
        │   ├── TV Shows (series with episode selection)
        │   ├── New & Popular (TMDB trending not in library)
        │   └── My List (statistics and all content)
        └── Embedded Player (VLC integration)

Key Features:
    - Automatic background library scanning
    - Real-time content loading with progress indicators
    - Embedded VLC video playback
    - User authentication and session management
    - TMDB integration for trending content
    - Custom folder import
    - Sign-out functionality

UI Components:
    - HeroBanner: Large featured content display
    - NavigationBar: Top navigation with user menu
    - CategoryRow: Horizontal scrolling content rows
    - AdvancedMovieCard: Individual content cards with hover effects

State Management:
    - Uses QStackedWidget for view switching
    - QTimer for progressive loading (prevents UI freezing)
    - BackgroundScanner thread for non-blocking scans

Keyboard Shortcuts:
    Player: Space (play/pause), F11 (fullscreen), ESC (exit),
            Arrow keys (seek/volume), Mouse wheel (volume)

Dependencies:
    - PyQt5: UI framework
    - requests: API communication
    - VLC: Media playback

Author: MovieFlix Team
License: MIT
"""

import sys
import os
import subprocess
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QPushButton, QLabel, QFrame, QMessageBox,
    QStackedWidget, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QPixmap, QFont, QIcon

# Import embedded player
try:
    from app.embedded_player import EmbeddedVideoPlayer
    PLAYER_AVAILABLE = True
except:
    try:
        from embedded_player import EmbeddedVideoPlayer
        PLAYER_AVAILABLE = True
    except:
        PLAYER_AVAILABLE = False
        print("Warning: Embedded player not available")

# Import UI components
try:
    from app.advanced_widgets import AdvancedMovieCard, CategoryRow
    from app.info_dialog import MovieInfoDialog
    from app.series_dialog import SeriesEpisodeDialog
    from app.login_dialog import LoginDialog
except:
    from advanced_widgets import AdvancedMovieCard, CategoryRow
    from info_dialog import MovieInfoDialog
    from series_dialog import SeriesEpisodeDialog
    from login_dialog import LoginDialog

# Get API URL from environment or use default
API_URL = os.getenv("API_URL", "http://127.0.0.1:8765")

# Global auth credentials
AUTH_CREDENTIALS = None


class BackgroundScanner(QThread):
    """
    Background thread for scanning library without freezing the UI.
    
    This thread performs the library scan operation in the background,
    allowing the main UI to remain responsive. It reports progress
    and results back to the main thread through Qt signals.
    
    Signals:
        scan_complete: Emitted with scan results dict when complete
        scan_error: Emitted with error message string if scan fails
        
    Example:
        scanner = BackgroundScanner()
        scanner.scan_complete.connect(on_complete_handler)
        scanner.scan_error.connect(on_error_handler)
        scanner.start()
    """
    scan_complete = pyqtSignal(dict)
    scan_error = pyqtSignal(str)
    
    def run(self):
        """Run scan in background"""
        try:
            print("Background scan starting...")
            response = requests.post(f"{API_URL}/library/scan", timeout=180)
            
            if response.status_code == 200:
                results = response.json()
                print(f"Background scan complete: {results}")
                self.scan_complete.emit(results)
            else:
                self.scan_error.emit(f"Scan failed with status: {response.status_code}")
        except Exception as e:
            print(f"Background scan error: {e}")
            import traceback
            traceback.print_exc()
            self.scan_error.emit(str(e))


class HeroBanner(QWidget):
    """Large hero banner with backdrop and details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(600)
        self.featured_movie = None
        
        # Background gradient
        self.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(20, 20, 20, 0.3),
                stop:0.7 rgba(20, 20, 20, 0.8),
                stop:1 rgba(20, 20, 20, 1));
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 0, 60, 80)
        layout.addStretch()
        
        # Badge (Featured/New/Trending)
        self.badge = QLabel("FEATURED")
        self.badge.setStyleSheet("""
            background-color: rgba(229, 9, 20, 0.9);
            color: white;
            padding: 8px 20px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        self.badge.setFixedWidth(140)
        layout.addWidget(self.badge)
        layout.addSpacing(15)
        
        # Title
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""
            color: white;
            font-size: 56px;
            font-weight: bold;
        """)
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumWidth(900)
        layout.addWidget(self.title_label)
        layout.addSpacing(15)
        
        # Meta info (rating, year, etc.)
        self.meta_label = QLabel()
        self.meta_label.setStyleSheet("""
            color: #46d369;
            font-size: 16px;
            font-weight: bold;
        """)
        layout.addWidget(self.meta_label)
        layout.addSpacing(10)
        
        # Description
        self.desc_label = QLabel()
        self.desc_label.setStyleSheet("""
            color: #e5e5e5;
            font-size: 18px;
        """)
        self.desc_label.setWordWrap(True)
        self.desc_label.setMaximumWidth(800)
        self.desc_label.setMaximumHeight(60)
        layout.addWidget(self.desc_label)
        layout.addSpacing(25)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.play_btn = QPushButton("▶  Play Now")
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: none;
                border-radius: 6px;
                padding: 15px 40px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.85);
            }
        """)
        self.play_btn.setCursor(Qt.PointingHandCursor)
        self.play_btn.setFixedHeight(55)
        
        self.info_btn = QPushButton("ℹ  More Info")
        self.info_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(109, 109, 110, 0.7);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.5);
                border-radius: 6px;
                padding: 15px 35px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(109, 109, 110, 0.9);
                border-color: white;
            }
        """)
        self.info_btn.setCursor(Qt.PointingHandCursor)
        self.info_btn.setFixedHeight(55)
        
        button_layout.addWidget(self.play_btn)
        button_layout.addWidget(self.info_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def set_featured(self, movie):
        """Set the featured movie"""
        self.featured_movie = movie
        self.title_label.setText(movie.get('title', 'Unknown'))
        
        # Meta info
        meta_parts = []
        if movie.get('rating'):
            meta_parts.append(f"⭐ {movie['rating']:.1f}/10")
        if movie.get('watched'):
            meta_parts.append("✓ Watched")
        self.meta_label.setText(" • ".join(meta_parts) if meta_parts else "")
        
        # Description
        desc = movie.get('overview', '')
        if desc and isinstance(desc, str):
            if len(desc) > 200:
                desc = desc[:197] + "..."
        else:
            desc = "No description available"
        self.desc_label.setText(desc)


class NavigationBar(QFrame):
    """Top navigation bar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(20, 20, 20, 0.98),
                    stop:1 rgba(20, 20, 20, 0.85));
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 0, 40, 0)
        layout.setSpacing(40)
        
        # Logo - proper spacing and sizing
        logo = QLabel("MOVIE FLIX")
        logo.setStyleSheet("""
            color: #e50914;
            font-size: 26px;
            font-weight: bold;
            font-family: Arial, sans-serif;
        """)
        logo.setMinimumWidth(150)
        layout.addWidget(logo)
        
        # Navigation buttons
        self.nav_buttons = {}
        for text in ["Home", "Movies", "TV Shows", "New & Popular", "My List"]:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #e5e5e5;
                    border: none;
                    padding: 10px 20px;
                    font-size: 15px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    color: white;
                }
                QPushButton:checked {
                    color: white;
                    font-weight: bold;
                }
            """)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            self.nav_buttons[text] = btn
            layout.addWidget(btn)
        
        # Set Home as default
        self.nav_buttons["Home"].setChecked(True)
        
        layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search movies, shows...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 0.5);
                color: white;
                border: 2px solid transparent;
                border-radius: 4px;
                padding: 10px 15px;
                font-size: 14px;
                min-width: 250px;
            }
            QLineEdit:focus {
                border-color: white;
                background-color: rgba(0, 0, 0, 0.7);
            }
        """)
        layout.addWidget(self.search_box)
        
        # Settings button
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(lambda: self.parent_window.show_settings() if hasattr(self.parent_window, 'show_settings') else None)
        layout.addWidget(self.settings_btn)
        
        # Store parent reference for menu
        self.parent_window = parent
        
        # User menu button
        self.user_btn = QPushButton("👤")
        self.user_btn.setFixedSize(40, 40)
        self.user_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(229, 9, 20, 0.8);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #e50914;
            }
        """)
        self.user_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.user_btn)


class AdvancedMovieLibrary(QMainWindow):
    """Advanced Netflix-style movie library with all features"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MovieFlix - Your Personal Streaming Library")
        
        # Set window icon - try multiple locations
        from PyQt5.QtWidgets import QApplication
        from pathlib import Path
        
        icon_set = False
        
        # Try to get icon from app instance first
        if hasattr(QApplication.instance(), 'icon_path') and QApplication.instance().icon_path:
            icon = QIcon(QApplication.instance().icon_path)
            if not icon.isNull():
                self.setWindowIcon(icon)
                icon_set = True
        
        # If not set, try common locations
        if not icon_set:
            possible_paths = [
                Path(__file__).parent.parent / "MovieFlix.ico",  # D:\movie_library\MovieFlix.ico
                Path(__file__).parent / "assets" / "app_icon.ico",  # app/assets/app_icon.ico
                Path(sys._MEIPASS) / "MovieFlix.ico" if getattr(sys, 'frozen', False) else None,  # PyInstaller
            ]
            
            for icon_path in possible_paths:
                if icon_path and icon_path.exists():
                    icon = QIcon(str(icon_path))
                    if not icon.isNull():
                        self.setWindowIcon(icon)
                        print(f"✓ Window icon loaded from: {icon_path}")
                        icon_set = True
                        break
        
        if not icon_set:
            print("⚠ Could not load window icon")
        
        # Apply dark theme IMMEDIATELY to prevent white flash
        self.setStyleSheet("QMainWindow { background-color: #141414; }")
        
        # Set reasonable window size and maximize
        self.setMinimumSize(1024, 768)
        self.resize(1280, 720)
        self.showMaximized()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Navigation bar
        self.nav_bar = NavigationBar(self)
        self.nav_bar.nav_buttons["Home"].clicked.connect(lambda: self.switch_view("home"))
        self.nav_bar.nav_buttons["Movies"].clicked.connect(lambda: self.switch_view("movies"))
        self.nav_bar.nav_buttons["TV Shows"].clicked.connect(lambda: self.switch_view("series"))
        self.nav_bar.nav_buttons["New & Popular"].clicked.connect(lambda: self.switch_view("new_popular"))
        self.nav_bar.nav_buttons["My List"].clicked.connect(lambda: self.switch_view("watchlist"))
        self.nav_bar.user_btn.clicked.connect(self.show_user_menu)
        main_layout.addWidget(self.nav_bar)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create views
        self.home_view = self._create_home_view()
        self.movies_view = self._create_movies_view()
        self.series_view = self._create_series_view()
        
        self.stacked_widget.addWidget(self.home_view)
        self.stacked_widget.addWidget(self.movies_view)
        self.stacked_widget.addWidget(self.series_view)
        
        # Standalone player window (VLC-style)
        self.player_window = None
        
        # Track previous view for returning after video playback
        self.previous_view = "home"
        self.previous_scroll_position = 0
        
        # Track current filter for immediate card removal
        self.current_filter = "all"  # "all", "movies", or "series"
        
        # Background scanner
        self.scanner = None
        
        # TMDB metadata fetcher
        self.tmdb_fetcher = None
        
        # Auto-scanner for background PC scanning
        from app.auto_scanner import AutoScanManager
        self.auto_scanner = AutoScanManager(self)
        
        # External drive monitor for temporary cards
        from app.external_drive_monitor import ExternalContentManager
        self.external_manager = ExternalContentManager(self)
        
        # Show window immediately (don't wait for content)
        print("✓ Main window created")
        
        # Start auto-load content AFTER window is shown (defer to avoid blocking window display)
        # This ensures the window appears instantly, then content loads in background
        QTimer.singleShot(500, self.auto_load_content)
        
        # Ask user if they want to scan PC on startup
        QTimer.singleShot(2000, self.auto_scanner.start_background_scan)
        
        # Start external drive monitoring
        QTimer.singleShot(3000, self.external_manager.start_monitoring)
        
        # Periodic cleanup of disconnected drives (every 10 seconds)
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.cleanup_external_drives)
        self.cleanup_timer.start(10000)  # 10 seconds
    
    def _create_home_view(self):
        """Create home view with hero and categories"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #141414; }
            QScrollBar:vertical { width: 12px; background-color: #1a1a1a; }
            QScrollBar::handle:vertical { background-color: #555; border-radius: 6px; }
            QScrollBar::handle:vertical:hover { background-color: #e50914; }
        """)
        
        content = QWidget()
        self.home_layout = QVBoxLayout(content)
        self.home_layout.setContentsMargins(0, 0, 0, 30)
        self.home_layout.setSpacing(0)
        
        # Hero banner
        self.hero = HeroBanner()
        self.home_layout.addWidget(self.hero)
        
        # Categories
        self.continue_watching_row = None
        self.trending_row = None
        self.recommended_row = None
        self.all_movies_row = None
        
        self.home_layout.addStretch()
        
        scroll.setWidget(content)
        return scroll
    
    def _create_movies_view(self):
        """Create movies-only view"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #141414; }
            QScrollBar:vertical { width: 12px; background-color: #1a1a1a; }
            QScrollBar::handle:vertical { background-color: #555; border-radius: 6px; }
        """)
        
        content = QWidget()
        self.movies_layout = QVBoxLayout(content)
        self.movies_layout.setContentsMargins(0, 40, 0, 30)
        self.movies_layout.setSpacing(0)
        
        # Title
        title = QLabel("Movies")
        title.setStyleSheet("""
            color: white;
            font-size: 36px;
            font-weight: bold;
            padding: 0 40px;
            margin-bottom: 20px;
        """)
        self.movies_layout.addWidget(title)
        
        self.movies_layout.addStretch()
        
        scroll.setWidget(content)
        return scroll
    
    def _create_series_view(self):
        """Create TV shows-only view"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #141414; }
            QScrollBar:vertical { width: 12px; background-color: #1a1a1a; }
            QScrollBar::handle:vertical { background-color: #555; border-radius: 6px; }
        """)
        
        content = QWidget()
        self.series_layout = QVBoxLayout(content)
        self.series_layout.setContentsMargins(0, 40, 0, 30)
        self.series_layout.setSpacing(0)
        
        # Title
        title = QLabel("TV Shows")
        title.setStyleSheet("""
            color: white;
            font-size: 36px;
            font-weight: bold;
            padding: 0 40px;
            margin-bottom: 20px;
        """)
        self.series_layout.addWidget(title)
        
        self.series_layout.addStretch()
        
        scroll.setWidget(content)
        return scroll
    
    def switch_view(self, view_name):
        """Switch between different views"""
        # Update nav button states
        for name, btn in self.nav_bar.nav_buttons.items():
            btn.setChecked(False)
        
        if view_name == "home":
            self.current_filter = "all"
            self.stacked_widget.setCurrentWidget(self.home_view)
            self.nav_bar.nav_buttons["Home"].setChecked(True)
        elif view_name == "movies":
            self.current_filter = "movies"
            self.stacked_widget.setCurrentWidget(self.movies_view)
            self.nav_bar.nav_buttons["Movies"].setChecked(True)
            self.load_movies_view()
        elif view_name == "series":
            self.current_filter = "series"
            self.stacked_widget.setCurrentWidget(self.series_view)
            self.nav_bar.nav_buttons["TV Shows"].setChecked(True)
            self.load_series_view()
        elif view_name == "new_popular":
            self.current_filter = "all"
            # Show New & Popular (last 3 months)
            self.stacked_widget.setCurrentWidget(self.movies_view)
            self.nav_bar.nav_buttons["New & Popular"].setChecked(True)
            self.load_new_popular()
        elif view_name == "watchlist":
            # Show My List (all content)
            self.stacked_widget.setCurrentWidget(self.home_view)
            self.nav_bar.nav_buttons["My List"].setChecked(True)
            self.load_my_list()
    
    def auto_load_content(self):
        """Auto-load content on startup - scan if empty, fetch metadata"""
        print("========================================")
        print("auto_load_content() START")
        print("========================================")
        
        # Show loading indicator
        loading_label = QLabel("Loading your library...")
        loading_label.setStyleSheet("""
            color: #888;
            font-size: 18px;
            padding: 100px;
        """)
        loading_label.setAlignment(Qt.AlignCenter)
        self.home_layout.insertWidget(1, loading_label)
        QApplication.processEvents()
        
        print("Loading label added, fetching movies...")
        
        def remove_loading_label():
            """Helper to remove loading label"""
            try:
                print("Removing loading label...")
                if hasattr(self, 'home_layout'):
                    for i in range(self.home_layout.count()):
                        item = self.home_layout.itemAt(i)
                        if item and item.widget() and isinstance(item.widget(), QLabel):
                            if "Loading" in item.widget().text():
                                item.widget().deleteLater()
                                print("✓ Loading label removed")
                                break
            except Exception as e:
                print(f"Error removing loading label: {e}")
        
        try:
            # Check if we have any content
            print("Fetching movies from backend...")
            response = requests.get(f"{API_URL}/movies", timeout=10)
            print(f"Got response: {response.status_code}")
            
            if response.status_code == 200:
                movies = response.json()
                print(f"Movies count: {len(movies) if movies else 0}")
                
                # Remove loading label in all cases
                remove_loading_label()
                
                # If empty, start background scan
                if not movies or len(movies) == 0:
                    print("No content found, starting background scan...")
                    self.start_background_scan()
                else:
                    # Load existing content
                    print("Loading existing content...")
                    self.load_all_content()
                    print("✓ load_all_content() completed")
                    
                    # Start background TMDB metadata fetch
                    print("Starting TMDB fetch...")
                    self.start_tmdb_fetch()
                    print("✓ TMDB fetch started")
            else:
                print(f"Backend returned status: {response.status_code}")
                remove_loading_label()
                self._show_empty_state()
        except requests.exceptions.Timeout:
            print("Backend request timed out")
            remove_loading_label()
            self._show_empty_state()
        except requests.exceptions.ConnectionError:
            print("Backend connection error - backend may still be starting")
            remove_loading_label()
            self._show_empty_state()
        except Exception as e:
            print(f"Error in auto_load_content: {e}")
            import traceback
            traceback.print_exc()
            remove_loading_label()
            self._show_empty_state()
        
        print("========================================")
        print("auto_load_content() END")
        print("========================================")
    
    def start_tmdb_fetch(self):
        """Start background TMDB metadata fetching"""
        if self.tmdb_fetcher and self.tmdb_fetcher.isRunning():
            print("TMDB fetch already in progress")
            return
        
        # Get TMDB API key from environment
        import os
        from dotenv import load_dotenv
        
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        load_dotenv(env_path)
        tmdb_api_key = os.getenv('TMDB_API_KEY', '')
        
        if not tmdb_api_key or tmdb_api_key == "YOUR_API_KEY":
            print("⚠️  TMDB_API_KEY not configured - skipping metadata fetch")
            return
        
        print("🔍 Starting background TMDB metadata fetch...")
        from app.tmdb_fetcher import TMDBMetadataFetcher
        
        self.tmdb_fetcher = TMDBMetadataFetcher(API_URL, tmdb_api_key)
        self.tmdb_fetcher.progress.connect(self.on_tmdb_progress)
        self.tmdb_fetcher.movie_updated.connect(self.on_movie_metadata_updated)
        self.tmdb_fetcher.finished.connect(self.on_tmdb_fetch_complete)
        self.tmdb_fetcher.start()
    
    def on_tmdb_progress(self, message):
        """Handle TMDB fetch progress"""
        print(f"TMDB: {message}")
        # Optionally show in status bar
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"📥 {message}")
            self.status_label.show()
    
    def on_movie_metadata_updated(self, movie_id, metadata):
        """Handle when a movie's metadata is updated"""
        print(f"✓ Movie {movie_id} metadata updated: {list(metadata.keys())}")
        # Reload the current view to show updated posters
        # We do this sparingly to avoid too many reloads
    
    def on_tmdb_fetch_complete(self, updated_count, total_count):
        """Handle TMDB fetch completion"""
        print(f"✓ TMDB fetch complete: {updated_count}/{total_count} items updated")
        
        if updated_count > 0:
            # Reload content to show new posters
            print("Reloading content to display updated posters...")
            self.load_all_content()
            
            # Show success message
            self.show_scan_status(f"✓ Updated {updated_count} movie posters from TMDB")
        else:
            print("No new metadata fetched (movies may already have posters)")

    
    def start_background_scan(self):
        """Start scanning in background thread"""
        if self.scanner and self.scanner.isRunning():
            print("Scan already in progress")
            return
        
        print("Starting background scan thread...")
        self.scanner = BackgroundScanner()
        self.scanner.scan_complete.connect(self.on_scan_complete)
        self.scanner.scan_error.connect(self.on_scan_error)
        self.scanner.start()
        
        # Show a subtle message
        self.show_scan_status("Scanning library in background... UI remains responsive")
    
    def on_scan_complete(self, results):
        """Handle scan completion"""
        print(f"Scan complete: {results}")
        
        movies_added = results.get('movies_added', 0)
        series_added = results.get('series_added', 0)
        
        if movies_added > 0 or series_added > 0:
            self.show_scan_status(f"✓ Scan complete: {movies_added} movies, {series_added} series added")
            print("Loading content after background scan...")
            self.load_all_content()
            
            # Start TMDB metadata fetch for newly scanned movies
            print("Starting TMDB metadata fetch for scanned movies...")
            QTimer.singleShot(2000, self.start_tmdb_fetch)
        else:
            self.show_scan_status("⚠ No content found. Add video files to library/ folder")
            self._show_empty_state()
    
    def on_scan_error(self, error_msg):
        """Handle scan error"""
        print(f"Scan error: {error_msg}")
        self.show_scan_status(f"✗ Scan failed: {error_msg}")
    
    def show_scan_status(self, message):
        """Show scan status in navigation bar"""
        # Create or update status label
        if not hasattr(self, 'status_label'):
            self.status_label = QLabel()
            self.status_label.setStyleSheet("""
                color: #46d369;
                font-size: 13px;
                padding: 5px 15px;
                background-color: rgba(0, 0, 0, 0.5);
                border-radius: 4px;
            """)
            self.nav_bar.layout().insertWidget(self.nav_bar.layout().count() - 1, self.status_label)
        
        self.status_label.setText(message)
        self.status_label.show()
        
        # Auto-hide after 5 seconds
        QTimer.singleShot(5000, self.status_label.hide)
    
    def silent_scan(self):
        """DEPRECATED - use start_background_scan() instead"""
        self.start_background_scan()
    
    def load_all_content(self):
        """Load content for home view"""
        print(">>> load_all_content() START")
        try:
            # Fetch movies
            print("  Fetching movies...")
            response = requests.get(f"{API_URL}/movies", timeout=5)
            print(f"  Movies API response: {response.status_code}")
            
            if response.status_code == 200:
                movies = response.json()
                print(f"  Movies received: {type(movies)}, count: {len(movies) if movies else 0}")
                
                # Check if movies is None or empty
                if not movies or not isinstance(movies, list) or len(movies) == 0:
                    print("  No movies found in database")
                    self._show_empty_state()
                    return
                
                print(f"  Loading {len(movies)} movies into UI...")
                
                # Clear any existing error messages
                while self.home_layout.count() > 1:
                    item = self.home_layout.takeAt(1)
                    if item.widget():
                        widget = item.widget()
                        widget.deleteLater()
                
                print("  Setting featured movie...")
                # Set featured
                if len(movies) > 0 and isinstance(movies[0], dict):
                    try:
                        self.hero.set_featured(movies[0])
                        # Disconnect any previous connections
                        try:
                            self.hero.play_btn.disconnect()
                        except:
                            pass
                        self.hero.play_btn.clicked.connect(lambda m=movies[0]: self.play_movie(m))
                    except Exception as e:
                        print(f"  Error setting featured movie: {e}")
                
                print("  Creating continue watching row...")
                # Continue watching (movies with progress)
                continue_watching = [m for m in movies if m.get('last_position', 0) > 0]
                if continue_watching:
                    print(f"  Found {len(continue_watching)} movies to continue watching")
                    self.continue_watching_row = CategoryRow("Continue Watching")
                    for movie in continue_watching[:10]:
                        card = AdvancedMovieCard(movie)
                        card.play_clicked.connect(self.play_movie)
                        card.info_clicked.connect(self.show_movie_info)
                        self.continue_watching_row.add_card(card)
                    self.home_layout.insertWidget(1, self.continue_watching_row)
                    self.home_layout.insertWidget(1, self.continue_watching_row)
                
                # Get recommendations (with longer timeout and better error handling)
                try:
                    print("Fetching recommendations...")
                    rec_response = requests.get(f"{API_URL}/recommendations/movies", timeout=15)
                    if rec_response.status_code == 200:
                        recommended = rec_response.json()
                        if recommended and isinstance(recommended, list) and len(recommended) > 0:
                            print(f"Found {len(recommended)} recommendations")
                            self.recommended_row = CategoryRow("Recommended for You")
                            for movie in recommended[:10]:
                                card = AdvancedMovieCard(movie)
                                card.play_clicked.connect(self.play_movie)
                                card.info_clicked.connect(self.show_movie_info)
                                self.recommended_row.add_card(card)
                            self.home_layout.insertWidget(self.home_layout.count() - 1, self.recommended_row)
                        else:
                            print("No recommendations available")
                    else:
                        print(f"Recommendations endpoint returned: {rec_response.status_code}")
                except requests.exceptions.Timeout:
                    print("⚠ Recommendations timed out - skipping")
                except Exception as e:
                    print(f"Error loading recommendations: {e}")
                
                # All movies
                print("Creating All Movies row")
                self.all_movies_row = CategoryRow("All Movies", self.show_all_movies)
                for movie in movies[:15]:
                    card = AdvancedMovieCard(movie)
                    card.play_clicked.connect(self.play_movie)
                    card.info_clicked.connect(self.show_movie_info)
                    self.all_movies_row.add_card(card)
                self.home_layout.insertWidget(self.home_layout.count() - 1, self.all_movies_row)
                print("Content loaded successfully")
            else:
                print(f"Failed to fetch movies: {response.status_code}")
                self._show_empty_state()
        
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            # Don't show error popup if already shown on startup
            self._show_empty_state()
        except Exception as e:
            print(f"Error loading content: {e}")
            import traceback
            traceback.print_exc()
            self._show_empty_state()
    
    def load_movies_view(self):
        """Load all movies in movies view"""
        print("Loading movies view...")
        
        # Clear existing using QTimer to prevent freezing
        def clear_widgets():
            while self.movies_layout.count() > 2:
                item = self.movies_layout.takeAt(1)
                if item.widget():
                    widget = item.widget()
                    widget.hide()
                    widget.deleteLater()
            
            # Load movies after short delay
            QTimer.singleShot(100, self._load_movies_data)
        
        QTimer.singleShot(10, clear_widgets)
    
    def _load_movies_data(self):
        """Actually load the movies data"""
        try:
            print("Fetching movies from API...")
            response = requests.get(f"{API_URL}/movies", timeout=10)
            
            if response.status_code == 200:
                movies = response.json()
                print(f"DEBUG: Movies API returned {len(movies) if movies else 0} movies")
                print(f"DEBUG: movies_layout current count: {self.movies_layout.count()}")
                
                if not movies or not isinstance(movies, list) or len(movies) == 0:
                    print("No movies to display in movies view")
                    return
                
                print(f"Loading {len(movies)} movies in movies view")
                
                # Group by rating/category
                high_rated = [m for m in movies if isinstance(m, dict) and (m.get('rating') or 0) >= 7.5]
                print(f"DEBUG: Found {len(high_rated)} highly rated movies")
                
                if high_rated and len(high_rated) > 0:
                    row = CategoryRow("Highly Rated")
                    for movie in high_rated[:15]:
                        card = AdvancedMovieCard(movie)
                        card.play_clicked.connect(lambda m=movie: self.play_movie(m))
                        card.info_clicked.connect(lambda m=movie: self.show_movie_info(m))
                        row.add_card(card)
                    self.movies_layout.insertWidget(1, row)
                    print(f"DEBUG: Added Highly Rated row at position 1")
                
                # All movies
                row = CategoryRow("All Movies")
                movies_added = 0
                for movie in movies:
                    if isinstance(movie, dict):
                        card = AdvancedMovieCard(movie)
                        card.play_clicked.connect(lambda m=movie: self.play_movie(m))
                        card.info_clicked.connect(lambda m=movie: self.show_movie_info(m))
                        row.add_card(card)
                        movies_added += 1
                self.movies_layout.insertWidget(self.movies_layout.count() - 1, row)
                print(f"DEBUG: Added All Movies row with {movies_added} cards at position {self.movies_layout.count() - 2}")
                print(f"DEBUG: movies_layout final count: {self.movies_layout.count()}")
                print(f"✓ Movies view loaded with {len(movies)} movies")
                
        except requests.exceptions.Timeout:
            print("Movies API timeout")
        except Exception as e:
            print(f"Error loading movies: {e}")
            import traceback
            traceback.print_exc()
    
    def load_series_view(self):
        """Load all TV shows in series view"""
        print("Loading series view...")
        
        # Clear existing using QTimer to prevent freezing
        def clear_widgets():
            while self.series_layout.count() > 2:
                item = self.series_layout.takeAt(1)
                if item.widget():
                    widget = item.widget()
                    widget.hide()
                    widget.deleteLater()
            
            # Load series after short delay
            QTimer.singleShot(100, self._load_series_data)
        
        QTimer.singleShot(10, clear_widgets)
    
    def _load_series_data(self):
        """Actually load the series data"""
        try:
            print("Fetching series from API...")
            response = requests.get(f"{API_URL}/series", timeout=10)
            
            if response.status_code == 200:
                series = response.json()
                
                if not series or not isinstance(series, list) or len(series) == 0:
                    print("No series to display")
                    return
                
                print(f"Loading {len(series)} series")
                
                row = CategoryRow("All TV Shows")
                for show in series:
                    if isinstance(show, dict):
                        card = AdvancedMovieCard(show)
                        card.play_clicked.connect(lambda s=show: self.show_series_episodes(s))
                        card.info_clicked.connect(lambda s=show: self.show_movie_info(s))
                        row.add_card(card)
                
                self.series_layout.insertWidget(1, row)
                print(f"✓ Series view loaded with {len(series)} shows")
                
        except requests.exceptions.Timeout:
            print("Series API timeout")
        except Exception as e:
            print(f"Error loading series: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_empty_state(self):
        """Show empty state"""
        empty = QWidget()
        layout = QVBoxLayout(empty)
        layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel("📁")
        icon.setStyleSheet("font-size: 100px;")
        icon.setAlignment(Qt.AlignCenter)
        
        title = QLabel("No Content Found")
        title.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        
        desc = QLabel("Add movies to library/mo/ and TV shows to library/se/\nApp will auto-scan on next restart")
        desc.setStyleSheet("color: #999; font-size: 16px;")
        desc.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(desc)
        
        self.home_layout.insertWidget(1, empty)
    
    def _ensure_player_initialized(self):
        """Initialize video player on first use (lazy loading)"""
        if self._player_initialized:
            return True
        
        if not PLAYER_AVAILABLE:
            print("⚠ Embedded player not available - install python-vlc")
            return False
        
        try:
            print("Initializing video player...")
            # Pass return callback to player
            self.video_player = EmbeddedVideoPlayer(self, return_callback=self.return_from_player)
            self.video_player.hide()
            self.stacked_widget.addWidget(self.video_player)
            self._player_initialized = True
            print("✓ Video player initialized")
            return True
        except Exception as e:
            print(f"⚠ Embedded player initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            return False
    
    def on_player_closed(self):
        """Handle player window closed - cleanup resources"""
        print("✓ Player window closed - cleaning up reference")
        
        # Delete the player window object to free memory
        if self.player_window:
            try:
                self.player_window.deleteLater()
            except:
                pass
            self.player_window = None
        
        print("✓ Player reference cleared")
    
    def return_from_player(self):
        """Return to the previous view after closing video player"""
        # DEPRECATED - not used with standalone player window
        pass
    
    def play_movie(self, movie):
        """Play a movie using standalone player window"""
        try:
            # Validate movie path
            movie_path = movie.get("path")
            if not movie_path:
                QMessageBox.warning(self, "Error", "Movie path not found in database.")
                return
            
            if not os.path.exists(movie_path):
                QMessageBox.warning(self, "Error", f"Movie file not found:\n{movie_path}\n\nThe file may have been moved or deleted.")
                return
            
            print(f"Playing movie: {movie.get('title')} from {movie_path}")
            
            # Close existing player if any
            if self.player_window:
                print("⚠ Closing existing player window...")
                self.player_window.close()
                self.player_window = None
            
            # Create standalone player window
            from app.standalone_player import StandalonePlayerWindow
            
            self.player_window = StandalonePlayerWindow(self)
            self.player_window.closed.connect(self.on_player_closed)
            
            # Play the movie
            movie_id = movie.get('id')
            start_pos = movie.get('last_position', 0)
            
            success = self.player_window.play_media(movie_path, movie_id, "movie", start_pos)
            
            if not success:
                QMessageBox.critical(self, "Playback Error", "Failed to start playback.\n\nPlease check the console for details.")
                self.player_window.close()
                self.player_window = None
                return
            
            # Mark as watched
            try:
                requests.post(f"{API_URL}/movies/{movie['id']}/watch", timeout=5)
            except:
                pass  # Don't fail playback if watch marking fails
                
        except KeyError as e:
            QMessageBox.warning(self, "Error", f"Missing movie data: {e}\n\nPlease rescan the library.")
        except Exception as e:
            print(f"Playback error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to play movie:\n{str(e)}")
    
    def show_library(self):
        """Return to library view from player"""
        self.stacked_widget.setCurrentWidget(self.home_view)
        if self.video_player:
            self.video_player.stop()
    
    def show_movie_info(self, movie):
        """Show movie information dialog"""
        dialog = MovieInfoDialog(movie, self)
        dialog.play_clicked.connect(self.play_movie)
        dialog.delete_clicked.connect(self.delete_item)
        dialog.exec_()
    
    def delete_item(self, item_data):
        """Delete a movie or series from the library"""
        from PyQt5.QtWidgets import QMessageBox
        import requests
        import traceback
        
        try:
            item_id = item_data.get('id')
            item_type = "series" if 'seasons' in item_data else "movie"
            title = item_data.get('title', 'Unknown')
            
            print(f"🗑 Attempting to delete {item_type}: {title} (ID: {item_id})")
            
            # Delete from backend
            if item_type == "movie":
                url = f"{API_URL}/movies/{item_id}"
            else:
                url = f"{API_URL}/series/{item_id}"
            
            print(f"  → DELETE request to: {url}")
            response = requests.delete(url, timeout=5)
            print(f"  → Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Deleted successfully from backend")
                
                # Immediately remove card from UI
                self._remove_card_from_ui(item_id, item_type)
                
                QMessageBox.information(
                    self,
                    "Removed",
                    result.get('message', f"'{title}' has been removed from your library.\n\nThe video files remain on your computer.")
                )
            else:
                print(f"  ❌ Delete failed: {response.status_code}")
                print(f"  Response: {response.text}")
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to remove '{title}' from library.\n\nServer response: {response.status_code}"
                )
                
        except Exception as e:
            print(f"❌ Error deleting item: {e}")
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while removing the item:\n\n{str(e)}"
            )
    
    def _remove_card_from_ui(self, item_id, item_type):
        """Remove a specific card from the UI immediately"""
        try:
            # Find and remove from all movie items
            if item_type == "movie":
                self.all_movies = [m for m in self.all_movies if m.get('id') != item_id]
            else:
                self.all_series = [s for s in self.all_series if s.get('id') != item_id]
            
            # Refresh the current view without reloading from API
            self._refresh_current_view()
            
            print(f"✓ Removed {item_type} card (ID: {item_id}) from UI")
            
        except Exception as e:
            print(f"❌ Error removing card from UI: {e}")
    
    def _refresh_current_view(self):
        """Refresh the currently displayed content rows"""
        try:
            # Determine which layout to refresh based on current view
            if self.current_filter == "movies":
                layout = self.movies_layout
            elif self.current_filter == "series":
                layout = self.series_layout
            else:
                layout = self.home_layout
            
            # Clear existing rows (keep title and stretch)
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                widget = item.widget() if item else None
                
                # Don't delete title labels or spacers
                if widget and not isinstance(widget, QLabel):
                    widget.deleteLater()
            
            # Re-display based on current filter
            if self.current_filter == "movies":
                self.display_filtered_movies()
            elif self.current_filter == "series":
                self.display_filtered_series()
            else:
                self.display_all_content()
            
        except Exception as e:
            print(f"❌ Error refreshing view: {e}")
    
    def display_filtered_movies(self):
        """Display only movies in the current view"""
        if self.all_movies:
            row = ContentRow("🎬 Movies", self.all_movies, self)
            row.card_clicked.connect(self.show_movie_info)
            # Insert before stretch
            self.movies_layout.insertWidget(self.movies_layout.count() - 1, row)
    
    def display_filtered_series(self):
        """Display only series in the current view"""
        if self.all_series:
            row = ContentRow("📺 TV Shows", self.all_series, self)
            row.card_clicked.connect(self.show_movie_info)
            # Insert before stretch
            self.series_layout.insertWidget(self.series_layout.count() - 1, row)
    
    def display_all_content(self):
        """Display all content (both movies and series)"""
        # Show both movies and series rows
        if self.all_movies:
            row = ContentRow("🎬 Movies", self.all_movies, self)
            row.card_clicked.connect(self.show_movie_info)
            # Insert before stretch
            self.home_layout.insertWidget(self.home_layout.count() - 1, row)
        
        if self.all_series:
            row = ContentRow("📺 TV Shows", self.all_series, self)
            row.card_clicked.connect(self.show_movie_info)
            # Insert before stretch
            self.home_layout.insertWidget(self.home_layout.count() - 1, row)
    
    def refresh_external_content(self):
        """Refresh display to show/hide external drive content"""
        print("🔄 Refreshing external content...")
        
        # First, remove any existing external content row
        existing_row = None
        for i in range(self.home_layout.count()):
            widget = self.home_layout.itemAt(i).widget()
            if hasattr(widget, 'objectName') and widget.objectName() == 'external_row':
                existing_row = widget
                break
        
        if existing_row:
            print("🗑 Removing old external content row")
            self.home_layout.removeWidget(existing_row)
            existing_row.deleteLater()
        
        # Get external content
        external = self.external_manager.get_all_external_content()
        external_movies = external['movies']
        external_series = external['series']
        
        if not external_movies and not external_series:
            print("✓ No external content - row removed")
            return
        
        # Get library paths for duplicate detection
        library_paths = set()
        try:
            movies_response = requests.get(f"{API_URL}/movies", timeout=5)
            if movies_response.status_code == 200:
                library_movies = movies_response.json()
                library_paths.update(m.get('path') for m in library_movies if m.get('path'))
            
            series_response = requests.get(f"{API_URL}/series", timeout=5)
            if series_response.status_code == 200:
                library_series = series_response.json()
                for s in library_series:
                    for season in s.get('seasons', []):
                        for ep in season.get('episodes', []):
                            if ep.get('path'):
                                library_paths.add(ep['path'])
        except:
            pass
        
        # Filter out duplicates
        unique_external_movies = [
            m for m in external_movies 
            if not self.external_manager.is_duplicate(m['path'], library_paths)
        ]
        
        print(f"📱 External content: {len(unique_external_movies)} unique movies")
        
        # Add external content section to home view
        # This will be shown above regular library content
        if unique_external_movies:
            # Check if external row already exists
            existing_row = None
            for i in range(self.home_layout.count()):
                widget = self.home_layout.itemAt(i).widget()
                if hasattr(widget, 'objectName') and widget.objectName() == 'external_row':
                    existing_row = widget
                    break
            
            if existing_row:
                # Remove old row
                self.home_layout.removeWidget(existing_row)
                existing_row.deleteLater()
            
            # Create new external content row
            from app.advanced_widgets import CategoryRow
            row = CategoryRow("📱 On External Drive (Temporary)")
            row.setObjectName('external_row')
            
            for movie in unique_external_movies[:20]:
                # Create virtual card data
                card_data = {
                    'id': None,  # Not in database
                    'title': movie['title'],
                    'path': movie['path'],
                    'poster': None,
                    'is_external': True,  # Flag as external
                    'drive': movie.get('drive')
                }
                
                from app.advanced_widgets import AdvancedMovieCard
                card = AdvancedMovieCard(card_data)
                card.play_clicked.connect(lambda m=card_data: self.play_external_movie(m))
                row.add_card(card)
            
            # Insert after hero banner (position 1)
            self.home_layout.insertWidget(1, row)
            print(f"✓ Added external content row with {len(unique_external_movies)} items")
    
    def cleanup_external_drives(self):
        """Periodic cleanup of disconnected external drives"""
        try:
            if hasattr(self, 'external_manager') and self.external_manager:
                self.external_manager.cleanup_disconnected_drives()
        except Exception as e:
            print(f"⚠ Error during external drive cleanup: {e}")
    
    def play_external_movie(self, movie_data):
        """Play a movie from external drive"""
        print(f"Playing external movie: {movie_data['title']}")
        
        # Check if file still exists
        if not os.path.exists(movie_data['path']):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "File Not Found",
                f"The file is no longer accessible.\n\n"
                f"The external drive may have been disconnected."
            )
            return
        
        # Play using existing player
        self.play_movie(movie_data)
    
    def show_settings(self):
        """Show settings dialog with scan options"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("MovieFlix Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Library scan section
        library_label = QLabel("Library Management")
        library_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin-top: 10px;")
        layout.addWidget(library_label)
        
        library_desc = QLabel("Scan your computer for movies and TV series")
        library_desc.setStyleSheet("color: #999; font-size: 13px;")
        layout.addWidget(library_desc)
        
        # Scan library button
        scan_library_btn = QPushButton("📁 Rescan Library Folder")
        scan_library_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        scan_library_btn.clicked.connect(lambda: self.start_scan('library'))
        layout.addWidget(scan_library_btn)
        
        # Full PC scan button
        scan_pc_btn = QPushButton("💻 Scan Entire Computer")
        scan_pc_btn.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f40612;
            }
        """)
        scan_pc_btn.clicked.connect(lambda: self.start_scan('full_pc'))
        layout.addWidget(scan_pc_btn)
        
        scan_note = QLabel("⚠️ Full PC scan may take several minutes")
        scan_note.setStyleSheet("color: #e50914; font-size: 12px;")
        layout.addWidget(scan_note)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def start_scan(self, scan_type):
        """Start scanning process"""
        from app.scan_progress_dialog import ScanProgressDialog
        
        dialog = ScanProgressDialog(scan_type, self)
        dialog.scan_complete.connect(self.on_scan_complete)
        dialog.start_scan()
        dialog.exec_()
    
    def on_scan_complete(self, results):
        """Handle scan completion"""
        movies = results.get('movies', [])
        series = results.get('series', [])
        
        if not movies and not series:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Scan Complete",
                "No new content found."
            )
            return
        
        # Show import dialog
        from app.database_import_dialog import DatabaseImportDialog
        
        dialog = DatabaseImportDialog(movies, series, API_URL, self)
        dialog.import_complete.connect(self.on_import_complete)
        dialog.start_import(fetch_metadata=True)  # Fetch metadata during import
        dialog.exec_()
    
    def on_import_complete(self, results):
        """Handle database import completion"""
        # Reload all content to show newly added items
        print("Import complete, reloading library...")
        self.auto_load_content()

    
    def show_series_episodes(self, series):
        """Show episode selection dialog for series"""
        dialog = SeriesEpisodeDialog(series, API_URL, self)
        dialog.play_episode.connect(self.play_episode)
        dialog.exec_()
    
    def play_episode(self, episode, series_episodes=None):
        """Play a series episode using standalone player window
        
        Args:
            episode: Episode dict with path, id, etc.
            series_episodes: Optional list of all episodes for series playback
        """
        try:
            # Validate episode path
            ep_path = episode.get("path")
            if not ep_path:
                QMessageBox.warning(self, "Error", "Episode path not found in database.")
                return
            
            if not os.path.exists(ep_path):
                QMessageBox.warning(self, "Error", f"Episode file not found:\n{ep_path}\n\nThe file may have been moved or deleted.")
                return
            
            season_num = episode.get('season_number', '?')
            ep_num = episode.get('episode_number', '?')
            series_title = episode.get('series_title', 'TV Series')
            print(f"Playing episode: {series_title} - S{season_num}E{ep_num}")
            print(f"Path: {ep_path}")
            
            # Close existing player if any
            if self.player_window:
                print("⚠ Closing existing player window...")
                self.player_window.close()
                self.player_window = None
            
            # Create standalone player window
            from app.standalone_player import StandalonePlayerWindow
            
            self.player_window = StandalonePlayerWindow(self)
            self.player_window.closed.connect(self.on_player_closed)
            
            # Play the episode
            episode_id = episode.get('id')
            start_pos = episode.get("last_position", 0)
            
            success = self.player_window.play_media(ep_path, episode_id, "episode", start_pos)
            
            if not success:
                QMessageBox.critical(self, "Playback Error", "Failed to start playback.\n\nPlease check the console for details.")
                self.player_window.close()
                self.player_window = None
                return
            
            # Mark as watched
            try:
                requests.post(f"{API_URL}/episodes/{episode['id']}/watch", timeout=5)
            except:
                pass  # Don't fail playback if watch marking fails
                
        except Exception as e:
            print(f"Error playing episode: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to play episode:\n{str(e)}\n\nCheck console for details.")
    
    def load_new_popular(self):
        """Load New & Popular - TMDB trending movies and series you DON'T have"""
        print("Loading New & Popular from TMDB...")
        
        # Clear movies view
        while self.movies_layout.count() > 2:
            item = self.movies_layout.takeAt(1)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
        
        QApplication.processEvents()
        
        try:
            # Get TMDB trending content
            trending_response = requests.get(f"{API_URL}/tmdb/trending", timeout=10)
            popular_response = requests.get(f"{API_URL}/tmdb/popular", timeout=10)
            
            if trending_response.status_code == 200:
                trending = trending_response.json()
                print(f"Got {len(trending)} trending items from TMDB")
                
                # Separate movies and TV shows with posters only
                trending_movies = [t for t in trending if t.get('media_type') == 'movie' and t.get('poster_path')]
                trending_tv = [t for t in trending if t.get('media_type') == 'tv' and t.get('poster_path')]
                
                # Add Trending Movies row
                if trending_movies:
                    row = CategoryRow(f"🔥 Trending Movies on TMDB")
                    for item in trending_movies[:15]:
                        # Convert TMDB format to our format
                        movie_data = {
                            'id': None,  # Not in our library
                            'title': item.get('title', item.get('name', 'Unknown')),
                            'overview': item.get('overview', ''),
                            'rating': item.get('vote_average'),
                            'poster': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                            'path': None,  # Not in our library
                            'tmdb_id': item.get('id'),
                            'is_tmdb': True  # Flag to indicate this is from TMDB
                        }
                        card = AdvancedMovieCard(movie_data)
                        # Don't connect play - they don't have it yet
                        card.info_clicked.connect(lambda m=movie_data: self.show_tmdb_info(m))
                        row.add_card(card)
                    self.movies_layout.insertWidget(1, row)
                
                # Add Trending TV Shows row
                if trending_tv:
                    row = CategoryRow(f"📺 Trending Series on TMDB")
                    for item in trending_tv[:15]:
                        series_data = {
                            'id': None,
                            'title': item.get('name', item.get('title', 'Unknown')),
                            'overview': item.get('overview', ''),
                            'rating': item.get('vote_average'),
                            'poster': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                            'path': None,
                            'tmdb_id': item.get('id'),
                            'is_tmdb': True
                        }
                        card = AdvancedMovieCard(series_data)
                        card.info_clicked.connect(lambda m=series_data: self.show_tmdb_info(m))
                        row.add_card(card)
                    self.movies_layout.insertWidget(self.movies_layout.count() - 1, row)
            
            # Also add popular movies
            if popular_response.status_code == 200:
                popular = popular_response.json()
                if popular and len(popular) > 0:
                    # Filter to only show items with posters
                    popular_with_posters = [p for p in popular if p.get('poster_path')]
                    
                    if popular_with_posters:
                        row = CategoryRow(f"⭐ Popular on TMDB")
                        for item in popular_with_posters[:15]:
                            movie_data = {
                                'id': None,
                                'title': item.get('title', item.get('name', 'Unknown')),
                                'overview': item.get('overview', ''),
                                'rating': item.get('vote_average'),
                                'poster': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                                'path': None,
                                'tmdb_id': item.get('id'),
                                'is_tmdb': True
                            }
                            card = AdvancedMovieCard(movie_data)
                            card.info_clicked.connect(lambda m=movie_data: self.show_tmdb_info(m))
                            row.add_card(card)
                        self.movies_layout.insertWidget(self.movies_layout.count() - 1, row)
            
            print("✓ New & Popular loaded from TMDB")
                    
        except Exception as e:
            print(f"Error loading New & Popular: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error message
            label = QLabel("Unable to load trending content from TMDB.\nCheck your internet connection and TMDB API key.")
            label.setStyleSheet("color: #888; font-size: 18px; padding: 50px;")
            label.setAlignment(Qt.AlignCenter)
            self.movies_layout.insertWidget(1, label)
    
    def show_tmdb_info(self, item):
        """Show info for TMDB content (that user doesn't have)"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle(item.get('title', 'Info'))
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("background-color: #181818; color: white;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel(item.get('title', 'Unknown'))
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Rating
        if item.get('rating'):
            rating = QLabel(f"⭐ {item['rating']:.1f}/10 TMDB Rating")
            rating.setStyleSheet("font-size: 16px; color: #46d369;")
            layout.addWidget(rating)
        
        # Overview
        overview = QLabel(item.get('overview', 'No description available.'))
        overview.setWordWrap(True)
        overview.setStyleSheet("font-size: 14px; color: #e5e5e5; margin-top: 10px;")
        layout.addWidget(overview)
        
        layout.addStretch()
        
        # Info message
        info = QLabel("This content is not in your library yet.\nDownload it and add to library/mo/ or library/series/")
        info.setStyleSheet("font-size: 12px; color: #888; margin-top: 20px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f40612;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def load_my_list(self):
        """Load my list - show library organization and stats"""
        # Clear home view
        while self.home_layout.count() > 1:
            item = self.home_layout.takeAt(1)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
        
        QApplication.processEvents()
        
        try:
            # Get all movies and series
            movies_resp = requests.get(f"{API_URL}/movies", timeout=10)
            series_resp = requests.get(f"{API_URL}/series", timeout=10)
            
            movies = movies_resp.json() if movies_resp.status_code == 200 else []
            series = series_resp.json() if series_resp.status_code == 200 else []
            
            total = len(movies) + len(series)
            
            if total == 0:
                label = QLabel("Your library is empty")
                label.setStyleSheet("color: #888; font-size: 18px; padding: 50px;")
                label.setAlignment(Qt.AlignCenter)
                self.home_layout.insertWidget(1, label)
                return
            
            # Library Statistics Header
            stats_widget = QWidget()
            stats_layout = QVBoxLayout(stats_widget)
            stats_layout.setContentsMargins(60, 30, 60, 30)
            stats_layout.setSpacing(20)
            
            # Title
            title = QLabel("📚 My Library")
            title.setStyleSheet("""
                color: white;
                font-size: 36px;
                font-weight: bold;
            """)
            stats_layout.addWidget(title)
            
            # Stats boxes
            stats_row = QHBoxLayout()
            stats_row.setSpacing(20)
            
            # Movies stat
            movie_stat = self._create_stat_box("🎬", "Movies", len(movies))
            stats_row.addWidget(movie_stat)
            
            # Series stat
            series_stat = self._create_stat_box("📺", "TV Shows", len(series))
            stats_row.addWidget(series_stat)
            
            # Total stat
            total_stat = self._create_stat_box("📊", "Total Items", total)
            stats_row.addWidget(total_stat)
            
            stats_row.addStretch()
            stats_layout.addLayout(stats_row)
            
            self.home_layout.insertWidget(1, stats_widget)
            
            # Recently Added (latest 10)
            recent_items = []
            for m in movies[:10]:
                m['type'] = 'movie'
                recent_items.append(m)
            for s in series[:10]:
                s['type'] = 'series'
                recent_items.append(s)
            
            if recent_items:
                row = CategoryRow(f"Recently Added")
                for item in recent_items[:20]:
                    if isinstance(item, dict):
                        card = AdvancedMovieCard(item)
                        if item.get('type') == 'movie':
                            card.play_clicked.connect(lambda m=item: self.play_movie(m))
                        else:
                            card.play_clicked.connect(lambda s=item: self.show_series_episodes(s))
                        card.info_clicked.connect(lambda i=item: self.show_movie_info(i))
                        row.add_card(card)
                self.home_layout.insertWidget(self.home_layout.count() - 1, row)
            
            # All Movies
            if movies:
                row = CategoryRow(f"All Movies ({len(movies)})")
                for movie in movies:
                    if isinstance(movie, dict):
                        card = AdvancedMovieCard(movie)
                        card.play_clicked.connect(lambda m=movie: self.play_movie(m))
                        card.info_clicked.connect(lambda m=movie: self.show_movie_info(m))
                        row.add_card(card)
                self.home_layout.insertWidget(self.home_layout.count() - 1, row)
            
            # All Series
            if series:
                row = CategoryRow(f"All TV Shows ({len(series)})")
                for show in series:
                    if isinstance(show, dict):
                        card = AdvancedMovieCard(show)
                        card.play_clicked.connect(lambda s=show: self.show_series_episodes(s))
                        card.info_clicked.connect(lambda s=show: self.show_movie_info(s))
                        row.add_card(card)
                self.home_layout.insertWidget(self.home_layout.count() - 1, row)
                
        except Exception as e:
            print(f"Error loading my list: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_stat_box(self, icon, label, count):
        """Create a statistics box"""
        box = QFrame()
        box.setFixedSize(180, 120)
        box.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a,
                    stop:1 #1a1a1a);
                border-radius: 12px;
                border: 1px solid #3a3a3a;
            }
        """)
        
        layout = QVBoxLayout(box)
        layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 40px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        count_label = QLabel(str(count))
        count_label.setStyleSheet("""
            color: #e50914;
            font-size: 28px;
            font-weight: bold;
        """)
        count_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(count_label)
        
        text_label = QLabel(label)
        text_label.setStyleSheet("color: #aaa; font-size: 13px;")
        text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(text_label)
        
        return box
    
    def show_user_menu(self):
        """Show user menu with options"""
        from PyQt5.QtWidgets import QMenu, QAction
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 8px;
            }
            QMenu::item {
                padding: 10px 30px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #e50914;
            }
        """)
        
        # Profile Management
        profile_action = QAction("👤 Manage Profile", self)
        profile_action.triggered.connect(self.show_profile_settings)
        menu.addAction(profile_action)
        
        menu.addSeparator()
        
        # Add Folder action
        add_folder_action = QAction("➕ Add Folder to Library", self)
        add_folder_action.triggered.connect(self.add_folder_to_library)
        menu.addAction(add_folder_action)
        
        # Rescan action
        rescan_action = QAction("🔄 Rescan Library", self)
        rescan_action.triggered.connect(self.start_background_scan)
        menu.addAction(rescan_action)
        
        menu.addSeparator()
        
        # Sign out action
        signout_action = QAction("🚪 Sign Out", self)
        signout_action.triggered.connect(self.sign_out)
        menu.addAction(signout_action)
        
        # Show menu near user button
        menu.exec_(self.mapToGlobal(self.nav_bar.geometry().topRight()))
    
    def add_folder_to_library(self):
        """Add a folder to the library"""
        from PyQt5.QtWidgets import QFileDialog, QInputDialog
        
        # Ask what type of content
        items = ("Movies", "TV Shows")
        item, ok = QInputDialog.getItem(
            self, "Add Folder",
            "What type of content is in this folder?",
            items, 0, False
        )
        
        if not ok:
            return
        
        # Select folder
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Add",
            os.path.expanduser("~")
        )
        
        if not folder:
            return
        
        try:
            # Send request to backend to scan this folder
            content_type = "movies" if item == "Movies" else "series"
            response = requests.post(
                f"{API_URL}/library/scan_folder",
                json={"path": folder, "type": content_type},
                timeout=120
            )
            
            if response.status_code == 200:
                results = response.json()
                added = results.get('added', 0)
                QMessageBox.information(
                    self,
                    "Folder Added",
                    f"Successfully added {added} {item.lower()} from:\n{folder}"
                )
                # Reload content
                self.load_all_content()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to add folder: {response.text}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to add folder:\n{str(e)}"
            )
    
    def sign_out(self):
        """Sign out and return to login"""
        reply = QMessageBox.question(
            self,
            "Sign Out",
            "Are you sure you want to sign out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear credentials
            global AUTH_CREDENTIALS
            AUTH_CREDENTIALS = None
            
            # Close main window
            self.close()
            
            # Show login dialog
            login = LoginDialog(API_URL)
            if login.exec_() == LoginDialog.Accepted:
                # Restart app
                self.__init__()
                self.show()
    
    def show_profile_settings(self):
        """Show redesigned profile management dialog"""
        from app.profile_dialog import ProfileManagementDialog
        
        dialog = ProfileManagementDialog(AUTH_CREDENTIALS.get('username', 'User'), self)
        if dialog.exec_() == ProfileManagementDialog.Accepted:
            # Profile was updated, refresh UI
            self.update_user_display()
    
    def update_user_display(self):
        """Update user display in navbar"""
        if hasattr(self, 'nav_bar') and hasattr(self.nav_bar, 'user_btn'):
            avatar = AUTH_CREDENTIALS.get('avatar', '👤')
            self.nav_bar.user_btn.setText(avatar)
    
    def load_new_popular(self):
        """Load TMDB movies from last 3 months that are NOT in library"""
        print("Loading New & Popular...")
        
        # Clear movies view
        def clear_widgets():
            while self.movies_layout.count() > 2:
                item = self.movies_layout.takeAt(1)
                if item.widget():
                    widget = item.widget()
                    widget.hide()
                    widget.deleteLater()
            
            QTimer.singleShot(100, self._load_new_popular_data)
        
        QTimer.singleShot(10, clear_widgets)
    
    def _load_new_popular_data(self):
        """Load TMDB new releases"""
        try:
            # Get TMDB new releases (not in library)
            response = requests.get(f"{API_URL}/tmdb/new-releases", timeout=10)
            
            if response.status_code == 200:
                tmdb_movies = response.json()
                
                if tmdb_movies and len(tmdb_movies) > 0:
                    row = CategoryRow("New Releases (Not in Library)")
                    for movie in tmdb_movies[:20]:
                        # Create card with TMDB data
                        card = AdvancedMovieCard(movie)
                        # Since these aren't in library, show info only
                        card.play_clicked.connect(lambda m=movie: self.show_tmdb_info(m))
                        card.info_clicked.connect(lambda m=movie: self.show_tmdb_info(m))
                        row.add_card(card)
                    self.movies_layout.insertWidget(1, row)
                
            # Get TMDB trending
            response = requests.get(f"{API_URL}/tmdb/trending", timeout=10)
            
            if response.status_code == 200:
                trending = response.json()
                
                if trending and len(trending) > 0:
                    row = CategoryRow("Trending on TMDB")
                    for movie in trending[:20]:
                        card = AdvancedMovieCard(movie)
                        card.play_clicked.connect(lambda m=movie: self.show_tmdb_info(m))
                        card.info_clicked.connect(lambda m=movie: self.show_tmdb_info(m))
                        row.add_card(card)
                    self.movies_layout.insertWidget(self.movies_layout.count() - 1, row)
            
            print("✓ New & Popular loaded")
            
        except Exception as e:
            print(f"Error loading new & popular: {e}")
            import traceback
            traceback.print_exc()
    
    def show_tmdb_info(self, movie):
        """Show info for TMDB movie (not in library)"""
        QMessageBox.information(
            self,
            movie.get('title', 'Unknown'),
            f"{movie.get('title', 'Unknown')}\n\n"
            f"Rating: {movie.get('rating', 'N/A')}/10\n"
            f"Release: {movie.get('release_date', 'Unknown')}\n\n"
            f"{movie.get('overview', 'No description')}\n\n"
            f"This movie is not in your library yet."
        )
    
    def show_series_detail(self, series):
        """Show series detail - DEPRECATED, use show_series_episodes instead"""
        self.show_series_episodes(series)
    
    def show_all_movies(self):
        """Navigate to all movies"""
        self.switch_view("movies")
    
    def scan_library(self):
        """DEPRECATED - Auto-scan in background now"""
        print("Manual scan requested, starting background scan...")
        self.start_background_scan()



# Alias for launcher compatibility
MovieLibraryApp = AdvancedMovieLibrary


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(20, 20, 20))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)
    
    # Set font
    try:
        font = QFont("Segoe UI", 10)
        app.setFont(font)
    except:
        pass
    
    try:
        # Show login dialog first
        login = LoginDialog(API_URL)
        
        if login.exec_() == LoginDialog.Accepted:
            # Login successful, store credentials globally
            AUTH_CREDENTIALS = login.credentials
            
            # Show main window
            window = AdvancedMovieLibrary()
            window.show()
            sys.exit(app.exec_())
        else:
            # User cancelled login
            print("Login cancelled")
            sys.exit(0)
            
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        QMessageBox.critical(None, "Fatal Error", f"Application failed to start:\n{str(e)}")
        sys.exit(1)
