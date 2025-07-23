import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from database import init_db
from dashboard import DashboardWindow


class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magen Business Enterprise Login")
        self.setFixedSize(500, 400)

        # Background Image
        import os
        image_path = os.path.join(os.getcwd(), "assets", "images", "download.jpg")
        if not os.path.exists(image_path):
            print(f"Image not found at {image_path}")
        else:
            print(f"Image found at {image_path}")

        self.background = QtGui.QPixmap(image_path)
        self.label_background = QtWidgets.QLabel(self)
        self.label_background.setPixmap(self.background)
        self.label_background.setScaledContents(True)
        self.label_background.setGeometry(0, 0, 500, 400)
        self.label_background.lower()

        # Animated Welcome Text
        self.welcome_label = QtWidgets.QLabel("Welcome to Magen Enterprise", self)
        self.welcome_label.setStyleSheet("color: blue; font-size: 20px; font-weight: bold;")
        self.welcome_label.setGeometry(500, 30, 350, 50)

        self.animation = QtCore.QPropertyAnimation(self.welcome_label, b"geometry")
        self.animation.setDuration(2000)
        self.animation.setStartValue(QtCore.QRect(500, 30, 350, 50))
        self.animation.setEndValue(QtCore.QRect(80, 30, 350, 50))
        self.animation.start()

        # Username Input
        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        self.username_input.setGeometry(150, 150, 200, 30)

        # Password Input
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setGeometry(150, 200, 200, 30)

        # Login Button
        self.login_button = QtWidgets.QPushButton("Login", self)
        self.login_button.setGeometry(200, 250, 100, 40)
        self.login_button.clicked.connect(self.login)

        # Message Label
        self.message_label = QtWidgets.QLabel("", self)
        self.message_label.setGeometry(100, 300, 300, 30)
        self.message_label.setStyleSheet("color: red; font-weight: bold;")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        import sqlite3
        conn = sqlite3.connect('magen.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            self.message_label.setStyleSheet("color: lightgreen; font-weight: bold;")
            self.message_label.setText("Login successful! Redirecting...")
            QtCore.QTimer.singleShot(1000, self.open_dashboard)
        else:
            self.message_label.setStyleSheet("color: red; font-weight: bold;")
            self.message_label.setText("Invalid username or password.")

    def open_dashboard(self):
        self.dashboard = DashboardWindow()
        self.dashboard.show()
        self.close()

if __name__ == "__main__":
    init_db()  # Ensures your database and tables are ready on first run

    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
