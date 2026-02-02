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
    delete_clicked = pyqtSignal(object)  # New signal for delete
    
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
        
        # Delete button
        delete_btn = QPushButton("🗑  Remove from Library")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(229, 9, 20, 0.8);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(229, 9, 20, 1);
            }
        """)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self._on_delete)
        button_layout.addWidget(delete_btn)
        
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
        
        # Cast section (fetch from TMDB if we have ID)
        if item_data.get('id'):
            self.add_cast_section(content_layout, item_data)
        
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
    
    def add_cast_section(self, layout, item_data):
        """Add cast and crew information section"""
        from backend.metadata import fetch_movie_cast, fetch_series_cast
        
        # Determine if it's a movie or series
        is_series = 'seasons' in item_data or item_data.get('type') == 'series'
        
        # Fetch cast (async in real app, but simplified here)
        cast_info = None
        try:
            # Try to get TMDB ID from database
            # For now, we'll use the item_data ID as TMDB ID
            # In production, you'd store tmdb_id separately
            if is_series:
                cast_info = fetch_series_cast(item_data['id'])
            else:
                cast_info = fetch_movie_cast(item_data['id'])
        except:
            pass
        
        if not cast_info:
            return
        
        # Cast section header
        cast_header = QLabel("Cast & Crew")
        cast_header.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-top: 20px;")
        layout.addWidget(cast_header)
        
        # Director/Creator info
        if not is_series and cast_info.get('director'):
            director_label = QLabel(f"Director: {cast_info['director']}")
            director_label.setStyleSheet("font-size: 14px; color: #b3b3b3; margin-top: 5px;")
            layout.addWidget(director_label)
        elif is_series and cast_info.get('creators'):
            creators_text = ", ".join(cast_info['creators'])
            creators_label = QLabel(f"Created by: {creators_text}")
            creators_label.setStyleSheet("font-size: 14px; color: #b3b3b3; margin-top: 5px;")
            layout.addWidget(creators_label)
        
        # Cast list (horizontal scroll)
        if cast_info.get('cast'):
            cast_container = QFrame()
            cast_container.setStyleSheet("background-color: transparent;")
            cast_layout = QHBoxLayout(cast_container)
            cast_layout.setSpacing(15)
            cast_layout.setContentsMargins(0, 10, 0, 10)
            
            for person in cast_info['cast'][:5]:  # Show top 5
                person_widget = self.create_cast_card(person)
                cast_layout.addWidget(person_widget)
            
            cast_layout.addStretch()
            layout.addWidget(cast_container)
    
    def create_cast_card(self, person):
        """Create a cast member card"""
        card = QFrame()
        card.setFixedSize(100, 150)
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(5, 5, 5, 5)
        card_layout.setSpacing(5)
        
        # Photo placeholder (or actual photo if available)
        photo_label = QLabel()
        photo_label.setFixedSize(90, 90)
        photo_label.setAlignment(Qt.AlignCenter)
        photo_label.setStyleSheet("""
            background-color: #2a2a2a;
            border-radius: 45px;
            font-size: 30px;
        """)
        
        if person.get('profile_url'):
            try:
                response = requests.get(person['profile_url'], timeout=5)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    # Make circular
                    photo_label.setPixmap(pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except:
                photo_label.setText("👤")
        else:
            photo_label.setText("👤")
        
        card_layout.addWidget(photo_label, alignment=Qt.AlignCenter)
        
        # Name
        name_label = QLabel(person.get('name', 'Unknown'))
        name_label.setStyleSheet("color: white; font-size: 11px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        card_layout.addWidget(name_label)
        
        # Character
        if person.get('character'):
            char_label = QLabel(person['character'])
            char_label.setStyleSheet("color: #888; font-size: 10px;")
            char_label.setAlignment(Qt.AlignCenter)
            char_label.setWordWrap(True)
            card_layout.addWidget(char_label)
        
        return card
    
    def _on_play(self):
        """Handle play button click"""
        self.play_clicked.emit(self.item_data)
        self.close()
    
    def _on_delete(self):
        """Handle delete button click"""
        from PyQt5.QtWidgets import QMessageBox
        
        # Confirm deletion
        item_type = "series" if 'seasons' in self.item_data else "movie"
        title = self.item_data.get('title', 'Unknown')
        
        reply = QMessageBox.question(
            self,
            "Remove from Library",
            f"Remove '{title}' from your MovieFlix library?\n\n"
            f"Note: The video file(s) will remain on your computer,\n"
            f"they will just be removed from MovieFlix.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_clicked.emit(self.item_data)
            self.close()
