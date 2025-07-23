import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
    QMessageBox, QFileDialog, QComboBox, QDateEdit, QFormLayout
)
from PyQt5.QtCore import QDate
import sqlite3

DATABASE_NAME = "magen.db"

class PurchasesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Record Purchase")
        self.setGeometry(100, 100, 400, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)

        # Product Dropdown
        self.product_input = QComboBox()
        self.product_input.addItems(["PMS", "AGO", "IK", "Gas"])
        form_layout.addRow("Select Product:", self.product_input)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Quantity")
        form_layout.addRow("Quantity:", self.quantity_input)

        self.unit_price_input = QLineEdit()
        self.unit_price_input.setPlaceholderText("Unit Price")
        form_layout.addRow("Unit Price:", self.unit_price_input)

        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Supplier Name")
        form_layout.addRow("Supplier Name:", self.supplier_input)

        # Date Picker
        self.date_picker = QDateEdit(calendarPopup=True)
        self.date_picker.setDate(QDate.currentDate())
        form_layout.addRow("Select Purchase Date:", self.date_picker)

        layout.addLayout(form_layout)

        # Attachment Buttons
        self.lpo_button = QPushButton("Attach LPO")
        self.lpo_button.clicked.connect(lambda: self.attach_file("LPO"))
        layout.addWidget(self.lpo_button)

        self.invoice_button = QPushButton("Attach Invoice")
        self.invoice_button.clicked.connect(lambda: self.attach_file("Invoice"))
        layout.addWidget(self.invoice_button)

        self.delivery_note_button = QPushButton("Attach Delivery Note")
        self.delivery_note_button.clicked.connect(lambda: self.attach_file("Delivery Note"))
        layout.addWidget(self.delivery_note_button)

        self.receipt_button = QPushButton("Attach Receipt")
        self.receipt_button.clicked.connect(lambda: self.attach_file("Receipt"))
        layout.addWidget(self.receipt_button)

        self.save_button = QPushButton("Save Purchase")
        self.save_button.clicked.connect(self.save_purchase)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        # File paths
        self.lpo_path = ""
        self.invoice_path = ""
        self.delivery_note_path = ""
        self.receipt_path = ""

    def attach_file(self, doc_type):
        file_path, _ = QFileDialog.getOpenFileName(self, f"Select {doc_type} file")
        if file_path:
            setattr(self, f"{doc_type.lower().replace(' ', '_')}_path", file_path)
            QMessageBox.information(self, "File Attached", f"{doc_type} attached successfully.")

    def save_purchase(self):
        product = self.product_input.currentText()
        quantity = self.quantity_input.text()
        unit_price = self.unit_price_input.text()
        supplier = self.supplier_input.text()
        date = self.date_picker.date().toString("yyyy-MM-dd")

        if not quantity or not unit_price:
            QMessageBox.warning(self, "Missing Data", "Quantity and unit price are required.")
            return

        try:
            quantity_val = float(quantity)
            unit_price_val = float(unit_price)
            total = quantity_val * unit_price_val

            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            # Ensure purchases table supports attachments
            cursor.execute("""
                INSERT INTO purchases (
                    product, quantity, unit_price, total, supplier, date, 
                    lpo_path, invoice_path, delivery_note_path, receipt_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product, quantity_val, unit_price_val, total, supplier, date,
                self.lpo_path, self.invoice_path, self.delivery_note_path, self.receipt_path
            ))

            # Update stock quantity or insert if not exists
            cursor.execute("SELECT quantity FROM stock WHERE product = ?", (product,))
            result = cursor.fetchone()
            if result:
                new_quantity = result[0] + quantity_val
                cursor.execute("UPDATE stock SET quantity = ? WHERE product = ?", (new_quantity, product))
            else:
                default_reorder_level = 450
                cursor.execute(
                    "INSERT INTO stock (product, quantity, reorder_level) VALUES (?, ?, ?)",
                    (product, quantity_val, default_reorder_level)
                )

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Purchase recorded and stock updated successfully.")
            self.clear_fields()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving purchase: {e}")

    def clear_fields(self):
        self.quantity_input.clear()
        self.unit_price_input.clear()
        self.supplier_input.clear()
        self.date_picker.setDate(QDate.currentDate())
        self.lpo_path = ""
        self.invoice_path = ""
        self.delivery_note_path = ""
        self.receipt_path = ""

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PurchasesWindow()
    window.show()
    sys.exit(app.exec_())
