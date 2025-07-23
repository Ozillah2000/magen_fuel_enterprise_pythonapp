import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtSignal

class LoginWindow(QMainWindow):
    login_success = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magen Fuel Enterprise - Login")
        self.setFixedSize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        # Background
        self.background_label = QLabel(self)
        pixmap = QPixmap('utils/assets/images/images1.jpg')  # Ensure correct path
        if pixmap.isNull():
            print("Image not found.")
        else:
            self.background_label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.background_label.setGeometry(0, 0, 600, 400)

        # Welcome message
        self.welcome_label = QLabel("Welcome to Magen Business Enterprise", self)
        self.welcome_label.setStyleSheet("color: blue; font-size: 20px; font-weight: bold;")
        self.welcome_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setGeometry(50, 30, 500, 40)

        # Fade animation
        self.fade_effect = QGraphicsOpacityEffect()
        self.welcome_label.setGraphicsEffect(self.fade_effect)
        self.fade_animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_animation.setDuration(2000)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()

        # Login form
        self.central_widget = QWidget(self)
        self.central_widget.setGeometry(150, 100, 300, 200)
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.central_widget.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        try:
            conn = sqlite3.connect('magen.db')
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                self.login_success.emit()
                self.close()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()

    from dashboard import DashboardWindow
    window.login_success.connect(lambda: DashboardWindow().show())

    def show_dashboard():
        window.close()
        dashboard_window = DashboardWindow()
        dashboard_window.show()
    window.show()

    window.login_success.connect(show_dashboard)
    window.show()
    sys.exit(app.exec_())
