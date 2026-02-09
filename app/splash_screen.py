"""
MovieFlix Loading Splash Screen
"""
from PyQt5.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget, QApplication, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QFont
import sys


class LoadingSplash(QWidget):
    """Loading splash screen with progress bar."""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 300)
        
        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # Setup UI
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Container with dark background
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #141414;
                border-radius: 10px;
                border: 2px solid #E50914;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(20)
        
        # Logo/Title
        title = QLabel("MovieFlix")
        title.setStyleSheet("""
            QLabel {
                color: #E50914;
                font-size: 48px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        
        # Status message
        self.status_label = QLabel("Initializing backend server...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
                background: transparent;
                border: none;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #333;
                border-radius: 5px;
                background-color: #222;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #E50914;
                border-radius: 3px;
            }
        """)
        
        # Timeout warning (hidden initially)
        self.warning_label = QLabel("This is taking longer than usual...\nPlease wait or check startup log.")
        self.warning_label.setStyleSheet("""
            QLabel {
                color: #FFA500;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.hide()
        
        # Add to layout
        container_layout.addWidget(title)
        container_layout.addWidget(self.status_label)
        container_layout.addWidget(self.progress)
        container_layout.addWidget(self.warning_label)
        container_layout.addStretch()
        
        layout.addWidget(container)
        self.setLayout(layout)
        
        # Timer for timeout warning
        self.warning_timer = QTimer()
        self.warning_timer.timeout.connect(self.show_warning)
        self.warning_timer.setSingleShot(True)
        self.warning_timer.start(15000)  # Show warning after 15 seconds
    
    def show_warning(self):
        """Show warning if loading takes too long."""
        self.warning_label.show()
    
    def update_status(self, message):
        """Update status message."""
        self.status_label.setText(message)
        QApplication.processEvents()
    
    def set_progress(self, value):
        """Set progress bar value (0-100)."""
        if self.progress.maximum() == 0:
            self.progress.setRange(0, 100)
        self.progress.setValue(value)
        QApplication.processEvents()


def show_loading_splash():
    """Show loading splash screen."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    splash = LoadingSplash()
    splash.show()
    app.processEvents()
    
    return app, splash