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
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        
        log_path = os.path.join(current_dir, "movieflix_startup.log")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def start_backend_threaded():
    """Start backend in a background thread (for frozen exe)."""
    def run_backend():
        try:
            import uvicorn
            from backend.main import app
            
            _startup_log("Backend thread starting uvicorn server")
            
            config = uvicorn.Config(
                app=app,
                host="0.0.0.0",
                port=8765,
                log_level="error",
                access_log=False
            )
            server = uvicorn.Server(config)
            server.run()
        except Exception as e:
            _startup_log(f"Backend thread error: {e}")
            print(f"Backend error: {e}")
    
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    _startup_log("Backend started in background thread")
    
    # Wait up to 60 seconds
    for i in range(120):  # 120 * 0.5 = 60 seconds
        time.sleep(0.5)
        
        if is_port_in_use(8765):
            _startup_log(f"Backend is responding on port 8765 after {(i+1)*0.5:.1f}s")
            return True
    
    _startup_log("Backend thread started but port 8765 not responding after 60s - continuing")
    return True  # Continue anyway


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
    
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if start_backend_silent():
        # Extra delay to ensure backend is fully ready
        time.sleep(2)
        launch_gui()
    else:
        _startup_log("Failed to start backend - exiting")
        
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "MovieFlix Error", "Failed to start backend server.")
        except:
            pass
        
        sys.exit(1)