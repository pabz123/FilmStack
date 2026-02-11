"""Modern Netflix-Style Login Dialog"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QWidget, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QCursor
import requests

class LoginDialog(QDialog):
    login_successful = pyqtSignal(str, str)
    def __init__(self, api_url, parent=None):
        super().__init__(parent)
        self.api_url, self.credentials = api_url, None
        self.setWindowTitle("MovieFlix")
        self.setFixedSize(500, 700)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        self.move((screen.width() - 500) // 2, (screen.height() - 700) // 2)
        self.setup_ui()
    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(200, lambda: (self.username_input.setFocus(), QApplication.processEvents()))
    def setup_ui(self):
        self.setStyleSheet("QDialog { background-color: #141414; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        header = QWidget()
        header.setFixedHeight(120)
        header.setStyleSheet("background-color: #000000;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(30, 20, 30, 20)
        logo = QLabel("MOVIEFLIX")
        logo.setStyleSheet("color: #E50914; font-size: 32px; font-weight: bold;")
        h_layout.addWidget(logo)
        h_layout.addStretch()
        layout.addWidget(header)
        content = QWidget()
        content.setStyleSheet("background-color: #141414;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(60, 60, 60, 60)
        card = QWidget()
        card.setFixedWidth(380)
        card.setStyleSheet("background-color: rgba(0, 0, 0, 0.75); border-radius: 8px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(50, 50, 50, 50)
        card_layout.setSpacing(25)
        title = QLabel("Sign In")
        title.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        card_layout.addWidget(title)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Email or username")
        self.username_input.setFixedHeight(50)
        self.username_input.setStyleSheet("QLineEdit { background-color: #333333; color: white; border: 1px solid #555555; border-radius: 4px; padding: 0 15px; font-size: 16px; } QLineEdit:focus { background-color: #454545; border: 1px solid #E50914; }")
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        card_layout.addWidget(self.username_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(50)
        self.password_input.setStyleSheet(self.username_input.styleSheet())
        self.password_input.returnPressed.connect(self.on_login)
        card_layout.addWidget(self.password_input)
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setFixedHeight(50)
        self.login_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_btn.setStyleSheet("QPushButton { background-color: #E50914; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: bold; } QPushButton:hover { background-color: #F40612; }")
        self.login_btn.clicked.connect(self.on_login)
        card_layout.addWidget(self.login_btn)
        
        # Help text with GitHub link
        help_container = QWidget()
        help_layout = QHBoxLayout(help_container)
        help_layout.setContentsMargins(0, 0, 0, 0)
        help_layout.setSpacing(5)
        
        help_text = QLabel("Need help? Report issues on GitHub:")
        help_text.setStyleSheet("color: #737373; font-size: 13px;")
        help_layout.addWidget(help_text)
        
        # Clickable link
        github_link = QLabel('<a href="https://github.com/pabz123/FilmStack/issues" style="color: #E50914; text-decoration: none;">Click here</a>')
        github_link.setStyleSheet("font-size: 13px;")
        github_link.setOpenExternalLinks(True)
        help_layout.addWidget(github_link)
        
        help_layout.addStretch()
        card_layout.addWidget(help_container, alignment=Qt.AlignCenter)
        
        # Register link
        register_btn = QPushButton("New user? Register here")
        register_btn.setFixedHeight(40)
        register_btn.setCursor(QCursor(Qt.PointingHandCursor))
        register_btn.setStyleSheet("QPushButton { background-color: transparent; color: #737373; border: 1px solid #555555; border-radius: 4px; font-size: 14px; } QPushButton:hover { color: white; border-color: #E50914; }")
        register_btn.clicked.connect(self.show_register)
        card_layout.addWidget(register_btn)
        c_layout.addStretch()
        c_layout.addWidget(card, alignment=Qt.AlignCenter)
        c_layout.addStretch()
        layout.addWidget(content)
        footer = QWidget()
        footer.setFixedHeight(60)
        footer.setStyleSheet("background-color: #000000;")
        f_layout = QVBoxLayout(footer)
        f_text = QLabel("© 2026 MovieFlix")
        f_text.setStyleSheet("color: #737373; font-size: 12px;")
        f_text.setAlignment(Qt.AlignCenter)
        f_layout.addWidget(f_text)
        layout.addWidget(footer)
    def on_login(self):
        username, password = self.username_input.text().strip(), self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, 'Login Error', 'Please enter both username and password.')
            return
        self.login_btn.setEnabled(False)
        self.login_btn.setText('Signing in...')
        
        print(f"Attempting login for user: {username}")
        
        try:
            # Use HTTPBasicAuth with /auth/me endpoint
            from requests.auth import HTTPBasicAuth
            response = requests.get(f"{self.api_url}/auth/me", 
                                   auth=HTTPBasicAuth(username, password), 
                                   timeout=5)
            
            print(f"Login response: {response.status_code}")
            
            if response.status_code == 200:
                self.credentials = {'username': username, 'password': password}
                
                print("✓ Login successful!")
                print("Accepting dialog and closing...")
                
                # Accept the dialog immediately - no overlay needed
                # The launcher.py will show its own progress dialog
                self.accept()
                
            else:
                print(f"Login failed: {response.status_code}")
                QMessageBox.warning(self, 'Login Failed', 
                                   'Invalid username or password.\n\n'
                                   'Please check your credentials and try again.')
                self.password_input.clear()
                self.password_input.setFocus()
                self.login_btn.setEnabled(True)
                self.login_btn.setText('Sign In')
        except requests.exceptions.ConnectionError:
            print("Connection error to backend")
            QMessageBox.critical(self, 'Connection Error', 'Cannot connect to backend.')
            self.login_btn.setEnabled(True)
            self.login_btn.setText('Sign In')
        except Exception as e:
            print(f"Login error: {e}")
            QMessageBox.critical(self, 'Error', f'Login error:\n{e}')
            self.login_btn.setEnabled(True)
            self.login_btn.setText('Sign In')
    
    def show_loading_overlay(self):
        """Show loading overlay while UI loads"""
        # Create overlay
        self.loading_overlay = QWidget(self)
        self.loading_overlay.setGeometry(0, 0, self.width(), self.height())
        self.loading_overlay.setStyleSheet("""
            QWidget {
                background-color: rgba(20, 20, 20, 0.95);
            }
        """)
        
        # Layout
        overlay_layout = QVBoxLayout(self.loading_overlay)
        overlay_layout.setAlignment(Qt.AlignCenter)
        
        # Spinner icon
        spinner = QLabel("⏳")
        spinner.setAlignment(Qt.AlignCenter)
        spinner.setStyleSheet("font-size: 48px; color: #E50914;")
        overlay_layout.addWidget(spinner)
        
        # Loading text
        loading_text = QLabel("Loading your library...")
        loading_text.setAlignment(Qt.AlignCenter)
        loading_text.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-top: 10px;
        """)
        overlay_layout.addWidget(loading_text)
        
        # Sub text
        sub_text = QLabel("Please wait a moment")
        sub_text.setAlignment(Qt.AlignCenter)
        sub_text.setStyleSheet("""
            color: #999;
            font-size: 14px;
            margin-top: 5px;
        """)
        overlay_layout.addWidget(sub_text)
        
        self.loading_overlay.show()
        self.loading_overlay.raise_()
        
        # Animate spinner
        self.animate_spinner(spinner)
    
    def animate_spinner(self, spinner):
        """Animate the spinner emoji"""
        spinners = ["⏳", "⌛", "⏳", "⌛"]
        self.spinner_index = 0
        
        def update_spinner():
            if hasattr(self, 'loading_overlay') and self.loading_overlay.isVisible():
                self.spinner_index = (self.spinner_index + 1) % len(spinners)
                spinner.setText(spinners[self.spinner_index])
                QTimer.singleShot(300, update_spinner)
        
        update_spinner()
    
    def close_after_loading(self):
        """Close the dialog after main window is ready"""
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.hide()
        self.accept()
    
    def show_register(self):
        """Show modern registration dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Join MovieFlix")
        dialog.setFixedSize(550, 700)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #000000, stop:1 #1a1a1a);
            }
        """)
        
        # Main layout with no margins
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section with logo
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #000000;")
        header_widget.setFixedHeight(180)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Logo
        logo_label = QLabel("🎬")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            font-size: 60px;
            padding: 10px;
        """)
        header_layout.addWidget(logo_label)
        
        # App name
        app_name = QLabel("MovieFlix")
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet("""
            color: #E50914;
            font-size: 36px;
            font-weight: bold;
            font-family: 'Arial Black', sans-serif;
            letter-spacing: 2px;
            margin-top: 5px;
        """)
        header_layout.addWidget(app_name)
        
        # Tagline
        tagline = QLabel("Create Your Account")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet("""
            color: #999999;
            font-size: 15px;
            margin-top: 10px;
        """)
        header_layout.addWidget(tagline)
        
        main_layout.addWidget(header_widget)
        
        # Form section
        form_widget = QWidget()
        form_widget.setStyleSheet("background: transparent;")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(50, 40, 50, 30)
        form_layout.setSpacing(15)
        
        # Input field style
        input_style = """
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 15px 20px;
                font-size: 15px;
            }
            QLineEdit:focus {
                background-color: #3a3a3a;
                border: 2px solid #E50914;
            }
            QLineEdit:hover {
                border: 2px solid #666666;
            }
        """
        
        label_style = """
            color: white;
            font-size: 13px;
            font-weight: bold;
            margin-bottom: 5px;
        """
        
        # Username
        username_label = QLabel("USERNAME")
        username_label.setStyleSheet(label_style)
        form_layout.addWidget(username_label)
        
        username_input = QLineEdit()
        username_input.setPlaceholderText("Enter your username")
        username_input.setFixedHeight(55)
        username_input.setStyleSheet(input_style)
        form_layout.addWidget(username_input)
        
        form_layout.addSpacing(10)
        
        # Password
        password_label = QLabel("PASSWORD")
        password_label.setStyleSheet(label_style)
        form_layout.addWidget(password_label)
        
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setPlaceholderText("Create a strong password")
        password_input.setFixedHeight(55)
        password_input.setStyleSheet(input_style)
        form_layout.addWidget(password_input)
        
        form_layout.addSpacing(10)
        
        # Confirm Password
        confirm_label = QLabel("CONFIRM PASSWORD")
        confirm_label.setStyleSheet(label_style)
        form_layout.addWidget(confirm_label)
        
        confirm_input = QLineEdit()
        confirm_input.setEchoMode(QLineEdit.Password)
        confirm_input.setPlaceholderText("Re-enter your password")
        confirm_input.setFixedHeight(55)
        confirm_input.setStyleSheet(input_style)
        form_layout.addWidget(confirm_input)
        
        form_layout.addSpacing(20)
        
        # Create Account button
        register_btn = QPushButton("Create Account")
        register_btn.setFixedHeight(55)
        register_btn.setCursor(QCursor(Qt.PointingHandCursor))
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #E50914;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 17px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #F40612;
            }
            QPushButton:pressed {
                background-color: #CC0000;
            }
        """)
        register_btn.clicked.connect(lambda: self.do_register(dialog, username_input.text(), password_input.text(), confirm_input.text()))
        form_layout.addWidget(register_btn)
        
        form_layout.addSpacing(10)
        
        # Info text
        info_text = QLabel("By creating an account, you agree to the MovieFlix Terms of Service")
        info_text.setWordWrap(True)
        info_text.setAlignment(Qt.AlignCenter)
        info_text.setStyleSheet("""
            color: #666666;
            font-size: 11px;
            margin: 10px 0;
        """)
        form_layout.addWidget(info_text)
        
        main_layout.addWidget(form_widget)
        
        # Footer
        footer_widget = QWidget()
        footer_widget.setStyleSheet("background-color: #000000; border-top: 1px solid #333333;")
        footer_widget.setFixedHeight(80)
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setAlignment(Qt.AlignCenter)
        
        # Already have account text
        have_account = QLabel("Already have an account?")
        have_account.setAlignment(Qt.AlignCenter)
        have_account.setStyleSheet("""
            color: #999999;
            font-size: 13px;
        """)
        footer_layout.addWidget(have_account)
        
        # Back to login button
        back_btn = QPushButton("Sign In")
        back_btn.setFixedSize(200, 40)
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #E50914;
                border: 2px solid #E50914;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E50914;
                color: white;
            }
        """)
        back_btn.clicked.connect(dialog.close)
        footer_layout.addWidget(back_btn)
        
        main_layout.addWidget(footer_widget)
        
        dialog.exec_()
    
    def do_register(self, dialog, username, password, confirm):
        """Perform registration"""
        if not username or not password:
            QMessageBox.warning(dialog, 'Registration Error', 'Please fill in all fields.')
            return
        
        if password != confirm:
            QMessageBox.warning(dialog, 'Registration Error', 'Passwords do not match.')
            return
        
        if len(password) < 6:
            QMessageBox.warning(dialog, 'Registration Error', 'Password must be at least 6 characters.')
            return
        
        try:
            response = requests.post(
                f"{self.api_url}/auth/register",
                params={'username': username, 'password': password},
                timeout=5
            )
            
            if response.status_code == 200:
                QMessageBox.information(dialog, 'Success', 'Account created successfully!\n\nYou can now log in.')
                dialog.close()
                # Pre-fill username
                self.username_input.setText(username)
                self.password_input.setFocus()
            else:
                error_msg = response.json().get('detail', 'Registration failed')
                QMessageBox.warning(dialog, 'Registration Failed', error_msg)
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(dialog, 'Connection Error', 'Cannot connect to backend.')
        except Exception as e:
            QMessageBox.critical(dialog, 'Error', f'Registration error:\n{e}')
