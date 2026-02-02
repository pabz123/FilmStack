"""
Scan Progress Dialog
Shows progress while scanning for movies/series
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


class ScanWorker(QThread):
    """Background thread for scanning files"""
    progress = pyqtSignal(str, int)  # (current_path, total_found)
    finished = pyqtSignal(dict)  # {movies: [], series: []}
    error = pyqtSignal(str)
    
    def __init__(self, scan_type='library'):
        super().__init__()
        self.scan_type = scan_type  # 'library' or 'full_pc'
        self.library_path = None
        
    def run(self):
        """Run the scan"""
        try:
            if self.scan_type == 'full_pc':
                from backend.scanner import scan_entire_pc
                
                def progress_callback(path, count):
                    self.progress.emit(path, count)
                
                results = scan_entire_pc(progress_callback)
                self.finished.emit(results)
            else:
                # Library scan
                from backend.scanner import scan_movies, scan_series
                import os
                
                base_path = self.library_path or os.path.join(os.getcwd(), 'library')
                
                self.progress.emit("Scanning movies...", 0)
                movies = scan_movies(os.path.join(base_path, 'movies'))
                
                self.progress.emit("Scanning series...", len(movies))
                series = scan_series(os.path.join(base_path, 'series'))
                
                self.finished.emit({
                    'movies': movies,
                    'series': series
                })
                
        except Exception as e:
            self.error.emit(str(e))


class ScanProgressDialog(QDialog):
    """Dialog showing scan progress"""
    
    scan_complete = pyqtSignal(dict)  # Emits results when done
    
    def __init__(self, scan_type='library', parent=None):
        super().__init__(parent)
        self.scan_type = scan_type
        self.results = None
        
        self.setWindowTitle("Scanning for Movies & Series")
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
        title = QLabel("Scanning Your Computer")
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        layout.addWidget(title)
        
        # Description
        if self.scan_type == 'full_pc':
            desc = QLabel("Scanning all drives for movies and TV series.\nThis may take a few minutes...")
        else:
            desc = QLabel("Scanning library folder for new content...")
        
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
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Preparing to scan...")
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            padding: 10px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
        """)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Found count
        self.found_label = QLabel("Found: 0 items")
        self.found_label.setStyleSheet("""
            color: #46d369;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
        """)
        layout.addWidget(self.found_label)
        
        # Log area (collapsible)
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
        
        log_title = QLabel("Scan Log:")
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
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedWidth(120)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_scan)
        button_layout.addWidget(self.cancel_btn)
        
        self.done_btn = QPushButton("Add to Library")
        self.done_btn.setFixedWidth(150)
        self.done_btn.setStyleSheet("""
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
        self.done_btn.clicked.connect(self.finish_scan)
        self.done_btn.setEnabled(False)
        button_layout.addWidget(self.done_btn)
        
        layout.addLayout(button_layout)
        
        # Set dark background
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
        """)
    
    def start_scan(self):
        """Start the scanning process"""
        self.worker = ScanWorker(self.scan_type)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
        self.status_label.setText("Scanning in progress...")
        self.log_text.append("Starting scan...")
    
    def on_progress(self, path, count):
        """Update progress"""
        # Truncate path if too long
        if len(path) > 60:
            display_path = "..." + path[-57:]
        else:
            display_path = path
        
        self.status_label.setText(f"Scanning: {display_path}")
        self.found_label.setText(f"Found: {count} items")
        
        # Add to log (only show every 10th to avoid spam)
        if count % 10 == 0:
            self.log_text.append(f"[{count}] {display_path}")
            # Auto-scroll to bottom
            self.log_text.verticalScrollBar().setValue(
                self.log_text.verticalScrollBar().maximum()
            )
    
    def on_finished(self, results):
        """Scan completed"""
        self.results = results
        movies_count = len(results.get('movies', []))
        series_count = len(results.get('series', []))
        
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        self.status_label.setText("✓ Scan complete!")
        self.status_label.setStyleSheet("""
            color: #46d369;
            font-size: 13px;
            padding: 10px;
            background-color: rgba(70, 211, 105, 0.1);
            border-radius: 5px;
            font-weight: bold;
        """)
        
        self.found_label.setText(
            f"Found: {movies_count} movies • {series_count} series"
        )
        
        self.log_text.append(f"\n✓ Scan complete!")
        self.log_text.append(f"  Movies: {movies_count}")
        self.log_text.append(f"  Series: {series_count}")
        
        self.cancel_btn.setText("Close")
        self.done_btn.setEnabled(True)
    
    def on_error(self, error_msg):
        """Handle scan error"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
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
        
        self.cancel_btn.setText("Close")
    
    def cancel_scan(self):
        """Cancel the scan"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        self.reject()
    
    def finish_scan(self):
        """Finish and emit results"""
        if self.results:
            self.scan_complete.emit(self.results)
        self.accept()
