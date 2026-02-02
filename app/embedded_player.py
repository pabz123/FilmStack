"""
Embedded VLC Player Widget - Netflix-Style In-Window Video Playback
===================================================================

This module provides a custom PyQt5 widget that embeds VLC media player
for seamless in-window video playback, similar to Netflix's player.

Key Features:
-------------
- Embedded VLC player (no external window)
- Custom UI controls (play/pause, seek, volume, fullscreen)
- Mouse wheel volume control
- Keyboard shortcuts (Space, F11, arrows)
- Progress tracking and resume capability
- Cross-platform support (Windows, macOS, Linux)

VLC Detection Strategy:
----------------------
The module automatically searches for VLC in the following order:
1. Local project directory (vlc/ or VLC/ folder)
2. Windows system paths:
   - C:\Program Files\VideoLAN\VLC
   - C:\Program Files (x86)\VideoLAN\VLC
3. System PATH environment variable

This allows for both portable (local VLC) and system-wide installations.

Video Output Configuration:
--------------------------
- Windows: Uses HWND (window handle) for embedding
- macOS: Uses NSObject for native embedding
- Linux: Uses XWindow for X11 embedding

Quality Settings:
----------------
- Hardware decoding enabled (--avcodec-hw=any)
- High-quality audio resampling (soxr)
- Optimized caching for smooth playback
- No video title overlay for clean experience

Usage Example:
-------------
```python
from app.embedded_player import EmbeddedVideoPlayer

# Create player widget
player = EmbeddedVideoPlayer(parent_widget)

# Play a movie
player.play_media(
    path="/path/to/movie.mp4",
    movie_id=1,
    media_type="movie",
    start_position=0
)

# Control playback
player.play_pause()          # Toggle play/pause
player.set_volume(70)        # Set volume 0-100
player.toggle_fullscreen()   # Enter/exit fullscreen
```

Dependencies:
------------
- python-vlc: Python bindings for VLC media player
- PyQt5: GUI framework
- VLC installation (system or local)

Author: MovieFlix Team
Version: 1.0
"""
import sys
import os
import platform
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QPalette, QColor

# Try to find and load VLC
VLC_AVAILABLE = False

def find_vlc_dll():
    """
    Find VLC DLL in multiple locations.
    Checks:
    1. Local vlc/ directory in project
    2. System installation paths
    3. PATH environment variable
    """
    possible_paths = []
    
    # 1. Check local vlc directory (both lowercase and uppercase)
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for vlc_name in ['vlc', 'VLC']:
        local_vlc = os.path.join(current_dir, vlc_name)
        if os.path.exists(local_vlc):
            possible_paths.append(local_vlc)
            print(f"✓ Found local VLC directory: {local_vlc}")
    
    # 2. Check common installation paths
    if platform.system() == 'Windows':
        common_paths = [
            r"C:\Program Files\VideoLAN\VLC",
            r"C:\Program Files (x86)\VideoLAN\VLC",
        ]
        for path in common_paths:
            if os.path.exists(path):
                possible_paths.append(path)
    
    # Add to PATH for python-vlc to find
    if possible_paths:
        current_path = os.environ.get('PATH', '')
        new_paths = ';'.join(possible_paths) if platform.system() == 'Windows' else ':'.join(possible_paths)
        os.environ['PATH'] = f"{new_paths};{current_path}" if current_path else new_paths
        print(f"✓ Added VLC paths to environment: {possible_paths}")
    
    return possible_paths

# Find VLC before importing
find_vlc_dll()

try:
    import vlc
    VLC_AVAILABLE = True
    print("✓ VLC module loaded successfully")
except Exception as e:
    VLC_AVAILABLE = False
    print(f"⚠ VLC module not available: {e}")


class EmbeddedVideoPlayer(QWidget):
    """Netflix-style embedded video player with advanced controls"""
    
    def __init__(self, parent=None, return_callback=None):
        super().__init__(parent)
        self.media_player = None
        self.is_playing = False
        self.is_fullscreen = False
        self.current_movie_id = None
        self.current_type = None
        self.return_callback = return_callback  # Callback to return to previous view
        self.current_episode_list = []  # For series playback
        self.current_episode_index = 0
        self.subtitle_files = []  # Available subtitle files
        self.audio_devices = []  # Available audio devices
        self.current_episode_info = None  # Store current episode info for display
        self.current_series_title = None  # Store series title
        
        if not VLC_AVAILABLE:
            print("⚠ VLC not available - player will not function")
            self.setup_error_ui()
            return
        
        # Create VLC instance with optimal quality settings
        vlc_args = [
            '--no-video-title-show',  # Don't show filename on video
            '--avcodec-hw=any',  # Hardware acceleration
            '--audio-resampler=soxr',  # High quality audio resampling
            '--network-caching=300',  # Low caching for local files
            '--file-caching=300',
            '--sout-mux-caching=300',
            '--cr-average=1000',
            '--audio-desync=0',  # Keep audio synced
            '--no-skip-frames',  # Don't skip frames
            '--no-audio-time-stretch',  # Better audio quality
            '--quiet'  # Suppress console output
        ]
        vlc_args = [arg for arg in vlc_args if arg]  # Remove empty strings
        
        try:
            self.instance = vlc.Instance(' '.join(vlc_args))
            if not self.instance:
                raise Exception("Failed to create VLC instance")
                
            self.media_player = self.instance.media_player_new()
            if not self.media_player:
                raise Exception("Failed to create media player")
            
            # Set audio output to highest quality
            self.media_player.audio_set_volume(70)
            
            print("✓ VLC player initialized successfully")
            
        except Exception as e:
            print(f"❌ VLC initialization error: {e}")
            import traceback
            traceback.print_exc()
            self.setup_error_ui()
            return
        
        self.setup_ui()
        
        # Timer to update position
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_ui)
        
        # Install event filter for mouse wheel
        self.installEventFilter(self)
    
    def setup_error_ui(self):
        """Setup error UI when VLC is not available"""
        layout = QVBoxLayout(self)
        error_label = QLabel("❌ VLC Player Not Available\n\nPlease ensure VLC is installed properly.")
        error_label.setStyleSheet("color: white; font-size: 18px;")
        error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(error_label)
    
    def setup_ui(self):
        """Setup the player UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Episode info banner at top (for series)
        self.episode_info_banner = QWidget()
        self.episode_info_banner.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 0, 0, 220),
                    stop:0.7 rgba(0, 0, 0, 180),
                    stop:1 rgba(0, 0, 0, 0));
                padding: 20px;
            }
        """)
        self.episode_info_banner.setFixedHeight(80)
        
        banner_layout = QVBoxLayout(self.episode_info_banner)
        banner_layout.setContentsMargins(20, 10, 20, 10)
        
        self.series_title_label = QLabel()
        self.series_title_label.setStyleSheet("color: #999; font-size: 14px;")
        banner_layout.addWidget(self.series_title_label)
        
        self.episode_title_label = QLabel()
        self.episode_title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        banner_layout.addWidget(self.episode_title_label)
        
        self.episode_info_banner.hide()  # Hidden by default
        layout.addWidget(self.episode_info_banner)
        
        # Video frame - ensure it stretches to fill space
        self.video_frame = QWidget()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setMinimumSize(640, 360)  # Minimum 16:9 size
        self.video_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.video_frame, 1)  # Stretch factor of 1
        
        # Controls at bottom
        controls_bg = QWidget()
        controls_bg.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 0, 0, 0),
                    stop:0.3 rgba(0, 0, 0, 180),
                    stop:1 rgba(0, 0, 0, 220));
                padding: 10px;
            }
        """)
        controls_bg.setFixedHeight(100)
        
        controls_layout = QVBoxLayout(controls_bg)
        controls_layout.setContentsMargins(20, 10, 20, 10)
        
        # Progress slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.position_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #e50914;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #e50914;
                border-radius: 3px;
            }
        """)
        controls_layout.addWidget(self.position_slider)
        
        # Buttons row
        button_row = QHBoxLayout()
        button_row.setSpacing(15)
        
        # Play/Pause button
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setFixedSize(50, 50)
        self.play_pause_btn.clicked.connect(self.play_pause)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        button_row.addWidget(self.play_pause_btn)
        
        # Skip backward button
        skip_back_btn = QPushButton("⏪")
        skip_back_btn.setFixedSize(40, 40)
        skip_back_btn.setToolTip("Skip Back 10s (Left Arrow)")
        skip_back_btn.clicked.connect(lambda: self.skip(-10))
        skip_back_btn.setStyleSheet(self.play_pause_btn.styleSheet().replace("50", "40"))
        button_row.addWidget(skip_back_btn)
        
        # Skip forward button
        skip_forward_btn = QPushButton("⏩")
        skip_forward_btn.setFixedSize(40, 40)
        skip_forward_btn.setToolTip("Skip Forward 10s (Right Arrow)")
        skip_forward_btn.clicked.connect(lambda: self.skip(10))
        skip_forward_btn.setStyleSheet(self.play_pause_btn.styleSheet().replace("50", "40"))
        button_row.addWidget(skip_forward_btn)
        
        # Next episode button (hidden by default)
        self.next_episode_btn = QPushButton("Next ▶")
        self.next_episode_btn.setFixedSize(80, 40)
        self.next_episode_btn.setToolTip("Next Episode")
        self.next_episode_btn.clicked.connect(self.play_next_episode)
        self.next_episode_btn.setStyleSheet(self.play_pause_btn.styleSheet().replace("50", "40"))
        self.next_episode_btn.hide()  # Hidden until series is playing
        button_row.addWidget(self.next_episode_btn)
        
        # Time label
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: white; font-size: 14px;")
        button_row.addWidget(self.time_label)
        
        button_row.addStretch()
        
        # Subtitle button
        self.subtitle_btn = QPushButton("CC")
        self.subtitle_btn.setFixedSize(40, 40)
        self.subtitle_btn.setToolTip("Subtitles (S)")
        self.subtitle_btn.clicked.connect(self.show_subtitle_menu)
        self.subtitle_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        button_row.addWidget(self.subtitle_btn)
        
        # Audio button
        self.audio_btn = QPushButton("🔉")
        self.audio_btn.setFixedSize(40, 40)
        self.audio_btn.setToolTip("Audio Settings (A)")
        self.audio_btn.clicked.connect(self.show_audio_menu)
        self.audio_btn.setStyleSheet(self.subtitle_btn.styleSheet())
        button_row.addWidget(self.audio_btn)
        
        # Speed button
        self.speed_btn = QPushButton("1x")
        self.speed_btn.setFixedSize(40, 40)
        self.speed_btn.setToolTip("Playback Speed")
        self.speed_btn.clicked.connect(self.show_speed_menu)
        self.speed_btn.setStyleSheet(self.subtitle_btn.styleSheet())
        button_row.addWidget(self.speed_btn)
        
        # Volume slider
        volume_label = QLabel("🔊")
        volume_label.setStyleSheet("color: white; font-size: 18px;")
        button_row.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: white;
                border-radius: 2px;
            }
        """)
        button_row.addWidget(self.volume_slider)
        
        # Fullscreen button
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setFixedSize(40, 40)
        self.fullscreen_btn.setToolTip("Toggle Fullscreen (F)")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        button_row.addWidget(self.fullscreen_btn)
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.clicked.connect(self.close_player)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #e50914;
            }
        """)
        button_row.addWidget(self.close_btn)
        
        controls_layout.addLayout(button_row)
        layout.addWidget(controls_bg)
        
        # Store controls widget for hiding in fullscreen
        self.controls_widget = controls_bg
    
    def eventFilter(self, obj, event):
        """Handle mouse wheel for volume control"""
        if event.type() == QEvent.Wheel and self.is_playing:
            delta = event.angleDelta().y()
            current_vol = self.volume_slider.value()
            new_vol = max(0, min(100, current_vol + (5 if delta > 0 else -5)))
            self.volume_slider.setValue(new_vol)
            return True
        return super().eventFilter(obj, event)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks - show/hide controls in fullscreen"""
        if self.is_fullscreen and hasattr(self, 'controls_widget'):
            if self.controls_widget.isVisible():
                self.controls_widget.hide()
            else:
                self.controls_widget.show()
                # Auto-hide after 3 seconds
                QTimer.singleShot(3000, self.hide_controls_if_fullscreen)
        super().mousePressEvent(event)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_Space:
            self.play_pause()
        elif event.key() == Qt.Key_F or event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape:
            if self.is_fullscreen:
                self.toggle_fullscreen()
            else:
                self.close_player()
        elif event.key() == Qt.Key_Up:
            self.volume_slider.setValue(min(100, self.volume_slider.value() + 5))
        elif event.key() == Qt.Key_Down:
            self.volume_slider.setValue(max(0, self.volume_slider.value() - 5))
        elif event.key() == Qt.Key_Left:
            if self.media_player:
                self.media_player.set_time(max(0, self.media_player.get_time() - 10000))
        elif event.key() == Qt.Key_Right:
            if self.media_player:
                self.media_player.set_time(self.media_player.get_time() + 10000)
        else:
            super().keyPressEvent(event)
    
    def toggle_fullscreen(self):
        """Toggle TRUE fullscreen mode - covers entire screen, hides everything"""
        if self.is_fullscreen:
            # Exit fullscreen
            print("Exiting fullscreen...")
            self.is_fullscreen = False
            
            # Get parent window (AdvancedMovieLibrary)
            parent = self.parent()
            if parent:
                # Restore window flags to normal
                parent.setWindowFlags(Qt.Window)
                
                # Show navbar if it exists
                if hasattr(parent, 'nav_bar'):
                    parent.nav_bar.show()
                
                # Exit fullscreen and restore to maximized
                parent.showNormal()
                parent.showMaximized()
            
            # Show player controls
            if hasattr(self, 'controls_widget'):
                self.controls_widget.show()
            
            # Show episode info banner if it was visible
            if hasattr(self, 'episode_info_banner'):
                if self.current_episode_info:  # Only show if playing episode
                    self.episode_info_banner.show()
            
            # Update button
            if hasattr(self, 'fullscreen_btn'):
                self.fullscreen_btn.setText("⛶")
            
            print("✓ Exited fullscreen mode")
        else:
            # Enter TRUE fullscreen
            print("Entering TRUE fullscreen...")
            self.is_fullscreen = True
            
            # Get parent window
            parent = self.parent()
            if parent:
                # Hide navbar to give more screen space
                if hasattr(parent, 'nav_bar'):
                    parent.nav_bar.hide()
                
                # Make window frameless (no borders) and always on top
                parent.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                
                # Get the FULL screen geometry (including taskbar area)
                from PyQt5.QtWidgets import QApplication
                desktop = QApplication.desktop()
                screen_rect = desktop.screenGeometry(desktop.primaryScreen())
                
                # Set window to cover entire screen
                parent.setGeometry(screen_rect)
                parent.showFullScreen()
                parent.show()  # Must call show() after changing window flags
            
            # Set focus to player so keyboard events work
            self.setFocus()
            
            # Update button
            if hasattr(self, 'fullscreen_btn'):
                self.fullscreen_btn.setText("◱")
            
            # Auto-hide controls after 3 seconds in fullscreen
            if hasattr(self, 'controls_widget'):
                QTimer.singleShot(3000, self.hide_controls_if_fullscreen)
            
            print("✓ Entered TRUE fullscreen mode - Press ESC or F to exit")
    
    def hide_controls_if_fullscreen(self):
        """Hide controls if still in fullscreen"""
        if self.is_fullscreen and hasattr(self, 'controls_widget'):
            self.controls_widget.hide()
    
    def play_media(self, path, movie_id, media_type, start_position=0):
        """Play a media file"""
        if not self.media_player:
            print("❌ ERROR: Media player not initialized - VLC may not be properly loaded")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Player Error",
                "VLC Media Player is not initialized.\n\n"
                "Please ensure:\n"
                "1. VLC directory exists at: D:\\movie_library\\VLC\\\n"
                "2. libvlc.dll and libvlccore.dll are present\n"
                "3. Restart MovieFlix"
            )
            return False
        
        # Validate file exists
        if not os.path.exists(path):
            print(f"❌ ERROR: File not found: {path}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Media file not found:\n{path}\n\nThe file may have been moved or deleted."
            )
            return False
        
        try:
            self.current_movie_id = movie_id
            self.current_type = media_type
            
            # Show episode info if it's a series
            if media_type == "episode" and self.current_episode_info:
                self.series_title_label.setText(self.current_series_title or "TV Series")
                season = self.current_episode_info.get('season_number', '?')
                episode = self.current_episode_info.get('episode_number', '?')
                title = self.current_episode_info.get('title', 'Episode')
                self.episode_title_label.setText(f"S{season}E{episode} - {title}")
                self.episode_info_banner.show()
                # Auto-hide after 5 seconds
                QTimer.singleShot(5000, self.episode_info_banner.hide)
            else:
                self.episode_info_banner.hide()
            
            print(f"▶ Loading media: {path}")
            
            # Stop any existing playback safely
            if self.is_playing:
                print("⏹ Stopping current playback...")
                self.media_player.stop()
                QTimer.singleShot(200, lambda: self._continue_play(path, start_position))
                return True
            else:
                return self._continue_play(path, start_position)
                
        except Exception as e:
            print(f"❌ ERROR in play_media: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _continue_play(self, path, start_position):
        """Continue playing after stop"""
        try:
            print(f"📀 Creating media object for: {path}")
            
            # Load media
            media = self.instance.media_new(path)
            if not media:
                print("❌ ERROR: Failed to create media object")
                return False
                
            self.media_player.set_media(media)
            
            # Set video output to our frame
            print(f"🖥️ Setting video output (Platform: {platform.system()})")
            if platform.system() == "Windows":
                self.media_player.set_hwnd(int(self.video_frame.winId()))
            elif platform.system() == "Darwin":  # macOS
                self.media_player.set_nsobject(int(self.video_frame.winId()))
            else:  # Linux
                self.media_player.set_xwindow(int(self.video_frame.winId()))
            
            # Set initial volume
            volume = self.volume_slider.value()
            self.media_player.audio_set_volume(volume)
            print(f"🔊 Volume set to: {volume}")
            
            # Play
            print("▶ Starting playback...")
            result = self.media_player.play()
            if result == -1:
                print("❌ ERROR: VLC play() returned -1 (failed to start)")
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(
                    self,
                    "Playback Failed",
                    f"VLC failed to start playback.\n\nFile: {os.path.basename(path)}\n\n"
                    "This may be due to:\n"
                    "- Unsupported codec\n"
                    "- Corrupted file\n"
                    "- Missing VLC plugins"
                )
                return False
            
            self.is_playing = True
            self.play_pause_btn.setText("⏸")
            
            # Start position if resuming
            if start_position > 0:
                QTimer.singleShot(1000, lambda: self.media_player.set_time(int(start_position * 1000)))
            
            # Start update timer
            self.timer.start()
            
            # Auto-load subtitles if available
            QTimer.singleShot(1500, lambda: self.auto_load_subtitles(path))
            
            print(f"✅ Playback started successfully!")
            return True
            
        except Exception as e:
            print(f"❌ ERROR in _continue_play: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def play_pause(self):
        """Toggle play/pause"""
        if not self.media_player:
            return
        
        if self.is_playing:
            self.media_player.pause()
            self.play_pause_btn.setText("▶")
            self.is_playing = False
        else:
            self.media_player.play()
            self.play_pause_btn.setText("⏸")
            self.is_playing = True
    
    def set_position(self, position):
        """Set playback position"""
        if self.media_player:
            self.media_player.set_time(position)
    
    def set_volume(self, volume):
        """Set volume"""
        if self.media_player:
            self.media_player.audio_set_volume(volume)
    
    def update_ui(self):
        """Update UI with current playback state"""
        if not self.media_player:
            return
        
        # Update position slider
        length = self.media_player.get_length()
        if length > 0:
            self.position_slider.setRange(0, length)
            self.position_slider.setValue(self.media_player.get_time())
            
            # Update time label
            current = self.media_player.get_time() // 1000
            total = length // 1000
            self.time_label.setText(f"{self.format_time(current)} / {self.format_time(total)}")
    
    def format_time(self, seconds):
        """Format seconds to HH:MM:SS or MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def skip(self, seconds):
        """Skip forward/backward by seconds"""
        if self.media_player:
            current = self.media_player.get_time()
            new_time = max(0, current + (seconds * 1000))
            self.media_player.set_time(new_time)
            print(f"Skipped {seconds}s to {new_time/1000:.1f}s")
    
    def show_subtitle_menu(self):
        """Show subtitle selection menu"""
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(0, 0, 0, 0.9);
                color: white;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #e50914;
            }
        """)
        
        # Add "Load Subtitle File" option
        load_action = menu.addAction("📁 Load Subtitle File...")
        load_action.triggered.connect(self.load_subtitle_file)
        
        menu.addSeparator()
        
        # Add subtitle track options if available
        if self.media_player:
            # Get available subtitle tracks
            spu_count = self.media_player.video_get_spu_count()
            if spu_count > 0:
                current_spu = self.media_player.video_get_spu()
                
                # Disable subtitles option
                disable_action = menu.addAction("❌ Disable Subtitles")
                disable_action.triggered.connect(lambda: self.media_player.video_set_spu(-1))
                
                # List available tracks
                for i in range(spu_count):
                    track_desc = self.media_player.video_get_spu_description()
                    if track_desc and i < len(track_desc):
                        track_name = track_desc[i][1].decode() if isinstance(track_desc[i][1], bytes) else str(track_desc[i][1])
                    else:
                        track_name = f"Track {i+1}"
                    
                    action = menu.addAction(f"{'✓ ' if i == current_spu else ''}  {track_name}")
                    action.triggered.connect(lambda checked, idx=i: self.media_player.video_set_spu(idx))
        
        # Show menu at button
        menu.exec_(self.subtitle_btn.mapToGlobal(self.subtitle_btn.rect().bottomLeft()))
    
    def load_subtitle_file(self):
        """Load external subtitle file"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Subtitle File",
            "",
            "Subtitle Files (*.srt *.ass *.ssa *.vtt);;All Files (*.*)"
        )
        
        if file_path and self.media_player:
            result = self.media_player.video_set_subtitle_file(file_path)
            if result == 0:
                print(f"✓ Loaded subtitle: {file_path}")
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Success", "Subtitle loaded successfully!")
            else:
                print(f"✗ Failed to load subtitle: {file_path}")
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", "Failed to load subtitle file.")
    
    def show_audio_menu(self):
        """Show audio settings menu"""
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(0, 0, 0, 0.9);
                color: white;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #e50914;
            }
        """)
        
        if self.media_player:
            # Audio tracks
            track_count = self.media_player.audio_get_track_count()
            if track_count > 0:
                current_track = self.media_player.audio_get_track()
                
                menu.addAction("🎵 Audio Tracks:").setEnabled(False)
                
                for i in range(track_count):
                    track_desc = self.media_player.audio_get_track_description()
                    if track_desc and i < len(track_desc):
                        track_name = track_desc[i][1].decode() if isinstance(track_desc[i][1], bytes) else str(track_desc[i][1])
                    else:
                        track_name = f"Track {i+1}"
                    
                    action = menu.addAction(f"{'✓ ' if i == current_track else ''}  {track_name}")
                    action.triggered.connect(lambda checked, idx=i: self.media_player.audio_set_track(idx))
                
                menu.addSeparator()
            
            # Audio devices
            menu.addAction("🔊 Audio Output:").setEnabled(False)
            
            # Note: VLC audio_output_device_enum is complex, simplified for now
            default_action = menu.addAction("✓ Default Output")
            default_action.setEnabled(False)
        
        menu.exec_(self.audio_btn.mapToGlobal(self.audio_btn.rect().bottomLeft()))
    
    def show_speed_menu(self):
        """Show playback speed menu"""
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(0, 0, 0, 0.9);
                color: white;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #e50914;
            }
        """)
        
        speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        current_speed = self.media_player.get_rate() if self.media_player else 1.0
        
        for speed in speeds:
            action = menu.addAction(f"{'✓ ' if abs(speed - current_speed) < 0.01 else ''}  {speed}x")
            action.triggered.connect(lambda checked, s=speed: self.set_playback_speed(s))
        
        menu.exec_(self.speed_btn.mapToGlobal(self.speed_btn.rect().bottomLeft()))
    
    def set_playback_speed(self, speed):
        """Set playback speed"""
        if self.media_player:
            self.media_player.set_rate(speed)
            self.speed_btn.setText(f"{speed}x")
            print(f"Playback speed: {speed}x")
    
    def play_next_episode(self):
        """Play next episode in series"""
        if self.current_episode_list and self.current_episode_index < len(self.current_episode_list) - 1:
            self.current_episode_index += 1
            next_episode = self.current_episode_list[self.current_episode_index]
            
            # Play next episode
            self.play_media(
                path=next_episode.get('path'),
                movie_id=next_episode.get('id'),
                media_type='episode',
                start_position=0
            )
            print(f"Playing next episode: {next_episode.get('title')}")
        else:
            print("No more episodes")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Series Complete", "No more episodes available.")
    
    def auto_load_subtitles(self, video_path):
        """Auto-load subtitle file if exists in same folder"""
        if not self.media_player:
            return
        
        video_dir = os.path.dirname(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        
        # Check for subtitle files with same name
        subtitle_extensions = ['.srt', '.ass', '.ssa', '.vtt']
        for ext in subtitle_extensions:
            subtitle_path = os.path.join(video_dir, video_name + ext)
            if os.path.exists(subtitle_path):
                print(f"Auto-loading subtitle: {subtitle_path}")
                self.media_player.video_set_subtitle_file(subtitle_path)
                return True
        
        return False
    
    def close_player(self):
        """Close the player and return to library"""
        try:
            # Stop playback safely
            if self.media_player and self.is_playing:
                self.is_playing = False
                self.timer.stop()
                self.media_player.stop()
                # Wait a bit for VLC to cleanup
                QTimer.singleShot(100, self._finish_close)
            else:
                self._finish_close()
        except Exception as e:
            print(f"Error closing player: {e}")
            self._finish_close()
    
    def _finish_close(self):
        """Finish closing the player"""
        try:
            self.hide()
            # Use callback if provided, otherwise fallback to parent method
            if self.return_callback:
                self.return_callback()
            elif self.parent():
                self.parent().show_library()
        except Exception as e:
            print(f"Error in _finish_close: {e}")
    
    def stop(self):
        """Stop playback"""
        try:
            if self.media_player and self.is_playing:
                self.is_playing = False
                self.timer.stop()
                self.media_player.stop()
                self.play_pause_btn.setText("▶")
        except Exception as e:
            print(f"Error stopping playback: {e}")
