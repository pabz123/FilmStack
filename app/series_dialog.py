"""
Series Episode Selector Dialog
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QWidget, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import requests


class SeriesEpisodeDialog(QDialog):
    """Dialog to select season and episode"""
    
    play_episode = pyqtSignal(dict)  # Emits episode dict
    
    def __init__(self, series, api_url, parent=None):
        super().__init__(parent)
        self.series = series
        self.api_url = api_url
        self.episodes = []
        
        self.setWindowTitle(f"Select Episode - {series.get('title', 'Unknown')}")
        self.setModal(True)
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_episodes()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a,
                    stop:1 #0a0a0a);
                border-bottom: 2px solid #e50914;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header)
        
        title = QLabel(self.series.get('title', 'Unknown Series'))
        title.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        header_layout.addWidget(title)
        
        if self.series.get('overview'):
            desc = QLabel(self.series['overview'][:200] + "...")
            desc.setStyleSheet("color: #ccc; font-size: 14px;")
            desc.setWordWrap(True)
            header_layout.addWidget(desc)
        
        layout.addWidget(header)
        
        # Scroll area for episodes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #141414;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(50)
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        layout.addWidget(close_btn)
    
    def load_episodes(self):
        """Load episodes from API"""
        try:
            series_id = self.series.get('id')
            if not series_id:
                self._show_error("Series ID not found")
                return
            
            response = requests.get(f"{self.api_url}/series/{series_id}/episodes", timeout=5)
            
            if response.status_code == 200:
                self.episodes = response.json()
                
                if not self.episodes:
                    self._show_error("No episodes found")
                    return
                
                self.display_episodes()
            else:
                self._show_error(f"Failed to load episodes (status: {response.status_code})")
                
        except Exception as e:
            print(f"Error loading episodes: {e}")
            self._show_error(f"Error: {str(e)}")
    
    def display_episodes(self):
        """Display episodes grouped by season"""
        # Group by season
        seasons = {}
        for ep in self.episodes:
            season_num = ep.get('season_number', 1)
            if season_num not in seasons:
                seasons[season_num] = []
            seasons[season_num].append(ep)
        
        # Display each season
        for season_num in sorted(seasons.keys()):
            # Season header
            season_label = QLabel(f"Season {season_num}")
            season_label.setStyleSheet("""
                color: white;
                font-size: 22px;
                font-weight: bold;
                padding: 15px 0 10px 0;
            """)
            self.content_layout.addWidget(season_label)
            
            # Episodes in this season
            episodes = sorted(seasons[season_num], key=lambda x: x.get('episode_number', 0))
            
            for episode in episodes:
                ep_widget = self.create_episode_widget(episode)
                self.content_layout.addWidget(ep_widget)
        
        self.content_layout.addStretch()
    
    def create_episode_widget(self, episode):
        """Create widget for single episode"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #222;
                border-radius: 8px;
                padding: 15px;
            }
            QFrame:hover {
                background-color: #2a2a2a;
            }
        """)
        
        layout = QHBoxLayout(widget)
        
        # Episode info
        info_layout = QVBoxLayout()
        
        ep_title = QLabel(f"E{episode.get('episode_number', '?')} - {episode.get('title', 'Unknown')}")
        ep_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        info_layout.addWidget(ep_title)
        
        if episode.get('overview'):
            desc = QLabel(episode['overview'][:150] + "..." if len(episode.get('overview', '')) > 150 else episode.get('overview', ''))
            desc.setStyleSheet("color: #aaa; font-size: 13px;")
            desc.setWordWrap(True)
            info_layout.addWidget(desc)
        
        # Duration if available
        if episode.get('duration'):
            duration_label = QLabel(f"Duration: {episode['duration']} min")
            duration_label.setStyleSheet("color: #888; font-size: 12px;")
            info_layout.addWidget(duration_label)
        
        layout.addLayout(info_layout, 1)
        
        # Play button
        play_btn = QPushButton("▶ Play")
        play_btn.setFixedSize(100, 40)
        play_btn.clicked.connect(lambda: self.on_play_episode(episode))
        play_btn.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f40612;
            }
        """)
        play_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(play_btn)
        
        return widget
    
    def on_play_episode(self, episode):
        """Handle play episode"""
        self.play_episode.emit(episode)
        self.accept()
    
    def _show_error(self, message):
        """Show error message"""
        error_label = QLabel(f"⚠️ {message}")
        error_label.setStyleSheet("color: #e50914; font-size: 16px; padding: 20px;")
        error_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(error_label)
