import sys
import sqlite3
import bcrypt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
    QMessageBox, QComboBox, QFormLayout, QListWidget
)
from themes import apply_gradient_theme

DATABASE_NAME = "magen.db"

class UserManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Management")
        self.setGeometry(100, 100, 400, 500)
        self.init_ui()
        apply_gradient_theme(self)

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        form_layout.addRow("Username:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)

        self.role_input = QComboBox()
        self.role_input.addItems(["Admin", "Cashier", "Manager"])
        form_layout.addRow("Role:", self.role_input)

        layout.addLayout(form_layout)

        self.add_button = QPushButton("Add User")
        self.add_button.clicked.connect(self.add_user)
        layout.addWidget(self.add_button)

        self.users_list = QListWidget()
        self.refresh_user_list()
        layout.addWidget(self.users_list)

        self.delete_button = QPushButton("Delete Selected User")
        self.delete_button.clicked.connect(self.delete_user)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def create_users_table(self):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def add_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        role = self.role_input.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Missing Data", "Username and password are required.")
            return

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash.decode('utf-8'), role))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", f"User '{username}' added successfully.")
            self.username_input.clear()
            self.password_input.clear()
            self.refresh_user_list()
        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")
            QMessageBox.warning(self, "Error", "Username already exists.")
        except Exception as e:
            print(f"General Error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add user: {e}")

    def refresh_user_list(self):
        self.users_list.clear()
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users")
        for row in cursor.fetchall():
            user_id, username, role = row
            self.users_list.addItem(f"{user_id}: {username} ({role})")
        conn.close()

    def delete_user(self):
        selected_item = self.users_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select a user to delete.")
            return

        user_text = selected_item.text()
        user_id = user_text.split(":")[0]

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this user?\n{user_text}",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DATABASE_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Deleted", "User deleted successfully.")
                self.refresh_user_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UserManager()
    window.create_users_table()
    window.show()
    sys.exit(app.exec_())
