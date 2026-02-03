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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.media_player = None
        self.is_playing = False
        self.is_fullscreen = False
        self.current_movie_id = None
        self.current_type = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        
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
    
    def play_media(self, path, movie_id=None, media_type="movie", start_position=0):
        """Play a media file"""
        if not self.media_player:
            return False
        
        if not os.path.exists(path):
            print(f"❌ File not found: {path}")
            return False
        
        try:
            self.current_movie_id = movie_id
            self.current_type = media_type
            
            print(f"▶ Loading: {path}")
            
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
        """Handle window close"""
        if self.media_player:
            self.media_player.stop()
        self.timer.stop()
        self.closed.emit()
        event.accept()
    
    def stop(self):
        """Stop playback"""
        if self.media_player:
            self.media_player.stop()
        self.is_playing = False
        self.play_pause_btn.setText("▶")
        self.timer.stop()
