"""
Movie/Series Info Dialog
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QWidget, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import requests


class MovieInfoDialog(QDialog):
    """Detailed movie/series information dialog"""
    
    play_clicked = pyqtSignal(object)
    
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        
        self.setWindowTitle("Details")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #181818;
            }
            QLabel {
                color: white;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Header with poster and basic info
        header = QHBoxLayout()
        
        # Poster
        poster_label = QLabel()
        poster_label.setFixedSize(200, 300)
        poster_label.setAlignment(Qt.AlignCenter)
        poster_label.setStyleSheet("background-color: #2a2a2a; border-radius: 8px;")
        
        if item_data.get('poster'):
            try:
                response = requests.get(
                    f"https://image.tmdb.org/t/p/w500{item_data['poster']}",
                    timeout=10
                )
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    poster_label.setPixmap(pixmap.scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except:
                poster_label.setText("No Poster")
        else:
            poster_label.setText("No Poster")
        
        header.addWidget(poster_label)
        header.addSpacing(30)
        
        # Info section
        info_layout = QVBoxLayout()
        
        # Title
        title = QLabel(item_data.get('title', 'Unknown'))
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        title.setWordWrap(True)
        info_layout.addWidget(title)
        
        # Meta info
        meta_parts = []
        if item_data.get('rating'):
            meta_parts.append(f"⭐ {item_data['rating']:.1f}/10")
        if item_data.get('watched'):
            meta_parts.append("✓ Watched")
        
        if meta_parts:
            meta = QLabel(" • ".join(meta_parts))
            meta.setStyleSheet("font-size: 16px; color: #46d369; font-weight: bold;")
            info_layout.addWidget(meta)
        
        info_layout.addSpacing(15)
        
        # Overview
        if item_data.get('overview'):
            overview_label = QLabel("Overview")
            overview_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e5e5e5;")
            info_layout.addWidget(overview_label)
            
            overview = QLabel(item_data['overview'])
            overview.setWordWrap(True)
            overview.setStyleSheet("font-size: 14px; color: #b3b3b3; line-height: 1.6;")
            info_layout.addWidget(overview)
        
        info_layout.addSpacing(15)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        play_btn = QPushButton("▶  Play Now")
        play_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: none;
                border-radius: 4px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.85);
            }
        """)
        play_btn.setCursor(Qt.PointingHandCursor)
        play_btn.clicked.connect(self._on_play)
        button_layout.addWidget(play_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(109, 109, 110, 0.7);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(109, 109, 110, 0.9);
            }
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        info_layout.addLayout(button_layout)
        
        info_layout.addStretch()
        header.addLayout(info_layout)
        
        content_layout.addLayout(header)
        
        # Additional info
        if item_data.get('path'):
            path_label = QLabel(f"File: {item_data['path']}")
            path_label.setStyleSheet("font-size: 11px; color: #666;")
            path_label.setWordWrap(True)
            content_layout.addWidget(path_label)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _on_play(self):
        """Emit play signal and close"""
        self.play_clicked.emit(self.item_data)
        self.close()
