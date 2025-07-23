# themes.py
from PyQt5 import QtGui
def apply_gradient_theme(window):
    window.setStyleSheet("""
        QWidget {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #2c3e50,
                stop:1 #3498db
            );
            color: white;
            font-family: Segoe UI, sans-serif;
            font-size: 14px;
        }
        QLineEdit, QComboBox, QDateEdit {
            background-color: rgba(255, 255, 255, 0.8);
            color: #2c3e50;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        QPushButton {
            background-color: #2980b9;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #3498db;
        }
        QLabel {
            font-weight: bold;
        }
    """)
    
