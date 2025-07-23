import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QFileDialog, QLabel
)
from PyQt5.QtCore import Qt
from themes import apply_gradient_theme

class SuppliersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Suppliers Management")
        apply_gradient_theme(self)
        self.setGeometry(200, 200, 750, 500)
        self.init_ui()

    def get_connection(self):
        return sqlite3.connect('magen.db')

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Suppliers Management")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Form layout
        form_layout = QFormLayout()
        self.supplier_name_input = QLineEdit()
        self.contact_person_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        self.products_supplied_input = QLineEdit()

        form_layout.addRow("Supplier Name:", self.supplier_name_input)
        form_layout.addRow("Contact Person:", self.contact_person_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Address:", self.address_input)
        form_layout.addRow("Products Supplied:", self.products_supplied_input)
        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Supplier")
        self.update_button = QPushButton("Update Selected")
        self.delete_button = QPushButton("Delete Selected")
        self.export_button = QPushButton("Export CSV")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        layout.addLayout(button_layout)

        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by supplier name, contact, or product...")
        self.search_button = QPushButton("Search")
        self.clear_search_button = QPushButton("Clear")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_search_button)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Supplier Name", "Contact Person", "Phone",
            "Email", "Address", "Products Supplied"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Connections
        self.add_button.clicked.connect(self.add_supplier)
        self.update_button.clicked.connect(self.update_supplier)
        self.delete_button.clicked.connect(self.delete_supplier)
        self.export_button.clicked.connect(self.export_to_csv)
        self.search_button.clicked.connect(self.search_suppliers)
        self.clear_search_button.clicked.connect(self.load_suppliers)
        self.table.itemSelectionChanged.connect(self.load_selected_supplier)

        self.load_suppliers()

        # Style
        self.setStyleSheet("""
            QWidget { font-size: 14px; }
            QLineEdit, QPushButton { padding: 6px; }
            QPushButton {
                background-color: #239B56;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1D8348; }
        """)

    def add_supplier(self):
        supplier_name = self.supplier_name_input.text().strip()
        contact_person = self.contact_person_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()
        products_supplied = self.products_supplied_input.text().strip()

        if not supplier_name or not phone:
            QMessageBox.warning(self, "Input Error", "Supplier Name and Phone are required.")
            return

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO suppliers (supplier_name, contact_person, phone, email, address, products_supplied)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (supplier_name, contact_person, phone, email, address, products_supplied))
        conn.commit()
        conn.close()

        self.clear_inputs()
        self.load_suppliers()
        QMessageBox.information(self, "Success", "Supplier added successfully.")

    def load_suppliers(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers")
        suppliers = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row_data in suppliers:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
            for col, data in enumerate(row_data):
                self.table.setItem(row_index, col, QTableWidgetItem(str(data)))

    def load_selected_supplier(self):
        selected = self.table.selectedItems()
        if selected:
            self.supplier_name_input.setText(selected[1].text())
            self.contact_person_input.setText(selected[2].text())
            self.phone_input.setText(selected[3].text())
            self.email_input.setText(selected[4].text())
            self.address_input.setText(selected[5].text())
            self.products_supplied_input.setText(selected[6].text())

    def update_supplier(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Selection Error", "Please select a supplier to update.")
            return

        supplier_id = int(selected[0].text())
        supplier_name = self.supplier_name_input.text().strip()
        contact_person = self.contact_person_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()
        products_supplied = self.products_supplied_input.text().strip()

        if not supplier_name or not phone:
            QMessageBox.warning(self, "Input Error", "Supplier Name and Phone are required.")
            return

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE suppliers
            SET supplier_name = ?, contact_person = ?, phone = ?, email = ?, address = ?, products_supplied = ?
            WHERE id = ?
        """, (supplier_name, contact_person, phone, email, address, products_supplied, supplier_id))
        conn.commit()
        conn.close()

        self.clear_inputs()
        self.load_suppliers()
        QMessageBox.information(self, "Success", "Supplier updated successfully.")

    def delete_supplier(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Selection Error", "Please select a supplier to delete.")
            return

        supplier_id = int(selected[0].text())

        confirm = QMessageBox.question(self, "Confirm Delete",
                                       "Are you sure you want to delete this supplier?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
            conn.commit()
            conn.close()

            self.clear_inputs()
            self.load_suppliers()
            QMessageBox.information(self, "Deleted", "Supplier deleted successfully.")

    def search_suppliers(self):
        keyword = self.search_input.text().strip()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM suppliers
            WHERE supplier_name LIKE ? OR contact_person LIKE ? OR products_supplied LIKE ?
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        suppliers = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row_data in suppliers:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
            for col, data in enumerate(row_data):
                self.table.setItem(row_index, col, QTableWidgetItem(str(data)))

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if path:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers")
            suppliers = cursor.fetchall()
            conn.close()

            with open(path, "w", newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "ID", "Supplier Name", "Contact Person",
                    "Phone", "Email", "Address", "Products Supplied"
                ])
                writer.writerows(suppliers)

            QMessageBox.information(self, "Export Complete", f"Supplier data exported to {path}")

    def clear_inputs(self):
        self.supplier_name_input.clear()
        self.contact_person_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.products_supplied_input.clear()
        self.table.clearSelection()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SuppliersWindow()
    window.show()
    sys.exit(app.exec_())
