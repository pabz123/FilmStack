"""
Standalone VLC Player Window - Separate Window Like VLC
=======================================================

This module provides a standalone video player window that opens independently
from the main MovieFlix window, similar to how VLC works.

Features:
- Independent window with its own controls
- Can be minimized/maximized separately
- Proper keyboard focus handling
- Fullscreen mode
- Always stays on top of main window
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QSlider, QLabel, QMainWindow, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
import os
import platform
import sys

# VLC import
try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    print("⚠ python-vlc not installed")
    VLC_AVAILABLE = False


class StandalonePlayerWindow(QMainWindow):
    """Standalone video player window"""
    
    closed = pyqtSignal()  # Signal when window is closed
    play_next_requested = pyqtSignal(object)  # Signal to request next content
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.media_player = None
        self.is_playing = False
        self.is_fullscreen = False
        self.current_movie_id = None
        self.current_type = None
        self.current_media_data = None  # Store current movie/episode data
        self.next_media_data = None  # Store next episode/movie data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        
        # Auto-play next
        self.autoplay_overlay = None
        self.autoplay_timer = QTimer()
        self.autoplay_timer.timeout.connect(self.autoplay_countdown)
        self.autoplay_countdown_value = 10
        
        # Window setup
        self.setWindowTitle("MovieFlix Player")
        self.setMinimumSize(800, 600)
        self.resize(1280, 720)
        
        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "MovieFlix.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Set window flags to stay on top but allow minimizing
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        
        # Dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000;
            }
            QPushButton {
                background-color: #333;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #333;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #e50914;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
        """)
        
        if not VLC_AVAILABLE:
            self.setup_error_ui()
            return
        
        # Initialize VLC
        vlc_args = [
            '--no-video-title-show',
            '--avcodec-hw=any',
            '--audio-resampler=soxr',
            '--network-caching=300',
            '--file-caching=300',
        ]
        
        self.instance = vlc.Instance(vlc_args)
        self.media_player = self.instance.media_player_new()
        
        self.setup_ui()
    
    def setup_error_ui(self):
        """Setup error UI"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        error_label = QLabel("❌ VLC Not Available\n\nPlease install VLC player")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("font-size: 18px; color: white;")
        layout.addWidget(error_label)
    
    def setup_ui(self):
        """Setup the player UI"""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Video frame
        self.video_frame = QWidget()
        self.video_frame.setStyleSheet("background-color: black;")
        layout.addWidget(self.video_frame, 1)
        
        # Controls
        controls = QWidget()
        controls.setStyleSheet("background-color: rgba(20, 20, 20, 250); padding: 10px;")
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(10, 10, 10, 10)
        
        # Progress slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.sliderMoved.connect(self.set_position)
        controls_layout.addWidget(self.position_slider)
        
        # Buttons and time
        button_row = QHBoxLayout()
        
        # Play/Pause
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.clicked.connect(self.play_pause)
        self.play_pause_btn.setFixedSize(50, 40)
        button_row.addWidget(self.play_pause_btn)
        
        # Time label
        self.time_label = QLabel("00:00 / 00:00")
        button_row.addWidget(self.time_label)
        
        button_row.addStretch()
        
        # Volume
        vol_label = QLabel("🔊")
        button_row.addWidget(vol_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.change_volume)
        button_row.addWidget(self.volume_slider)
        
        # Fullscreen
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.fullscreen_btn.setFixedSize(40, 40)
        button_row.addWidget(self.fullscreen_btn)
        
        controls_layout.addLayout(button_row)
        
        layout.addWidget(controls)
        
        self.controls_widget = controls
    
    def play_media(self, path, movie_id=None, media_type="movie", start_position=0, media_data=None, next_media=None):
        """Play a media file
        
        Args:
            path: Path to video file
            movie_id: Database ID
            media_type: "movie" or "episode"
            start_position: Start position in seconds
            media_data: Full media data dict (for auto-next)
            next_media: Next episode/movie data (for auto-next)
        """
        if not self.media_player:
            return False
        
        if not os.path.exists(path):
            print(f"❌ File not found: {path}")
            return False
        
        try:
            self.current_movie_id = movie_id
            self.current_type = media_type
            self.current_media_data = media_data
            self.next_media_data = next_media
            
            # Reset trigger flags for new media
            if hasattr(self, '_credits_triggered'):
                delattr(self, '_credits_triggered')
            if hasattr(self, '_end_triggered'):
                delattr(self, '_end_triggered')
            
            print(f"▶ Loading: {path}")
            if next_media:
                print(f"📺 Next queued: {next_media.get('title', 'Unknown')}")
            
            # Create media
            media = self.instance.media_new(path)
            if not media:
                return False
            
            self.media_player.set_media(media)
            
            # Set video output
            if platform.system() == "Windows":
                self.media_player.set_hwnd(int(self.video_frame.winId()))
            elif platform.system() == "Darwin":
                self.media_player.set_nsobject(int(self.video_frame.winId()))
            else:
                self.media_player.set_xwindow(int(self.video_frame.winId()))
            
            # Set volume
            self.media_player.audio_set_volume(self.volume_slider.value())
            
            # Play
            result = self.media_player.play()
            if result == -1:
                print("❌ Playback failed")
                return False
            
            self.is_playing = True
            self.play_pause_btn.setText("⏸")
            
            # Start position
            if start_position > 0:
                QTimer.singleShot(1000, lambda: self.media_player.set_time(int(start_position * 1000)))
            
            # Start timer
            self.timer.start(1000)
            
            # Show window and focus
            self.show()
            self.raise_()
            self.activateWindow()
            
            print("✅ Playback started")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def play_pause(self):
        """Toggle play/pause"""
        if not self.media_player:
            return
        
        if self.is_playing:
            self.media_player.pause()
            self.is_playing = False
            self.play_pause_btn.setText("▶")
        else:
            self.media_player.play()
            self.is_playing = True
            self.play_pause_btn.setText("⏸")
    
    def set_position(self, position):
        """Seek to position"""
        if self.media_player:
            self.media_player.set_position(position / 1000.0)
    
    def change_volume(self, value):
        """Change volume"""
        if self.media_player:
            self.media_player.audio_set_volume(value)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen"""
        if self.is_fullscreen:
            self.showNormal()
            self.controls_widget.show()
            self.is_fullscreen = False
            self.fullscreen_btn.setText("⛶")
        else:
            self.showFullScreen()
            QTimer.singleShot(3000, lambda: self.controls_widget.hide() if self.is_fullscreen else None)
            self.is_fullscreen = True
            self.fullscreen_btn.setText("◱")
    
    def update_ui(self):
        """Update UI elements"""
        if not self.media_player:
            return
        
        # Update position
        length = self.media_player.get_length()
        position = self.media_player.get_time()
        
        if length > 0:
            self.position_slider.setMaximum(1000)
            self.position_slider.setValue(int(position * 1000 / length))
            
            # Update time
            pos_min = int(position / 60000)
            pos_sec = int((position % 60000) / 1000)
            len_min = int(length / 60000)
            len_sec = int((length % 60000) / 1000)
            self.time_label.setText(f"{pos_min:02d}:{pos_sec:02d} / {len_min:02d}:{len_sec:02d}")
            
            # Check if we're in the credits zone (last 5% of video OR last 3 minutes, whichever is shorter)
            if length > 0 and position > 0 and self.next_media_data:
                # Calculate when to show "Next" button
                # For episodes: last 5% or last 3 minutes
                # For movies: last 5% or last 5 minutes
                if self.current_type == "episode":
                    credits_threshold = min(length * 0.95, length - 180000)  # 95% or last 3 min
                else:
                    credits_threshold = min(length * 0.95, length - 300000)  # 95% or last 5 min
                
                # Trigger when entering credits zone
                if position >= credits_threshold and not hasattr(self, '_credits_triggered'):
                    self._credits_triggered = True
                    print(f"🎬 Credits detected at {pos_min:02d}:{pos_sec:02d} - showing auto-next")
                    QTimer.singleShot(500, self.on_video_ended)
            
            # Fallback: If no next content, close when video actually ends (last 2 seconds)
            if not self.next_media_data and length > 0 and position > 0:
                time_remaining = (length - position) / 1000  # seconds
                if time_remaining <= 2 and time_remaining > 0 and not hasattr(self, '_end_triggered'):
                    self._end_triggered = True
                    print("🎬 Video ended - closing player")
                    QTimer.singleShot(3000, self.close)
    
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
                self.close()
        elif event.key() == Qt.Key_Left:
            if self.media_player:
                self.media_player.set_time(max(0, self.media_player.get_time() - 10000))
        elif event.key() == Qt.Key_Right:
            if self.media_player:
                self.media_player.set_time(self.media_player.get_time() + 10000)
        elif event.key() == Qt.Key_Up:
            self.volume_slider.setValue(min(100, self.volume_slider.value() + 5))
        elif event.key() == Qt.Key_Down:
            self.volume_slider.setValue(max(0, self.volume_slider.value() - 5))
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close with proper cleanup"""
        print("🔄 Cleaning up player resources...")
        
        # Stop timers
        self.timer.stop()
        self.autoplay_timer.stop()
        
        # Hide overlay if exists
        if self.autoplay_overlay:
            self.autoplay_overlay.hide()
            self.autoplay_overlay.deleteLater()
            self.autoplay_overlay = None
        
        # Stop and release media player
        if self.media_player:
            self.media_player.stop()
            # Release media
            self.media_player.set_media(None)
            # Release media player
            self.media_player.release()
            self.media_player = None
        
        # Release VLC instance
        if hasattr(self, 'instance') and self.instance:
            self.instance.release()
            self.instance = None
        
        print("✓ Player resources cleaned up")
        self.closed.emit()
        event.accept()
    
    def on_video_ended(self):
        """Handle credits/end - show auto-play overlay"""
        print("📺 Credits/End detected")
        
        if self.next_media_data:
            print(f"✓ Next content available: {self.next_media_data.get('title')}")
            self.show_autoplay_overlay()
        else:
            print("ℹ No next content - will close when video ends")
            # Don't close immediately - let video finish naturally
    
    def show_autoplay_overlay(self):
        """Show auto-play next overlay with countdown (Netflix-style bottom-right)"""
        if not self.next_media_data:
            return
        
        # Create overlay widget positioned in bottom-right corner
        self.autoplay_overlay = QWidget(self.centralWidget())
        self.autoplay_overlay.setStyleSheet("""
            QWidget {
                background-color: rgba(20, 20, 20, 0.95);
                border: 2px solid #e50914;
                border-radius: 8px;
            }
        """)
        
        # Position in bottom-right corner
        overlay_width = 400
        overlay_height = 220
        margin = 20
        parent_width = self.centralWidget().width()
        parent_height = self.centralWidget().height()
        
        x = parent_width - overlay_width - margin
        y = parent_height - overlay_height - margin - 100  # Account for controls
        
        self.autoplay_overlay.setGeometry(x, y, overlay_width, overlay_height)
        
        layout = QVBoxLayout(self.autoplay_overlay)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Title
        if self.current_type == "episode":
            title_text = "Next Episode"
        else:
            title_text = "Up Next"
        
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Next content title
        next_title = self.next_media_data.get('title', 'Unknown')
        if self.current_type == "episode":
            season = self.next_media_data.get('season_number', '?')
            episode = self.next_media_data.get('episode_number', '?')
            series_title = self.next_media_data.get('series_title', '')
            next_title = f"S{season}E{episode}"
            if series_title:
                next_title += f": {series_title}"
        
        content_label = QLabel(next_title)
        content_label.setStyleSheet("font-size: 14px; color: #ccc;")
        content_label.setWordWrap(True)
        content_label.setMaximumWidth(360)
        layout.addWidget(content_label)
        
        # Countdown label
        self.countdown_label = QLabel(f"Playing in {self.autoplay_countdown_value}s...")
        self.countdown_label.setStyleSheet("font-size: 13px; color: #999; margin-top: 10px;")
        layout.addWidget(self.countdown_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Play now button
        play_now_btn = QPushButton("▶ Play Now")
        play_now_btn.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f40612;
            }
        """)
        play_now_btn.clicked.connect(self.play_next_now)
        play_now_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(play_now_btn)
        
        # Cancel button
        cancel_btn = QPushButton("✕ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        cancel_btn.clicked.connect(self.cancel_autoplay)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Show overlay
        self.autoplay_overlay.show()
        self.autoplay_overlay.raise_()
        
        # Start countdown
        self.autoplay_countdown_value = 10
        self.autoplay_timer.start(1000)  # 1 second interval
    
    def autoplay_countdown(self):
        """Update countdown and auto-play when reaches 0"""
        self.autoplay_countdown_value -= 1
        
        if self.autoplay_countdown_value > 0:
            self.countdown_label.setText(f"Playing in {self.autoplay_countdown_value}s...")
        else:
            # Time's up - play next
            self.autoplay_timer.stop()
            self.play_next_now()
    
    def play_next_now(self):
        """Play next content immediately"""
        print("▶ Playing next content now")
        
        # Hide overlay
        if self.autoplay_overlay:
            self.autoplay_overlay.hide()
            self.autoplay_overlay.deleteLater()
            self.autoplay_overlay = None
        
        # Stop timer
        self.autoplay_timer.stop()
        
        # Emit signal to play next
        if self.next_media_data:
            self.play_next_requested.emit(self.next_media_data)
            # Close this player - parent will open new one
            self.close()
    
    def cancel_autoplay(self):
        """Cancel auto-play and close player"""
        print("✕ Auto-play cancelled")
        
        # Stop timer
        self.autoplay_timer.stop()
        
        # Hide overlay
        if self.autoplay_overlay:
            self.autoplay_overlay.hide()
            self.autoplay_overlay.deleteLater()
            self.autoplay_overlay = None
        
        # Close player
        self.close()
    
    def stop(self):
        """Stop playback"""
        if self.media_player:
            self.media_player.stop()
        self.is_playing = False
        self.play_pause_btn.setText("▶")
        self.timer.stop()
