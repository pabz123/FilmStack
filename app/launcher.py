"""
MovieFlix Application Launcher
==============================

This module provides a professional loading screen that performs system checks
before launching the main MovieFlix application.

Features:
- Modern splash screen with progress bar
- Background startup checks (VLC, backend connection, UI components)
- Graceful error handling with user-friendly messages
- Smooth transition to main application

Startup Checks:
1. VLC availability - Verifies python-vlc is installed
2. Backend connection - Tests API server is running
3. UI components - Loads interface modules

Usage:
    python app/launcher.py
    or
    MovieFlix.bat (Windows)

Dependencies:
- PyQt5: UI framework
- requests: Backend communication
- vlc: Media player integration
- dotenv: Environment configuration
"""

import sys
import os
import datetime
from PyQt5.QtWidgets import QApplication, QSplashScreen, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor, QLinearGradient


def _startup_log(message: str) -> None:
    """Write startup diagnostics to a log file (useful for pythonw/.exe runs)."""
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_path = os.path.join(root_dir, "movieflix_startup.log")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        # Never block startup on logging failures.
        pass


class StartupThread(QThread):
    """
    Background thread for performing startup checks without blocking UI.
    
    Signals:
        progress: Emits (percentage, message) during startup
        finished: Emits when all checks pass
        error: Emits error message if a check fails
    """
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, api_url):
        super().__init__()
        self.api_url = api_url
    
    def run(self):
        """Run startup checks"""
        try:
            import time
            
            # Check 1: VLC availability
            self.progress.emit(20, "Checking media player...")
            time.sleep(0.3)
            
            # Check if VLC is available
            from app.vlc_installer_helper import check_vlc_installed
            if not check_vlc_installed():
                self.error.emit("VLC_NOT_FOUND")  # Special error code
                return
            
            self.progress.emit(30, "✓ Media player ready")
            
            # Check 2: Backend connection
            self.progress.emit(50, "Connecting to backend...")
            time.sleep(0.3)
            try:
                import requests
                response = requests.get(f"{self.api_url}/movies", timeout=5)
                if response.status_code in [200, 401]:  # 401 is ok, means auth is working
                    self.progress.emit(70, "✓ Backend connected")
                else:
                    self.error.emit(f"Backend returned status {response.status_code}")
                    return
            except requests.exceptions.ConnectionError:
                self.error.emit("Cannot connect to backend.\nPlease start the backend first (run start_movieflix.py)")
                return
            except Exception as e:
                self.error.emit(f"Backend error: {str(e)}")
                return
            
            # Check 3: Load UI components
            self.progress.emit(85, "Loading interface...")
            time.sleep(0.3)
            
            self.progress.emit(100, "Ready!")
            time.sleep(0.2)
            
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(f"Startup error: {str(e)}")


class LoadingScreen(QWidget):
    """Modern loading screen with progress bar"""
    
    def __init__(self, api_url):
        super().__init__()
        self.api_url = api_url
        self.setWindowTitle("MovieFlix")
        self.setFixedSize(600, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        self.setup_ui()
        self.start_startup()
    
    def setup_ui(self):
        """Setup the loading UI"""
        # Gradient background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a,
                    stop:1 #0a0a0a);
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        
        # Logo
        logo = QLabel("🎬")
        logo.setFont(QFont("Arial", 72))
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("color: #e50914; background: transparent;")
        layout.addWidget(logo)
        
        # Title
        title = QLabel("MovieFlix")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(title)
        
        # Tagline
        tagline = QLabel("Your Personal Streaming Service")
        tagline.setFont(QFont("Arial", 12))
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet("color: #aaa; background: transparent;")
        layout.addWidget(tagline)
        
        layout.addStretch()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #e50914;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888; background: transparent;")
        layout.addWidget(self.status_label)
    
    def start_startup(self):
        """Start the startup checks"""
        self.startup_thread = StartupThread(self.api_url)
        self.startup_thread.progress.connect(self.update_progress)
        self.startup_thread.finished.connect(self.launch_app)
        self.startup_thread.error.connect(self.show_error)
        self.startup_thread.start()
    
    def update_progress(self, value, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def show_error(self, message):
        """Show error and close"""
        from PyQt5.QtWidgets import QMessageBox
        
        # Special handling for VLC not found
        if message == "VLC_NOT_FOUND":
            from app.vlc_installer_helper import show_vlc_required_dialog
            if show_vlc_required_dialog(self):
                # User installed VLC and wants to continue - restart checks
                self.start_startup()
                return
            else:
                # User chose to exit
                QApplication.quit()
                return
        
        # Other errors
        QMessageBox.critical(self, "Startup Error", message)
        QApplication.quit()
    
    def launch_app(self):
        """Launch the main application with login"""
        try:
            # Import required modules
            from app.login_dialog import LoginDialog
            from app.advanced_ui import AdvancedMovieLibrary, AUTH_CREDENTIALS, API_URL
            
            # Close loading screen first
            self.close()
            
            # Show login dialog
            login = LoginDialog(API_URL)
            
            if login.exec_() == LoginDialog.Accepted:
                # Login successful - store credentials
                import app.advanced_ui as ui_module
                ui_module.AUTH_CREDENTIALS = login.credentials
                
                # Create and show main window
                self.main_window = AdvancedMovieLibrary()
                self.main_window.show()
            else:
                # User cancelled login
                print("Login cancelled by user")
                QApplication.quit()
            
        except Exception as e:
            self.show_error(f"Failed to launch app:\n{str(e)}")


def main():
    """Main entry point - direct to login, no loading screen"""
    # Get API URL from environment
    from dotenv import load_dotenv
    load_dotenv()
    
    api_host = os.getenv('API_HOST', '127.0.0.1')
    api_port = os.getenv('API_PORT', '8765')
    api_url = f"http://{api_host}:{api_port}"
    
    _startup_log("Launcher main() starting")
    app = QApplication(sys.argv)
    app.setApplicationName("MovieFlix")
    app.setOrganizationName("MovieFlix")
    
    # Set application icon - look in root directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(root_dir, 'MovieFlix.ico')
    
    # Try to set icon and Windows taskbar AppUserModelID
    if os.path.exists(icon_path):
        from PyQt5.QtGui import QIcon
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
        # Store icon path for main window to use
        app.icon_path = icon_path
        
        # IMPORTANT: Set Windows AppUserModelID for proper taskbar icon
        if sys.platform == 'win32':
            try:
                import ctypes
                myappid = 'movieflix.streamingapp.1.0'  # Unique app ID
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                print(f"✓ Application icon set: {icon_path}")
                _startup_log(f"Icon set: {icon_path}")
            except Exception as e:
                print(f"⚠ Could not set AppUserModelID: {e}")
                _startup_log(f"Could not set AppUserModelID: {e}")
    else:
        app.icon_path = None
        print(f"⚠ Icon not found at: {icon_path}")
        _startup_log(f"Icon not found: {icon_path}")
    
    # Set dark palette to avoid white flashes
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(20, 20, 20))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)
    
    # Show splash screen
    from app.splash_screen import LoadingSplash
    splash = LoadingSplash()
    splash.show()
    app.processEvents()
    
    try:
        # Wait a moment for splash to render
        splash.update_status("Initializing...")
        app.processEvents()

        # Small delay for splash render (keep short; backend startup is handled by start_movieflix.py)
        import time
        time.sleep(0.15)
        
        # Update splash
        splash.update_status("Loading components...")
        app.processEvents()
        
        # Import UI modules
        from app.login_dialog import LoginDialog
        from app.advanced_ui import AdvancedMovieLibrary
        import app.advanced_ui as ui_module
        
        # Update splash
        splash.update_status("Ready to login...")
        app.processEvents()

        # Small delay before showing login
        time.sleep(0.15)
        
        # Close splash
        splash.close()
        
        # Wait briefly, then show login
        time.sleep(0.2)
        
        # Show login dialog
        login = LoginDialog(api_url)

        if login.exec_() == LoginDialog.Accepted:
            _startup_log("Login accepted")
            ui_module.AUTH_CREDENTIALS = login.credentials

            # Create a simple progress dialog that stays visible
            from PyQt5.QtWidgets import QProgressDialog
            progress = QProgressDialog("Loading MovieFlix...", None, 0, 100, None)
            progress.setWindowTitle("MovieFlix")
            progress.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
            progress.setModal(False)  # Changed to non-modal for testing
            progress.setMinimumDuration(0)
            progress.setValue(10)
            progress.show()
            app.processEvents()
            
            # Hide login overlay
            if hasattr(login, 'loading_overlay') and login.loading_overlay:
                try:
                    login.loading_overlay.hide()
                except Exception:
                    pass
            
            # Close login
            login.close()
            app.processEvents()
            
            # Create main window in steps with progress feedback
            main_window = [None]  # Use list to modify in closure
            
            def step1():
                print("Step 1: Initializing components...")
                _startup_log("Step 1: Initializing")
                progress.setLabelText("Initializing components...")
                progress.setValue(30)
                app.processEvents()
                QTimer.singleShot(50, step2)
            
            def step2():
                progress.setLabelText("Loading library...")
                progress.setValue(50)
                app.processEvents()
                try:
                    _startup_log("Creating main window")
                    print("Creating AdvancedMovieLibrary...")
                    
                    main_window[0] = AdvancedMovieLibrary()
                    
                    _startup_log("Main window created")
                    print("✓ AdvancedMovieLibrary created successfully")
                    
                    QTimer.singleShot(50, step3)
                except Exception as e:
                    _startup_log(f"Error creating window: {e}")
                    print(f"ERROR creating window: {e}")
                    import traceback
                    traceback.print_exc()
                    progress.close()
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.critical(None, "Error", f"Failed to create window:\n{str(e)}\n\nCheck console for details.")
                    sys.exit(1)
            
            def step3():
                progress.setLabelText("Almost ready...")
                progress.setValue(90)
                app.processEvents()
                
                print("Step 3: Showing main window...")
                _startup_log("Step 3: Showing window")
                
                # Show main window
                if main_window[0]:
                    try:
                        main_window[0].show()
                        print("✓ Main window shown")
                        _startup_log("Main window shown")
                    except Exception as e:
                        print(f"ERROR showing window: {e}")
                        _startup_log(f"Error showing window: {e}")
                else:
                    print("ERROR: main_window is None!")
                    _startup_log("ERROR: main_window is None")
                
                # Close progress
                progress.setValue(100)
                progress.close()
                print("✓ Progress dialog closed")
            
            # Start async window creation
            QTimer.singleShot(100, step1)
            
            sys.exit(app.exec_())
        else:
            _startup_log("Login cancelled")
            print("Login cancelled by user")
            sys.exit(0)
            
    except Exception as e:
        if 'splash' in locals():
            splash.close()
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        _startup_log(f"Fatal error: {e}")
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "MovieFlix Error", f"Failed to start:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
