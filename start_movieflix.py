"""
MovieFlix Silent Launcher
=========================

Starts backend silently in background, then launches GUI.
No console windows visible to user.
"""

import os
import sys
import subprocess
import time
import socket
import datetime
import threading

# Add backend to path for config import
sys.path.insert(0, os.path.dirname(__file__))

try:
    from backend.config import STARTUP_LOG, BACKEND_LOG, ensure_dir_exists
    # Ensure log directory exists
    ensure_dir_exists(STARTUP_LOG.parent)
    _log_path = str(STARTUP_LOG)
except ImportError:
    # Fallback if config not available
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    _log_path = os.path.join(current_dir, "movieflix_startup.log")


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except OSError:
            return True


def _startup_log(message: str) -> None:
    """Write startup diagnostics to a log file."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(_log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def start_backend_threaded():
    """Start backend in a background thread (for frozen exe)."""
    # Get dynamic port from config
    try:
        from backend.config import BACKEND_PORT
        port = BACKEND_PORT
    except ImportError:
        port = 8765  # Fallback
    
    def run_backend():
        try:
            _startup_log(f"Backend thread: Importing uvicorn and FastAPI app (port {port})")
            import uvicorn
            
            # Import backend app
            try:
                from backend.main import app
                _startup_log("Backend thread: Successfully imported backend.main.app")
            except Exception as import_error:
                _startup_log(f"Backend thread: Failed to import backend.main.app: {import_error}")
                import traceback
                _startup_log(f"Backend thread: Traceback: {traceback.format_exc()}")
                return
            
            _startup_log(f"Backend thread: Starting uvicorn server on port {port}")
            
            config = uvicorn.Config(
                app=app,
                host="127.0.0.1",
                port=port,
                log_level="error",
                access_log=False
            )
            server = uvicorn.Server(config)
            _startup_log("Backend thread: Uvicorn config created, calling server.run()")
            server.run()
        except Exception as e:
            _startup_log(f"Backend thread error: {e}")
            import traceback
            _startup_log(f"Backend thread traceback: {traceback.format_exc()}")
            print(f"Backend error: {e}")
    
    _startup_log("Creating backend thread")
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    _startup_log(f"Backend thread started, waiting for port {port} to open")
    
    # Wait up to 60 seconds
    for i in range(120):  # 120 * 0.5 = 60 seconds
        time.sleep(0.5)
        
        if is_port_in_use(port):
            _startup_log(f"✓ Backend is responding on port {port} after {(i+1)*0.5:.1f}s")
            print(f"✓ Backend started on port {port} in {(i+1)*0.5:.1f}s")
            return True
        
        # Progress indicator every 5 seconds
        if (i+1) % 10 == 0:
            elapsed = (i+1) * 0.5
            _startup_log(f"Still waiting for backend... ({elapsed:.1f}s)")
    
    _startup_log(f"⚠ Backend thread started but port {port} not responding after 60s - continuing anyway")
    print("⚠ Warning: Backend may not have started properly")
    return False


def start_backend_subprocess():
    """Start backend as subprocess (for running from source)."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(current_dir, 'venv', 'Scripts', 'pythonw.exe')
    
    try:
        if sys.platform == 'win32':
            DETACHED_PROCESS = 0x00000008
            CREATE_NO_WINDOW = 0x08000000
            
            subprocess.Popen(
                [venv_python, '-m', 'uvicorn', 'backend.main:app', '--host', '0.0.0.0', '--port', '8765'],
                cwd=current_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW
            )
        else:
            subprocess.Popen(
                [venv_python, '-m', 'uvicorn', 'backend.main:app', '--host', '0.0.0.0', '--port', '8765'],
                cwd=current_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
        
        _startup_log("Starting backend process")
        
        for i in range(20):
            time.sleep(0.5)
            if is_port_in_use(8765):
                _startup_log("Backend port is open")
                return True
        
        return True
        
    except Exception as e:
        _startup_log(f"Failed to start backend: {e}")
        return False


def start_backend_silent():
    """Start backend server silently in background."""
    if is_port_in_use(8765):
        _startup_log("Backend already running")
        return True
    
    if getattr(sys, 'frozen', False):
        _startup_log("Running as frozen exe - starting backend in thread")
        return start_backend_threaded()
    else:
        _startup_log("Running from source - starting backend as subprocess")
        return start_backend_subprocess()


def launch_gui():
    """Launch the GUI application."""
    try:
        _startup_log("Launching GUI")
        
        from app.launcher import main
        main()
    except Exception as e:
        _startup_log(f"Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            
            from PyQt5.QtGui import QPalette, QColor
            from PyQt5.QtCore import Qt
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(20, 20, 20))
            palette.setColor(QPalette.WindowText, Qt.white)
            app.setPalette(palette)
            
            QMessageBox.critical(
                None,
                "MovieFlix Error",
                f"Failed to launch application:\n\n{str(e)}"
            )
        except:
            pass


if __name__ == "__main__":
    _startup_log("="*50)
    _startup_log("MovieFlix starting")
    _startup_log(f"Python: {sys.version}")
    _startup_log(f"Frozen: {getattr(sys, 'frozen', False)}")
    _startup_log(f"Executable: {sys.executable}")
    
    # Change to correct directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
        _startup_log(f"Changed directory to: {os.getcwd()}")
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        _startup_log(f"Running from source, directory: {os.getcwd()}")
    
    _startup_log("Starting backend server...")
    print("Starting MovieFlix...")
    print("Starting backend server...")
    
    backend_started = start_backend_silent()
    
    if not backend_started:
        _startup_log("⚠ Backend failed to start properly!")
        print("⚠ Warning: Backend may not have started")
        print("Check movieflix_startup.log for details")
        
        # Show error dialog
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Backend Error",
                "The MovieFlix backend server failed to start.\n\n"
                "This is likely a temporary issue.\n\n"
                "Solutions:\n"
                "1. Close and restart MovieFlix\n"
                "2. Check movieflix_startup.log for details\n"
                "3. Make sure no firewall is blocking port 8765\n"
                "4. Check Windows Firewall settings"
            )
            sys.exit(1)
        except Exception as e:
            _startup_log(f"Failed to show error dialog: {e}")
            sys.exit(1)
    
    _startup_log("✓ Backend started successfully")
    print("✓ Backend started")
    
    # Extra delay to ensure backend is fully ready
    time.sleep(1)
    
    print("Launching GUI...")
    launch_gui()