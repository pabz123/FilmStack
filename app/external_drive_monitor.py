"""
External Drive Monitor for MovieFlix
====================================

Monitors external drives (USB, external HDD) and displays their content
as temporary cards without adding to database.

Features:
- Detects internal vs external drives
- Scans external drives for media
- Creates temporary virtual cards
- Auto-removes cards when drive disconnected
- Duplicate detection (vs library content)
"""

import os
import string
import platform
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from backend.scanner import scan_movies, scan_series, VIDEO_EXTENSIONS


def get_drive_type(drive_letter):
    """
    Determine if a drive is internal or external (Windows only).
    
    Args:
        drive_letter (str): Drive letter (e.g., 'C', 'D')
        
    Returns:
        str: 'internal' or 'external' or 'unknown'
    """
    if platform.system() != 'Windows':
        return 'unknown'
    
    try:
        import win32api
        import win32file
        
        drive = f"{drive_letter}:\\"
        drive_type = win32file.GetDriveType(drive)
        
        # Drive types:
        # 2 = DRIVE_REMOVABLE (USB, flash)
        # 3 = DRIVE_FIXED (internal HDD/SSD)
        # 5 = DRIVE_CDROM
        # 4 = DRIVE_REMOTE (network)
        
        if drive_type == 2:  # Removable (USB flash, external drives)
            print(f"🔍 {drive_letter}: detected as REMOVABLE → external")
            return 'external'
        elif drive_type == 3:  # Fixed
            # C: is always internal
            if drive_letter == 'C':
                return 'internal'
            # D: could be internal or external - for testing, treat as internal
            elif drive_letter == 'D':
                return 'internal'
            # E: and above are often external drives
            else:
                print(f"🔍 {drive_letter}: detected as FIXED (likely external HDD) → external")
                return 'external'
        elif drive_type == 5:  # CD-ROM
            print(f"🔍 {drive_letter}: detected as CDROM → ignored")
            return 'unknown'
        else:
            return 'unknown'
            
    except ImportError:
        # win32api not available, use simple heuristic
        # C: and D: are usually internal
        if drive_letter in ['C', 'D']:
            return 'internal'
        else:
            # E: and above are often external
            print(f"🔍 {drive_letter}: no win32api, assuming external")
            return 'external'
    except Exception as e:
        print(f"Error detecting drive type for {drive_letter}: {e}")
        return 'unknown'


def get_available_drives():
    """
    Get all available drives categorized by type.
    
    Returns:
        dict: {'internal': ['C', 'D'], 'external': ['E', 'F']}
    """
    drives = {'internal': [], 'external': []}
    
    if platform.system() == 'Windows':
        for letter in string.ascii_uppercase:
            drive_path = f"{letter}:\\"
            if os.path.exists(drive_path):
                drive_type = get_drive_type(letter)
                if drive_type == 'internal':
                    drives['internal'].append(letter)
                elif drive_type == 'external':
                    drives['external'].append(letter)
    
    return drives


class ExternalDriveScanner(QThread):
    """Scans external drives for media files"""
    
    scan_complete = pyqtSignal(dict)  # Emits {'drive': 'E', 'movies': [], 'series': []}
    
    def __init__(self, drive_letter):
        super().__init__()
        self.drive_letter = drive_letter
    
    def run(self):
        """Scan the external drive"""
        try:
            drive_path = f"{self.drive_letter}:\\"
            print(f"🔍 Scanning external drive {drive_path}...")
            
            movies = []
            series = []
            
            # Quick scan - just look for video files, don't organize too much
            for root, dirs, files in os.walk(drive_path):
                # Skip system folders
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['System Volume Information', '$RECYCLE.BIN']]
                
                for file in files:
                    if file.lower().endswith(VIDEO_EXTENSIONS):
                        full_path = os.path.join(root, file)
                        title = os.path.splitext(file)[0]
                        
                        # Simple detection: if has episode pattern, it's a series
                        if any(pattern in file.lower() for pattern in ['s01e', 's02e', 's03e', 's1e', 's2e', 's3e', 'episode', 'ep.']):
                            series.append({
                                'title': title,
                                'path': full_path,
                                'drive': self.drive_letter
                            })
                        else:
                            movies.append({
                                'title': title,
                                'path': full_path,
                                'drive': self.drive_letter
                            })
            
            print(f"✓ Found {len(movies)} movies, {len(series)} episodes on {drive_path}")
            
            self.scan_complete.emit({
                'drive': self.drive_letter,
                'movies': movies,
                'series': series
            })
            
        except Exception as e:
            print(f"Error scanning drive {self.drive_letter}: {e}")


class ExternalDriveMonitor(QThread):
    """Monitors external drives and detects connection/disconnection"""
    
    drive_added = pyqtSignal(str)  # Emits drive letter
    drive_removed = pyqtSignal(str)  # Emits drive letter
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.known_drives = set()
        
        # Get initial drives
        initial = get_available_drives()
        self.known_drives = set(initial['external'])
    
    def run(self):
        """Monitor drives every 3 seconds"""
        while self.running:
            self.check_drives()
            self.msleep(3000)  # Check every 3 seconds
    
    def check_drives(self):
        """Check for drive changes"""
        current = get_available_drives()
        current_external = set(current['external'])
        
        # Check for new drives
        new_drives = current_external - self.known_drives
        for drive in new_drives:
            print(f"✨ NEW external drive detected: {drive}:")
            self.drive_added.emit(drive)
        
        # Check for removed drives
        removed_drives = self.known_drives - current_external
        for drive in removed_drives:
            print(f"❌ External drive disconnected: {drive}:")
            self.drive_removed.emit(drive)
        
        self.known_drives = current_external
    
    def stop(self):
        """Stop monitoring"""
        self.running = False


class ExternalContentManager:
    """
    Manages external drive content display.
    Coordinates scanning and card creation/removal.
    """
    
    def __init__(self, parent_ui):
        self.parent = parent_ui
        self.external_content = {}  # {'E': {'movies': [], 'series': []}}
        self.monitor = None
        self.scanners = {}
    
    def start_monitoring(self):
        """Start monitoring external drives"""
        print("=" * 50)
        print("🔌 Starting External Drive Monitor")
        print("=" * 50)
        
        # Check initial drives
        drives = get_available_drives()
        print(f"📂 Internal drives: {', '.join(drives['internal']) or 'None'}")
        print(f"🔌 External drives: {', '.join(drives['external']) or 'None'}")
        
        # Start drive monitor
        self.monitor = ExternalDriveMonitor()
        self.monitor.drive_added.connect(self.on_drive_added)
        self.monitor.drive_removed.connect(self.on_drive_removed)
        self.monitor.start()
        
        print("✓ Monitor started - checking every 3 seconds")
        print("=" * 50)
        
        # Scan any external drives already connected
        if drives['external']:
            print(f"\n📁 Scanning {len(drives['external'])} existing external drive(s)...")
            for drive in drives['external']:
                print(f"  → Scanning {drive}:")
                self.scan_drive(drive)
        else:
            print("\n💡 No external drives detected yet")
            print("   Connect an external drive to see its content!")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if self.monitor:
            self.monitor.stop()
            self.monitor.wait()
    
    def scan_drive(self, drive_letter):
        """Scan an external drive"""
        scanner = ExternalDriveScanner(drive_letter)
        scanner.scan_complete.connect(self.on_scan_complete)
        scanner.start()
        self.scanners[drive_letter] = scanner
    
    def on_drive_added(self, drive_letter):
        """Handle new drive connected"""
        print(f"\n{'='*50}")
        print(f"✨ NEW DRIVE CONNECTED: {drive_letter}:")
        print(f"{'='*50}")
        self.scan_drive(drive_letter)
    
    def on_drive_removed(self, drive_letter):
        """Handle drive disconnected"""
        print(f"\n{'='*50}")
        print(f"❌ DRIVE DISCONNECTED: {drive_letter}:")
        print(f"{'='*50}")
        
        # Remove content for this drive
        if drive_letter in self.external_content:
            del self.external_content[drive_letter]
        
        # Notify parent to refresh UI
        if hasattr(self.parent, 'refresh_external_content'):
            self.parent.refresh_external_content()
    
    def on_scan_complete(self, results):
        """Handle scan completion"""
        drive = results['drive']
        self.external_content[drive] = {
            'movies': results['movies'],
            'series': results['series']
        }
        
        print(f"✓ External content from {drive}: available")
        
        # Notify parent to refresh UI
        if hasattr(self.parent, 'refresh_external_content'):
            self.parent.refresh_external_content()
    
    def cleanup_disconnected_drives(self):
        """Remove content from drives that are no longer connected"""
        print("🧹 Cleaning up disconnected drives...")
        
        # Get currently connected drives
        current_drives = get_available_drives()
        connected_external = set(current_drives['external'])
        
        # Find drives in our content that are no longer connected
        stored_drives = set(self.external_content.keys())
        disconnected = stored_drives - connected_external
        
        if disconnected:
            for drive in disconnected:
                print(f"❌ Removing content from disconnected drive: {drive}:")
                del self.external_content[drive]
            
            # Refresh UI to remove cards
            if hasattr(self.parent, 'refresh_external_content'):
                self.parent.refresh_external_content()
            
            print(f"✓ Cleaned up {len(disconnected)} disconnected drive(s)")
        else:
            print("✓ No disconnected drives to clean up")
    
    def get_all_external_content(self):
        """Get all external content across all drives"""
        # First, cleanup any disconnected drives
        self.cleanup_disconnected_drives()
        
        all_movies = []
        all_series = []
        
        for drive, content in self.external_content.items():
            all_movies.extend(content['movies'])
            all_series.extend(content['series'])
        
        return {'movies': all_movies, 'series': all_series}
    
    def is_duplicate(self, external_path, library_paths):
        """
        Check if external file is duplicate of library file.
        
        Args:
            external_path (str): Path to external file
            library_paths (set): Set of library file paths
            
        Returns:
            bool: True if duplicate
        """
        # Simple check: same filename
        external_name = os.path.basename(external_path).lower()
        
        for lib_path in library_paths:
            lib_name = os.path.basename(lib_path).lower()
            if external_name == lib_name:
                return True
        
        return False
