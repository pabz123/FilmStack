"""
Advanced Netflix-style Movie Card with animations and detailed info
"""
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QThread
import requests


class PosterLoader(QThread):
    """Background thread for loading poster images"""
    poster_loaded = pyqtSignal(QPixmap)
    
    def __init__(self, poster_url):
        super().__init__()
        self.poster_url = poster_url
    
    def run(self):
        """Load poster in background"""
        try:
            response = requests.get(self.poster_url, timeout=3)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        220, 280,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                    self.poster_loaded.emit(scaled_pixmap)
        except Exception as e:
            # Silently fail - placeholder will remain
            pass


class AdvancedMovieCard(QFrame):
    """Advanced movie card with hover zoom and details"""
    
    clicked = pyqtSignal(object)
    play_clicked = pyqtSignal(object)
    info_clicked = pyqtSignal(object)
    
    def __init__(self, movie_data, parent=None):
        super().__init__(parent)
        self.movie_data = movie_data
        self.is_hovered = False
        
        self.setFixedSize(220, 330)
        self.setCursor(Qt.PointingHandCursor)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Poster container
        self.poster_container = QFrame()
        self.poster_container.setFixedSize(220, 280)
        poster_layout = QVBoxLayout(self.poster_container)
        poster_layout.setContentsMargins(0, 0, 0, 0)
        
        # Poster image
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(220, 280)
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border-radius: 8px;
            }
        """)
        
        # Load poster
        self._load_poster()
        
        # Hover overlay (initially hidden)
        self.overlay = QFrame(self.poster_label)
        self.overlay.setGeometry(0, 0, 220, 280)
        self.overlay.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0,0,0,0),
                stop:0.5 rgba(0,0,0,0.3),
                stop:1 rgba(0,0,0,0.9));
            border-radius: 8px;
        """)
        self.overlay.hide()
        
        # Hover controls
        controls_layout = QVBoxLayout(self.overlay)
        controls_layout.setContentsMargins(10, 0, 10, 15)
        controls_layout.addStretch()
        
        # Rating badge
        if self.movie_data.get('rating'):
            rating_badge = QLabel(f"⭐ {self.movie_data['rating']:.1f}")
            rating_badge.setStyleSheet("""
                background-color: rgba(229, 9, 20, 0.9);
                color: white;
                padding: 5px 10px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 12px;
            """)
            rating_badge.setFixedHeight(24)
            controls_layout.addWidget(rating_badge)
            controls_layout.addSpacing(5)
        
        # Play button (different behavior for series vs movies)
        if self.movie_data.get('seasons'):  # It's a series
            self.play_btn = QPushButton("▶ Watch")
            self.play_btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.8);
                }
            """)
            self.play_btn.clicked.connect(lambda: self.play_clicked.emit(self.movie_data))
            controls_layout.addWidget(self.play_btn)
        elif not self.movie_data.get('is_tmdb', False) and self.movie_data.get('path'):
            # It's a movie with a path
            self.play_btn = QPushButton("▶ Play")
            self.play_btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.8);
                }
            """)
            self.play_btn.clicked.connect(lambda: self.play_clicked.emit(self.movie_data))
            controls_layout.addWidget(self.play_btn)
        else:
            # For TMDB content they don't have, show "Not in Library" badge
            if self.movie_data.get('is_tmdb', False):
                badge = QLabel("📥 Not in Library")
                badge.setStyleSheet("""
                    background-color: rgba(255, 255, 255, 0.2);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-weight: bold;
                    font-size: 12px;
                """)
                controls_layout.addWidget(badge)
        
        # Info button
        self.info_btn = QPushButton("ℹ Info")
        self.info_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(109, 109, 110, 0.7);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(109, 109, 110, 0.9);
            }
        """)
        self.info_btn.clicked.connect(lambda: self.info_clicked.emit(self.movie_data))
        controls_layout.addWidget(self.info_btn)
        
        poster_layout.addWidget(self.poster_label)
        
        # Title and info
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(5, 8, 5, 0)
        info_layout.setSpacing(3)
        
        title = QLabel(self.movie_data.get('title', 'Unknown'))
        title.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: bold;
        """)
        title.setWordWrap(True)
        title.setMaximumHeight(40)
        info_layout.addWidget(title)
        
        # Watch status
        if self.movie_data.get('watched'):
            watched_label = QLabel("✓ Watched")
            watched_label.setStyleSheet("color: #46d369; font-size: 11px;")
            info_layout.addWidget(watched_label)
        
        # Series info (seasons/episodes count)
        if self.movie_data.get('seasons'):
            season_count = len(self.movie_data['seasons'])
            episode_count = sum(len(season.get('episodes', [])) for season in self.movie_data['seasons'])
            series_info = QLabel(f"{season_count} Season{'s' if season_count != 1 else ''} • {episode_count} Episodes")
            series_info.setStyleSheet("color: #888; font-size: 11px;")
            info_layout.addWidget(series_info)
        
        layout.addWidget(self.poster_container)
        layout.addWidget(info_container)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        # Animations
        self.scale_anim = QPropertyAnimation(self, b"geometry")
        self.scale_anim.setDuration(200)
        self.scale_anim.setEasingCurve(QEasingCurve.OutCubic)
        
    def _load_poster(self):
        """Load poster image asynchronously using QThread"""
        poster = self.movie_data.get('poster', '')
        
        # Show placeholder immediately
        self._show_placeholder()
        
        # Check if we have a poster URL
        if poster:
            # If it starts with http, use it directly
            if poster.startswith('http'):
                poster_url = poster
            else:
                # Otherwise, add TMDB base URL
                poster_url = f"https://image.tmdb.org/t/p/w500{poster}"
            
            # Load poster in background thread
            self.poster_loader = PosterLoader(poster_url)
            self.poster_loader.poster_loaded.connect(self._on_poster_loaded)
            self.poster_loader.start()
    
    def _on_poster_loaded(self, pixmap):
        """Called when poster is loaded in background"""
        self.poster_label.setPixmap(pixmap)
        self.poster_label.setText("")  # Clear placeholder text
    
    def _show_placeholder(self):
        """Show placeholder with movie title"""
        title = self.movie_data.get('title', 'No Image')
        # Shorten very long titles
        if len(title) > 40:
            title = title[:37] + "..."
        
        self.poster_label.setText(title)
        self.poster_label.setStyleSheet("""
            background-color: #2a2a2a;
            color: #666;
            font-size: 12px;
            padding: 10px;
            border-radius: 8px;
        """)
        self.poster_label.setWordWrap(True)
    
    def enterEvent(self, event):
        """Show overlay on hover"""
        self.is_hovered = True
        self.overlay.show()
        
        # Subtle glow effect without changing position
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 1px solid rgba(229, 9, 20, 0.8);
            }
        """)
        
        self.raise_()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Hide overlay when not hovering"""
        self.is_hovered = False
        self.overlay.hide()
        
        # Reset to default style
        self.setStyleSheet("""
            QFrame {
                background-color: #141414;
                border-radius: 8px;
                border: none;
            }
        """)
        
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Emit clicked signal"""
        if not self.is_hovered:
            self.clicked.emit(self.movie_data)
        super().mousePressEvent(event)


class CategoryRow(QWidget):
    """Horizontal scrolling category row with enhanced styling"""
    
    def __init__(self, title, show_all_callback=None, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 15, 40, 15)
        main_layout.setSpacing(15)
        
        # Header with title and "See All" button
        header_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        if show_all_callback:
            see_all_btn = QPushButton("See All →")
            see_all_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #e5e5e5;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    color: white;
                }
            """)
            see_all_btn.setCursor(Qt.PointingHandCursor)
            see_all_btn.clicked.connect(show_all_callback)
            header_layout.addWidget(see_all_btn)
        
        main_layout.addLayout(header_layout)
        
        # Scroll area with custom styling
        from PyQt5.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedHeight(360)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:horizontal {
                height: 10px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                margin: 0 40px;
            }
            QScrollBar::handle:horizontal {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                min-width: 50px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: rgba(229, 9, 20, 0.8);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        # Container for cards
        self.container = QWidget()
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(20)
        self.container_layout.addStretch()
        
        scroll.setWidget(self.container)
        main_layout.addWidget(scroll)
        
    def add_card(self, card):
        """Add a card to the row"""
        self.container_layout.insertWidget(self.container_layout.count() - 1, card)
    
    def clear_cards(self):
        """Remove all cards"""
        while self.container_layout.count() > 1:  # Keep the stretch
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
