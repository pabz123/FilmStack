"""
Redesigned Modern Profile Management Dialog
Netflix-style with avatar support and better UX
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFrame,
                             QScrollArea, QWidget, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QPen
import requests


class ProfileManagementDialog(QDialog):
    """Modern profile management dialog with avatars"""
    
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.selected_avatar = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Profile Management")
        self.setFixedSize(600, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #141414;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #000000; padding: 20px;")
        header_layout = QVBoxLayout(header)
        
        title = QLabel("👤 Profile Management")
        title.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        
        subtitle = QLabel(f"Logged in as: {self.username}")
        subtitle.setStyleSheet("""
            color: #999;
            font-size: 14px;
            margin-top: 5px;
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #141414;
            }
            QScrollBar:vertical {
                width: 12px;
                background-color: #1a1a1a;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
            }
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)
        
        # Display Name Section
        name_section = self._create_section("Display Name", "Change how your name appears")
        self.name_input = QLineEdit()
        self.name_input.setText(self.username)
        self.name_input.setPlaceholderText("Enter display name")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 12px;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 2px solid #e50914;
            }
        """)
        name_section.layout().addWidget(self.name_input)
        content_layout.addWidget(name_section)
        
        # Email Section
        email_section = self._create_section("Email (Optional)", "For notifications and recovery")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your@email.com")
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 12px;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 2px solid #e50914;
            }
        """)
        email_section.layout().addWidget(self.email_input)
        content_layout.addWidget(email_section)
        
        # Avatar Selection Section
        avatar_section = self._create_section("Choose Avatar", "Select your profile picture")
        avatar_grid = QGridLayout()
        avatar_grid.setSpacing(15)
        
        # Avatar options
        avatars = [
            ("👤", "Default"),
            ("😀", "Happy"),
            ("😎", "Cool"),
            ("🎭", "Theater"),
            ("🎬", "Movie"),
            ("🍿", "Popcorn"),
            ("🎮", "Gamer"),
            ("🎵", "Music"),
            ("📚", "Reader"),
            ("🚀", "Space"),
            ("🦸", "Hero"),
            ("🧙", "Wizard")
        ]
        
        row, col = 0, 0
        for emoji, name in avatars:
            btn = QPushButton(emoji)
            btn.setFixedSize(70, 70)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a2a;
                    border: 3px solid #444;
                    border-radius: 35px;
                    font-size: 32px;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                    border: 3px solid #e50914;
                }
                QPushButton:pressed {
                    background-color: #1a1a1a;
                }
            """)
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, e=emoji: self.select_avatar(e))
            avatar_grid.addWidget(btn, row, col)
            
            col += 1
            if col >= 6:
                col = 0
                row += 1
        
        avatar_widget = QWidget()
        avatar_widget.setLayout(avatar_grid)
        avatar_section.layout().addWidget(avatar_widget)
        content_layout.addWidget(avatar_section)
        
        # Selected Avatar Display
        self.selected_label = QLabel("Selected: 👤 Default")
        self.selected_label.setStyleSheet("""
            color: #46d369;
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
        """)
        self.selected_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.selected_label)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Footer with buttons
        footer = QFrame()
        footer.setStyleSheet("background-color: #000000; padding: 20px;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setSpacing(15)
        
        footer_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(45)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        footer_layout.addWidget(cancel_btn)
        
        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.setFixedHeight(45)
        save_btn.setMinimumWidth(150)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f40612;
            }
            QPushButton:pressed {
                background-color: #b8070d;
            }
        """)
        save_btn.clicked.connect(self.save_profile)
        footer_layout.addWidget(save_btn)
        
        layout.addWidget(footer)
        
    def _create_section(self, title, description):
        """Create a settings section"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        section_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            color: #999;
            font-size: 13px;
        """)
        section_layout.addWidget(desc_label)
        
        return section
    
    def select_avatar(self, emoji):
        """Select an avatar"""
        self.selected_avatar = emoji
        avatar_names = {
            "👤": "Default", "😀": "Happy", "😎": "Cool",
            "🎭": "Theater", "🎬": "Movie", "🍿": "Popcorn",
            "🎮": "Gamer", "🎵": "Music", "📚": "Reader",
            "🚀": "Space", "🦸": "Hero", "🧙": "Wizard"
        }
        name = avatar_names.get(emoji, "Custom")
        self.selected_label.setText(f"Selected: {emoji} {name}")
    
    def save_profile(self):
        """Save profile changes"""
        display_name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        
        if not display_name:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Display name cannot be empty."
            )
            return
        
        # Update credentials
        from app.advanced_ui import AUTH_CREDENTIALS
        AUTH_CREDENTIALS['username'] = display_name
        if email:
            AUTH_CREDENTIALS['email'] = email
        if self.selected_avatar:
            AUTH_CREDENTIALS['avatar'] = self.selected_avatar
        
        QMessageBox.information(
            self,
            "Profile Updated",
            f"Your profile has been updated successfully!\n\n"
            f"Display Name: {display_name}\n"
            f"Avatar: {self.selected_avatar or '👤'}"
        )
        self.accept()
    
    def get_profile_data(self):
        """Get the profile data"""
        return {
            'display_name': self.name_input.text().strip(),
            'email': self.email_input.text().strip(),
            'avatar': self.selected_avatar or '👤'
        }
