"""
Modern Splash Screen for MovieFlix
Shows on startup before login
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon
import os


class SplashScreen(QWidget):
    """Modern splash screen with MovieFlix branding"""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window size
        self.setFixedSize(500, 300)
        
        # Center on screen
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()
        self.move(
            int((screen.width() - self.width()) / 2),
            int((screen.height() - self.height()) / 2)
        )
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container with background
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #141414;
                border-radius: 12px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(20)
        
        # Icon/Logo area
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Try to load icon
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(root_dir, 'MovieFlix.ico')
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            # Fallback to text logo
            icon_label.setText("🎬")
            icon_label.setStyleSheet("font-size: 60px;")
        
        container_layout.addWidget(icon_label)
        
        # App name
        name_label = QLabel("MovieFlix")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("""
            color: #E50914;
            font-size: 36px;
            font-weight: bold;
            font-family: 'Arial', sans-serif;
        """)
        container_layout.addWidget(name_label)
        
        # Tagline
        tagline = QLabel("Your Personal Streaming Library")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet("""
            color: #e5e5e5;
            font-size: 14px;
            margin-top: -10px;
        """)
        container_layout.addWidget(tagline)
        
        container_layout.addSpacing(20)
        
        # Status label
        self.status_label = QLabel("Starting up...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #999;
            font-size: 13px;
        """)
        container_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.setFixedHeight(4)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #2a2a2a;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #E50914;
                border-radius: 2px;
            }
        """)
        container_layout.addWidget(self.progress)
        
        container_layout.addStretch()
        
        # Version/Copyright
        version = QLabel("© 2026 MovieFlix")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("""
            color: #666;
            font-size: 11px;
        """)
        container_layout.addWidget(version)
        
        layout.addWidget(container)
        
    def update_status(self, message):
        """Update status message"""
        self.status_label.setText(message)
        
    def close_with_fade(self):
        """Close splash with fade effect"""
        from PyQt5.QtCore import QPropertyAnimation
        from PyQt5.QtWidgets import QGraphicsOpacityEffect
        
        opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(opacity_effect)
        
        self.fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()
