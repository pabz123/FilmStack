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


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except OSError:
            return True


def start_backend_silent():
    """Start backend server silently in background."""
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(current_dir, 'venv', 'Scripts', 'pythonw.exe')  # Use pythonw.exe for no console
    
    # Check if backend is already running
    if is_port_in_use(8765):
        print("Backend already running on port 8765")
        _startup_log("Backend already running")
        return True
    
    # Start backend as detached process (no console window)
    try:
        # Use CREATE_NO_WINDOW flag on Windows to hide console
        if sys.platform == 'win32':
            DETACHED_PROCESS = 0x00000008
            CREATE_NO_WINDOW = 0x08000000
            
            # Use uvicorn module to start backend properly
            subprocess.Popen(
                [venv_python, '-m', 'uvicorn', 'backend.main:app', '--host', '0.0.0.0', '--port', '8765'],
                cwd=current_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW
            )
        else:
            # Unix-like systems
            subprocess.Popen(
                [venv_python, '-m', 'uvicorn', 'backend.main:app', '--host', '0.0.0.0', '--port', '8765'],
                cwd=current_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
        
        print("Starting backend...")
        _startup_log("Starting backend process")
        
        # Wait for backend to be ready (max 5 seconds with faster checks)
        for i in range(10):
            time.sleep(0.5)
            if is_port_in_use(8765):
                print(f"Backend ready in {(i+1)*0.5:.1f} seconds!")
                _startup_log("Backend port is open")
                return True
        
        # Backend not responding yet, but continue anyway
        print("Backend started but not responding yet - continuing...")
        return True
        
    except Exception as e:
        print(f"Failed to start backend: {e}")
        _startup_log(f"Failed to start backend: {e}")
        return False


def _startup_log(message: str) -> None:
    """Write startup diagnostics to a log file (useful for pythonw/.exe runs)."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(current_dir, "movieflix_startup.log")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def launch_gui():
    """Launch the GUI application."""
    try:
        # Keep this short; backend readiness is already checked in start_backend_silent().
        print("Waiting for backend to be ready...")
        time.sleep(0.2)
        _startup_log("Launching GUI")
        
        # Import and run the launcher (now goes directly to login)
        from app.launcher import main
        main()
    except Exception as e:
        print(f"Failed to launch GUI: {e}")
        _startup_log(f"Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error dialog
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            
            # Set dark theme to avoid white flash
            from PyQt5.QtGui import QPalette, QColor
            from PyQt5.QtCore import Qt
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(20, 20, 20))
            palette.setColor(QPalette.WindowText, Qt.white)
            app.setPalette(palette)
            
            QMessageBox.critical(
                None,
                "MovieFlix Error",
                f"Failed to launch application:\n\n{str(e)}\n\nCheck that all dependencies are installed."
            )
        except:
            pass


if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if backend is already running
    if is_port_in_use(8765):
        print("Backend already running, skipping backend start")
        _startup_log("Backend already running, launching GUI")
        # Launch GUI directly
        launch_gui()
    else:
        # Start backend silently
        if start_backend_silent():
            # Launch GUI
            launch_gui()
        else:
            print("Failed to start backend. Exiting.")
            _startup_log("Failed to start backend")
            sys.exit(1)
