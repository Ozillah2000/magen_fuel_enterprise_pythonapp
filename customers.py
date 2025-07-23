import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QFileDialog, QLabel
)
from PyQt5.QtCore import Qt

class CustomersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customers Management")
        self.setGeometry(150, 150, 700, 500)
        self.init_ui()

    def get_connection(self):
        return sqlite3.connect('magen.db')

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Customers Management")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Form layout
        form_layout = QFormLayout()
        self.full_name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        form_layout.addRow("Full Name:", self.full_name_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Address:", self.address_input)
        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Customer")
        self.update_button = QPushButton("Update Selected")
        self.delete_button = QPushButton("Delete Selected")
        self.export_button = QPushButton("Export CSV")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        layout.addLayout(button_layout)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or phone...")
        self.search_button = QPushButton("Search")
        self.clear_search_button = QPushButton("Clear")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_search_button)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Full Name", "Phone", "Email", "Address"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Connections
        self.add_button.clicked.connect(self.add_customer)
        self.update_button.clicked.connect(self.update_customer)
        self.delete_button.clicked.connect(self.delete_customer)
        self.export_button.clicked.connect(self.export_to_csv)
        self.search_button.clicked.connect(self.search_customers)
        self.clear_search_button.clicked.connect(self.load_customers)
        self.table.itemSelectionChanged.connect(self.load_selected_customer)

        self.load_customers()

        # Style
        self.setStyleSheet("""
            QWidget { font-size: 14px; }
            QLineEdit, QPushButton { padding: 6px; }
            QPushButton {
                background-color: #2471A3;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1F618D; }
        """)

    def add_customer(self):
        name = self.full_name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()

        if not name or not phone:
            QMessageBox.warning(self, "Input Error", "Full Name and Phone are required.")
            return

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers (full_name, phone, email, address)
            VALUES (?, ?, ?, ?)
        """, (name, phone, email, address))
        conn.commit()
        conn.close()

        self.clear_inputs()
        self.load_customers()
        QMessageBox.information(self, "Success", "Customer added successfully.")

    def load_customers(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row_data in customers:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
            for col, data in enumerate(row_data):
                self.table.setItem(row_index, col, QTableWidgetItem(str(data)))

    def load_selected_customer(self):
        selected = self.table.selectedItems()
        if selected:
            self.full_name_input.setText(selected[1].text())
            self.phone_input.setText(selected[2].text())
            self.email_input.setText(selected[3].text())
            self.address_input.setText(selected[4].text())

    def update_customer(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Selection Error", "Please select a customer to update.")
            return

        customer_id = int(selected[0].text())
        name = self.full_name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()

        if not name or not phone:
            QMessageBox.warning(self, "Input Error", "Full Name and Phone are required.")
            return

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE customers
            SET full_name = ?, phone = ?, email = ?, address = ?
            WHERE id = ?
        """, (name, phone, email, address, customer_id))
        conn.commit()
        conn.close()

        self.clear_inputs()
        self.load_customers()
        QMessageBox.information(self, "Success", "Customer updated successfully.")

    def delete_customer(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Selection Error", "Please select a customer to delete.")
            return

        customer_id = int(selected[0].text())

        confirm = QMessageBox.question(self, "Confirm Delete",
                                       "Are you sure you want to delete this customer?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            conn.commit()
            conn.close()

            self.clear_inputs()
            self.load_customers()
            QMessageBox.information(self, "Deleted", "Customer deleted successfully.")

    def search_customers(self):
        keyword = self.search_input.text().strip()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM customers
            WHERE full_name LIKE ? OR phone LIKE ?
        """, (f"%{keyword}%", f"%{keyword}%"))
        customers = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row_data in customers:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
            for col, data in enumerate(row_data):
                self.table.setItem(row_index, col, QTableWidgetItem(str(data)))

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if path:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers")
            customers = cursor.fetchall()
            conn.close()

            with open(path, "w", newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Full Name", "Phone", "Email", "Address"])
                writer.writerows(customers)

            QMessageBox.information(self, "Export Complete", f"Customer data exported to {path}")

    def clear_inputs(self):
        self.full_name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.table.clearSelection()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomersWindow()
    window.show()
    sys.exit(app.exec_())
