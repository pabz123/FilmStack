"""
MovieFlix Configuration
========================
Central configuration for all file paths.
All paths are relative to the application directory.
Works in both frozen (exe) and development modes.
Includes dynamic port allocation to avoid conflicts.
"""

import os
import sys
import socket
from pathlib import Path


def get_app_dir():
    """
    Get the application base directory.
    Works for both frozen (PyInstaller) and development mode.
    
    Returns:
        Path: Application base directory
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return Path(sys._MEIPASS).parent
    else:
        # Running from source
        return Path(__file__).parent.parent


def get_data_dir():
    """
    Get the data directory where database and library are stored.
    In frozen mode, this is next to the exe.
    In dev mode, this is the project root.
    
    Returns:
        Path: Data directory path
    """
    if getattr(sys, 'frozen', False):
        # Frozen: use directory where exe is located
        exe_dir = Path(sys.executable).parent
        return exe_dir
    else:
        # Development: use project root
        return get_app_dir()


def ensure_dir_exists(path):
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        path: Path to directory
        
    Returns:
        Path: The directory path
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


# Application directories
APP_DIR = get_app_dir()
DATA_DIR = get_data_dir()

# Database configuration
DATABASE_PATH = DATA_DIR / "movies.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Library directory (where movies/series are stored)
LIBRARY_DIR = ensure_dir_exists(DATA_DIR / "library")

# Backend directory
BACKEND_DIR = DATA_DIR / "backend"

# Environment file
ENV_FILE = DATA_DIR / ".env"

# Logs
LOG_DIR = ensure_dir_exists(DATA_DIR / "logs")
STARTUP_LOG = LOG_DIR / "movieflix_startup.log"
BACKEND_LOG = LOG_DIR / "backend_error.log"

# Port configuration
PORT_FILE = DATA_DIR / ".movieflix_port"
DEFAULT_PORT = 8765
PORT_RANGE_START = 8765
PORT_RANGE_END = 8865  # Try 100 ports


def find_free_port(start_port=PORT_RANGE_START, end_port=PORT_RANGE_END):
    """
    Find a free port in the given range.
    
    Args:
        start_port: Starting port number
        end_port: Ending port number
        
    Returns:
        int: Free port number, or None if none found
    """
    for port in range(start_port, end_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None


def get_backend_port():
    """
    Get the backend port to use.
    First tries to read from port file, then finds a free port.
    Saves the port to file for frontend to use.
    
    Returns:
        int: Port number to use
    """
    # Try to read existing port from file
    if PORT_FILE.exists():
        try:
            port = int(PORT_FILE.read_text().strip())
            # Verify port is still free
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    # Port is free, use it
                    return port
            except OSError:
                # Port in use, find new one
                pass
        except (ValueError, OSError):
            pass
    
    # Find a free port
    port = find_free_port()
    if port is None:
        # Fallback to default and hope for the best
        port = DEFAULT_PORT
    
    # Save port to file
    try:
        PORT_FILE.write_text(str(port))
    except OSError:
        pass
    
    return port


# Backend port (dynamically allocated)
BACKEND_PORT = get_backend_port()
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"

# Print paths for debugging
if __name__ == "__main__":
    print("MovieFlix Configuration")
    print("=" * 50)
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    print(f"APP_DIR: {APP_DIR}")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"DATABASE_PATH: {DATABASE_PATH}")
    print(f"LIBRARY_DIR: {LIBRARY_DIR}")
    print(f"LOG_DIR: {LOG_DIR}")
    print(f"BACKEND_PORT: {BACKEND_PORT}")
    print(f"BACKEND_URL: {BACKEND_URL}")
