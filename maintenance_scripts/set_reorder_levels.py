import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QMessageBox, QHBoxLayout
)
from database import get_connection

class ReorderLevelManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reorder Level Manager")
        self.resize(500, 400)
        self.layout = QVBoxLayout()

        self.label = QLabel("View and Update Reorder Levels for Products")
        self.layout.addWidget(self.label)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Product", "Current Quantity", "Reorder Level"])
        self.layout.addWidget(self.table)

        # Update section
        self.update_layout = QHBoxLayout()
        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("Product Name (case-sensitive)")
        self.reorder_input = QLineEdit()
        self.reorder_input.setPlaceholderText("New Reorder Level")

        self.update_button = QPushButton("Update Reorder Level")
        self.update_button.clicked.connect(self.update_reorder_level)

        self.update_layout.addWidget(self.product_input)
        self.update_layout.addWidget(self.reorder_input)
        self.update_layout.addWidget(self.update_button)
        self.layout.addLayout(self.update_layout)

        self.setLayout(self.layout)
        self.load_data()

    def load_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT product, quantity, reorder_level FROM stock")
        data = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        self.table.resizeColumnsToContents()

    def update_reorder_level(self):
        product = self.product_input.text().strip()
        reorder_level = self.reorder_input.text().strip()

        if not product or not reorder_level:
            QMessageBox.warning(self, "Input Error", "Please fill in both product and reorder level.")
            return

        try:
            reorder_level = float(reorder_level)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Reorder level must be a number.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM stock WHERE product = ?", (product,))
        result = cursor.fetchone()

        if not result:
            QMessageBox.warning(self, "Error", f"Product '{product}' not found in stock.")
            conn.close()
            return

        cursor.execute(
            "UPDATE stock SET reorder_level = ? WHERE product = ?",
            (reorder_level, product)
        )
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", f"Reorder level for '{product}' updated successfully.")
        self.product_input.clear()
        self.reorder_input.clear()
        self.load_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReorderLevelManager()
    window.show()
    sys.exit(app.exec_())
