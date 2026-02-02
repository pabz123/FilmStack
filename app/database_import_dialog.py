"""
Database Import Progress Dialog
Shows progress while adding scanned content to database
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QProgressBar, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import requests


class DatabaseImportWorker(QThread):
    """Background thread for adding content to database"""
    progress = pyqtSignal(str, int, int)  # (message, current, total)
    finished = pyqtSignal(dict)  # {added, skipped, errors}
    error = pyqtSignal(str)
    
    def __init__(self, movies, series, api_url, fetch_metadata=True):
        super().__init__()
        self.movies = movies
        self.series = series
        self.api_url = api_url
        self.fetch_metadata = fetch_metadata
        
    def run(self):
        """Run the import process"""
        try:
            total_items = len(self.movies) + len(self.series)
            current = 0
            
            movies_added = 0
            series_added = 0
            episodes_added = 0
            skipped = 0
            errors = 0
            
            # Import movies
            if self.movies:
                self.progress.emit(f"Adding {len(self.movies)} movies...", current, total_items)
                
                try:
                    response = requests.post(
                        f"{self.api_url}/movies/bulk_add",
                        json=self.movies,
                        params={'fetch_metadata': self.fetch_metadata},
                        timeout=300  # 5 minutes for large batches
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        movies_added = result.get('added', 0)
                        skipped += result.get('skipped', 0)
                        
                        for i in range(len(self.movies)):
                            current += 1
                            if i % 5 == 0:  # Update every 5 movies
                                self.progress.emit(
                                    f"Added movie: {self.movies[i].get('title', 'Unknown')[:40]}...",
                                    current,
                                    total_items
                                )
                    else:
                        errors += len(self.movies)
                        self.progress.emit(f"Error adding movies: {response.status_code}", current, total_items)
                        
                except Exception as e:
                    errors += len(self.movies)
                    self.progress.emit(f"Error adding movies: {str(e)}", current, total_items)
            
            # Import series
            if self.series:
                self.progress.emit(f"Adding {len(self.series)} series...", current, total_items)
                
                try:
                    response = requests.post(
                        f"{self.api_url}/series/bulk_add",
                        json=self.series,
                        params={'fetch_metadata': self.fetch_metadata},
                        timeout=300
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        series_added = result.get('added', 0)
                        episodes_added = result.get('episodes_added', 0)
                        skipped += result.get('skipped', 0)
                        
                        for i in range(len(self.series)):
                            current += 1
                            if i % 3 == 0:  # Update every 3 series
                                first_ep = self.series[i][0] if self.series[i] else {}
                                series_title = first_ep.get('series_title', 'Unknown')
                                self.progress.emit(
                                    f"Added series: {series_title[:40]}...",
                                    current,
                                    total_items
                                )
                    else:
                        errors += len(self.series)
                        self.progress.emit(f"Error adding series: {response.status_code}", current, total_items)
                        
                except Exception as e:
                    errors += len(self.series)
                    self.progress.emit(f"Error adding series: {str(e)}", current, total_items)
            
            # Emit final results
            self.finished.emit({
                'movies_added': movies_added,
                'series_added': series_added,
                'episodes_added': episodes_added,
                'skipped': skipped,
                'errors': errors
            })
            
        except Exception as e:
            self.error.emit(str(e))


class DatabaseImportDialog(QDialog):
    """Dialog showing database import progress"""
    
    import_complete = pyqtSignal(dict)
    
    def __init__(self, movies, series, api_url, parent=None):
        super().__init__(parent)
        self.movies = movies
        self.series = series
        self.api_url = api_url
        
        self.setWindowTitle("Adding to Library")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Adding Content to Library")
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        layout.addWidget(title)
        
        # Description
        total = len(self.movies) + len(self.series)
        desc = QLabel(f"Adding {len(self.movies)} movies and {len(self.series)} series to your library.\nFetching metadata from TMDB...")
        desc.setStyleSheet("color: #999; font-size: 14px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2a2a2a;
                border: none;
                border-radius: 5px;
                height: 30px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #e50914;
                border-radius: 5px;
            }
        """)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Preparing to add content...")
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            padding: 10px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
        """)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Stats
        self.stats_label = QLabel("Added: 0 movies, 0 series")
        self.stats_label.setStyleSheet("""
            color: #46d369;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
        """)
        layout.addWidget(self.stats_label)
        
        # Log area
        log_frame = QFrame()
        log_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """)
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(10, 10, 10, 10)
        
        log_title = QLabel("Import Log:")
        log_title.setStyleSheet("color: #999; font-size: 12px;")
        log_layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #666;
                border: none;
                font-size: 11px;
                font-family: 'Courier New', monospace;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_frame)
        
        layout.addStretch()
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedWidth(120)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f40612;
            }
            QPushButton:disabled {
                background-color: #333;
                color: #666;
            }
        """)
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setEnabled(False)
        layout.addWidget(self.close_btn, alignment=Qt.AlignRight)
        
        # Set dark background
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
        """)
    
    def start_import(self, fetch_metadata=True):
        """Start the import process"""
        self.worker = DatabaseImportWorker(
            self.movies,
            self.series,
            self.api_url,
            fetch_metadata
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
        self.log_text.append("Starting import...")
        self.log_text.append(f"Movies to add: {len(self.movies)}")
        self.log_text.append(f"Series to add: {len(self.series)}")
        self.log_text.append("")
    
    def on_progress(self, message, current, total):
        """Update progress"""
        self.status_label.setText(message)
        self.progress_bar.setValue(current)
        
        # Add to log
        self.log_text.append(f"[{current}/{total}] {message}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def on_finished(self, results):
        """Import completed"""
        movies_added = results.get('movies_added', 0)
        series_added = results.get('series_added', 0)
        episodes_added = results.get('episodes_added', 0)
        skipped = results.get('skipped', 0)
        errors = results.get('errors', 0)
        
        self.progress_bar.setValue(self.progress_bar.maximum())
        
        self.status_label.setText("✓ Import complete!")
        self.status_label.setStyleSheet("""
            color: #46d369;
            font-size: 13px;
            padding: 10px;
            background-color: rgba(70, 211, 105, 0.1);
            border-radius: 5px;
            font-weight: bold;
        """)
        
        self.stats_label.setText(
            f"✓ Added: {movies_added} movies, {series_added} series ({episodes_added} episodes)\n"
            f"Skipped: {skipped} (already in library) | Errors: {errors}"
        )
        
        self.log_text.append("")
        self.log_text.append("=" * 50)
        self.log_text.append("✓ Import complete!")
        self.log_text.append(f"  Movies added: {movies_added}")
        self.log_text.append(f"  Series added: {series_added}")
        self.log_text.append(f"  Episodes added: {episodes_added}")
        self.log_text.append(f"  Skipped (duplicates): {skipped}")
        self.log_text.append(f"  Errors: {errors}")
        self.log_text.append("=" * 50)
        
        self.close_btn.setEnabled(True)
        
        self.import_complete.emit(results)
    
    def on_error(self, error_msg):
        """Handle import error"""
        self.status_label.setText(f"✗ Error: {error_msg}")
        self.status_label.setStyleSheet("""
            color: #e50914;
            font-size: 13px;
            padding: 10px;
            background-color: rgba(229, 9, 20, 0.1);
            border-radius: 5px;
            font-weight: bold;
        """)
        
        self.log_text.append(f"\n✗ Error: {error_msg}")
        
        self.close_btn.setEnabled(True)
