"""
Auto-Scanner Module for MovieFlix
==================================

Automatically scans the entire PC for movies and series in the background.
Runs on startup and notifies users when new content is found.

Features:
- Background scanning (non-blocking)
- Smart duplicate detection
- System notifications
- Optional import dialog for new content
"""

import sys
import requests
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox
from backend.scanner import scan_entire_pc


class BackgroundScanWorker(QThread):
    """
    Background worker that scans the entire PC for media files.
    Runs silently without UI and only reports when done.
    """
    
    scan_complete = pyqtSignal(dict)  # Emits scan results
    scan_error = pyqtSignal(str)  # Emits error message
    
    def __init__(self, api_url="http://localhost:8765"):
        super().__init__()
        self.api_url = api_url
        self.is_cancelled = False
    
    def run(self):
        """Run the background scan"""
        try:
            # Scan the entire PC
            results = scan_entire_pc(progress_callback=None)  # Silent scan
            
            if self.is_cancelled:
                return
            
            # Get current library content to detect new items
            existing_movies = self._get_existing_movies()
            existing_series = self._get_existing_series()
            
            # Filter out items already in library
            new_movies = self._filter_new_items(results['movies'], existing_movies)
            new_series = self._filter_new_series(results['series'], existing_series)
            
            # Emit results
            scan_results = {
                'total_movies': len(results['movies']),
                'total_series': len(results['series']),
                'new_movies': new_movies,
                'new_series': new_series,
                'new_count': len(new_movies) + len(new_series)
            }
            
            self.scan_complete.emit(scan_results)
            
        except Exception as e:
            self.scan_error.emit(f"Background scan error: {str(e)}")
    
    def _get_existing_movies(self):
        """Get list of movies already in library"""
        try:
            response = requests.get(f"{self.api_url}/movies", timeout=5)
            if response.status_code == 200:
                movies = response.json()
                return {movie['path'] for movie in movies}
        except:
            pass
        return set()
    
    def _get_existing_series(self):
        """Get list of series already in library"""
        try:
            response = requests.get(f"{self.api_url}/series", timeout=5)
            if response.status_code == 200:
                series = response.json()
                # Collect all episode paths
                paths = set()
                for show in series:
                    for season in show.get('seasons', []):
                        for episode in season.get('episodes', []):
                            paths.add(episode['path'])
                return paths
        except:
            pass
        return set()
    
    def _filter_new_items(self, items, existing_paths):
        """Filter items to only include new ones not in library"""
        return [item for item in items if item['path'] not in existing_paths]
    
    def _filter_new_series(self, series_list, existing_paths):
        """Filter series to only include episodes not in library"""
        new_series = []
        for episodes in series_list:
            new_episodes = [ep for ep in episodes if ep['path'] not in existing_paths]
            if new_episodes:
                new_series.append(new_episodes)
        return new_series
    
    def cancel(self):
        """Cancel the scan"""
        self.is_cancelled = True


class AutoScanManager:
    """
    Manages automatic background scanning.
    Coordinates scan timing, notifications, and import dialogs.
    """
    
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.scan_worker = None
        # Get dynamic API URL
        try:
            from backend.config import BACKEND_URL
            self.api_url = BACKEND_URL
        except ImportError:
            self.api_url = "http://localhost:8765"
    
    def start_background_scan(self):
        """Start background scan with user permission"""
        from PyQt5.QtWidgets import QMessageBox
        
        # Ask user for permission first
        reply = QMessageBox.question(
            self.parent_window,
            "Scan Entire PC?",
            "Do you want to scan your entire PC for movies and series?\n\n"
            "This will:\n"
            "• Search all drives for video files\n"
            "• Take several minutes depending on your PC\n"
            "• Find content outside the library folder\n\n"
            "Alternatively, you can add files to the library folder\n"
            "and use 'Scan Library' for faster results.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            print("User declined full PC scan")
            return
        
        print("User approved PC scan - starting...")
        self._start_scan_worker()
    
    def _start_scan_worker(self):
        """Actually start the scan worker (internal method)"""
        # Delay scan by 3 seconds to let UI fully load
        QTimer.singleShot(3000, self._run_scan)
    
    def _run_scan(self):
        """Execute the background scan"""
        # Don't start if already scanning
        if self.scan_worker and self.scan_worker.isRunning():
            return
        
        # Create and start worker
        self.scan_worker = BackgroundScanWorker(self.api_url)
        self.scan_worker.scan_complete.connect(self._on_scan_complete)
        self.scan_worker.scan_error.connect(self._on_scan_error)
        self.scan_worker.start()
        
        print("🔍 Background scan started...")
        print("   Scanning: All drives (C:, D:, E:, external drives)")
        print("   Looking for: Movies and TV series")
        print("   This may take 2-5 minutes...")
    
    def _on_scan_complete(self, results):
        """Handle scan completion"""
        try:
            total_found = results['total_movies'] + results['total_series']
            new_count = results['new_count']
            
            print(f"✓ Background scan complete! Found {total_found} items ({new_count} new)")
            
            if new_count > 0:
                # New content found - ask user if they want to import
                print(f"New content details: {len(results['new_movies'])} movies, {len(results['new_series'])} series")
                self._show_import_dialog(results)
            else:
                # No new content - just notify
                self._show_no_new_content_notification(total_found)
                
        except Exception as e:
            print(f"❌ CRITICAL ERROR in scan completion: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_scan_error(self, error_message):
        """Handle scan errors"""
        print(f"❌ Background scan error: {error_message}")
    
    def _show_import_dialog(self, results):
        """Show detailed dialog with file locations before importing"""
        try:
            new_movies = results['new_movies']
            new_series = results['new_series']
            
            # Create a custom dialog with details
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
            
            dialog = QDialog(self.parent)
            dialog.setWindowTitle("New Content Detected")
            dialog.setMinimumSize(700, 500)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #141414;
                }
                QLabel {
                    color: white;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: white;
                    border: 1px solid #333;
                    padding: 10px;
                    font-family: Consolas, monospace;
                    font-size: 11px;
                }
                QPushButton {
                    background-color: #e50914;
                    color: white;
                    border: none;
                    padding: 10px 30px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #f40612;
                }
                QPushButton#cancelBtn {
                    background-color: #333;
                }
                QPushButton#cancelBtn:hover {
                    background-color: #444;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(30, 30, 30, 30)
            
            # Title
            title = QLabel("🎬 New Media Files Detected!")
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e50914;")
            layout.addWidget(title)
            
            # Summary
            summary = QLabel(
                f"The background scan found new content on your computer:\n\n"
                f"📽️  {len(new_movies)} new movie{'s' if len(new_movies) != 1 else ''}\n"
                f"📺  {len(new_series)} new series"
            )
            summary.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
            layout.addWidget(summary)
            
            # Location details label
            details_label = QLabel("📂 File Locations:")
            details_label.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 10px;")
            layout.addWidget(details_label)
            
            # Details text box
            details_text = QTextEdit()
            details_text.setReadOnly(True)
            
            # Build details content
            content = ""
            
            if new_movies:
                content += "=== MOVIES ===\n\n"
                for i, movie in enumerate(new_movies[:20], 1):  # Show first 20
                    content += f"{i}. {movie['title']}\n"
                    content += f"   📁 {movie['path']}\n\n"
                if len(new_movies) > 20:
                    content += f"... and {len(new_movies) - 20} more movies\n\n"
            
            if new_series:
                content += "\n=== TV SERIES ===\n\n"
                shown_series = 0
                for episodes in new_series[:10]:  # Show first 10 series
                    if episodes:
                        series_title = episodes[0].get('title', 'Unknown')
                        content += f"{shown_series + 1}. {series_title} ({len(episodes)} episodes)\n"
                        # Show first episode location as example
                        content += f"   📁 {episodes[0]['path']}\n\n"
                        shown_series += 1
                if len(new_series) > 10:
                    content += f"... and {len(new_series) - 10} more series\n"
            
            details_text.setPlainText(content)
            layout.addWidget(details_text)
            
            # Question
            question = QLabel("Would you like to add this content to your MovieFlix library?")
            question.setStyleSheet("font-size: 13px; margin-top: 10px;")
            layout.addWidget(question)
            
            # Buttons
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            cancel_btn = QPushButton("No, Thanks")
            cancel_btn.setObjectName("cancelBtn")
            cancel_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_btn)
            
            import_btn = QPushButton("Yes, Add to Library")
            import_btn.clicked.connect(dialog.accept)
            import_btn.setDefault(True)
            button_layout.addWidget(import_btn)
            
            layout.addLayout(button_layout)
            
            # Show dialog
            if dialog.exec_() == QDialog.Accepted:
                # User wants to import
                self._start_import(results)
            else:
                print("User declined to import new content")
                
        except Exception as e:
            print(f"❌ Error showing import dialog: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_no_new_content_notification(self, total_found):
        """Show notification that scan found no new content"""
        try:
            message = f"Background scan complete!\n\n"
            message += f"Scanned {total_found} media files.\n"
            message += f"No new content to add."
            
            msg_box = QMessageBox(self.parent)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Scan Complete")
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            
            # Don't auto-close - let user dismiss it
            msg_box.exec_()
            
        except Exception as e:
            print(f"❌ Error showing notification: {e}")
    
    def _start_import(self, results):
        """Start the database import process"""
        try:
            from app.database_import_dialog import DatabaseImportDialog
            
            print(f"Preparing to import: {len(results['new_movies'])} movies, {len(results['new_series'])} series")
            
            # Get the data in the correct format
            movies = results['new_movies']
            series = results['new_series']
            
            # Open import dialog with correct parameters
            print("Opening import dialog...")
            dialog = DatabaseImportDialog(
                movies,
                series,
                self.api_url,
                self.parent
            )
            
            # Connect completion signal
            dialog.import_complete.connect(self._on_import_complete)
            
            # Start import with metadata fetching
            print("Starting import...")
            dialog.start_import(fetch_metadata=True)
            
            # Show dialog
            print("Showing import dialog...")
            dialog.exec_()
                
        except Exception as e:
            print(f"❌ CRITICAL ERROR starting import: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error to user
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self.parent,
                "Import Error",
                f"Failed to start import:\n\n{str(e)}\n\nPlease use Settings → Scan Entire Computer instead."
            )
    
    def _on_import_complete(self, results):
        """Handle import completion"""
        print("✓ Import complete!")
        print(f"  Movies added: {results.get('movies_added', 0)}")
        print(f"  Series added: {results.get('series_added', 0)}")
        print(f"  Episodes added: {results.get('episodes_added', 0)}")
        
        # Reload library
        if hasattr(self.parent, 'auto_load_content'):
            print("Reloading library...")
            self.parent.auto_load_content()
