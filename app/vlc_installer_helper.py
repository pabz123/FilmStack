"""
VLC Installation Helper
Shows friendly dialog when VLC is not found
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtCore import QUrl
import subprocess
import sys


class VLCNotFoundDialog(QDialog):
    """Dialog shown when VLC is not detected on the system"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VLC Media Player Required")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        # Setup UI
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🎬 VLC Media Player Required")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Message
        message = QLabel(
            "MovieFlix needs VLC Media Player for video playback.\n\n"
            "VLC is a free, open-source media player used by millions worldwide."
        )
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        
        # Instructions
        instructions = QLabel(
            "<b>Installation Steps:</b><br><br>"
            "1. Click 'Download VLC' below<br>"
            "2. Download and install VLC<br>"
            "3. Restart MovieFlix<br><br>"
            "<i>VLC will be detected automatically!</i>"
        )
        instructions.setWordWrap(True)
        instructions.setTextFormat(Qt.RichText)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        """)
        layout.addWidget(instructions)
        
        # Download button
        download_btn = QPushButton("📥 Download VLC (Free)")
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6600;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #ff7700;
            }
        """)
        download_btn.clicked.connect(self.download_vlc)
        download_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(download_btn)
        
        # Check again button
        check_btn = QPushButton("🔄 I've Installed VLC - Check Again")
        check_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                font-size: 13px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        check_btn.clicked.connect(self.check_vlc_again)
        check_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(check_btn)
        
        # Exit button
        exit_btn = QPushButton("Exit MovieFlix")
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px;
                font-size: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        exit_btn.clicked.connect(self.exit_app)
        exit_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(exit_btn)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Apply window styling
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)
    
    def download_vlc(self):
        """Open VLC download page in browser"""
        try:
            if sys.platform == 'win32':
                url = "https://www.videolan.org/vlc/download-windows.html"
            elif sys.platform == 'darwin':
                url = "https://www.videolan.org/vlc/download-macosx.html"
            else:
                url = "https://www.videolan.org/vlc/#download"
            QDesktopServices.openUrl(QUrl(url))
            if sys.platform.startswith('linux'):
                QMessageBox.information(
                    self,
                    "Install VLC on Linux",
                    "On Ubuntu/Debian, run in a terminal:\n\n"
                    "  sudo apt update && sudo apt install vlc\n\n"
                    "After installing VLC, click 'Check Again' below."
                )
            else:
                QMessageBox.information(
                    self,
                    "Download Started",
                    "VLC download page opened in your browser.\n\n"
                    "After installing VLC, click 'Check Again' below."
                )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not open browser.\n\n"
                f"Please install VLC:\n"
                f"  Ubuntu/Debian: sudo apt install vlc\n"
                f"  Other Linux:   https://www.videolan.org/vlc/\n\n"
                f"Error: {str(e)}"
            )
    
    def check_vlc_again(self):
        """Check if VLC is now installed"""
        try:
            import vlc
            # Try to create instance to verify it works
            instance = vlc.Instance()
            instance.release()
            
            QMessageBox.information(
                self,
                "Success!",
                "✓ VLC detected successfully!\n\n"
                "Click OK to continue to MovieFlix."
            )
            self.accept()  # Close dialog with success
        except Exception as e:
            QMessageBox.warning(
                self,
                "VLC Not Found",
                "VLC is still not detected.\n\n"
                "Please make sure:\n"
                "1. VLC is fully installed\n"
                "2. You've restarted this application\n\n"
                "If the problem persists, try:\n"
                "- Reinstalling VLC\n"
                "- Restarting your computer\n\n"
                f"Technical details: {str(e)}"
            )
    
    def exit_app(self):
        """Exit the application"""
        self.reject()  # Close dialog with cancel
        sys.exit(0)


def check_vlc_installed():
    """
    Check if VLC is installed and working.
    Returns True if VLC is available, False otherwise.
    Shows dialog if VLC is not found.
    """
    try:
        import vlc
        # Try to create instance
        instance = vlc.Instance()
        instance.release()
        return True
    except ImportError:
        # python-vlc not installed
        return False
    except Exception:
        # VLC library not found on system
        return False


def show_vlc_required_dialog(parent=None):
    """
    Show VLC required dialog.
    Returns True if user installed VLC and wants to continue,
    False if user chose to exit.
    """
    dialog = VLCNotFoundDialog(parent)
    result = dialog.exec_()
    return result == QDialog.Accepted
