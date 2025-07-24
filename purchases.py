from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
    QMessageBox, QComboBox, QDateEdit, QFormLayout
)
from PyQt5.QtCore import QDate
import sqlite3
import sys
import os

from pdf_generator import generate_lpo_pdf_document
from themes import apply_gradient_theme

DATABASE_NAME = "magen.db"

class PurchasesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Record Purchase")
        self.setGeometry(100, 100, 400, 500)
        self.init_ui()
        apply_gradient_theme(self)

    def fetch_suppliers(self):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT supplier_name FROM suppliers")
        suppliers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return suppliers

    def generate_lpo_pdf(self, purchase_id, product, quantity, unit_price, total, supplier, date):
        if not os.path.exists("purchases_lpos"):
            os.makedirs("purchases_lpos")
        file_path = f"purchases_lpos/LPO_{purchase_id}.pdf"

        lpo_data = {
            "customer_name": supplier,
            "date": date,
            "items": [
                {
                    "product": product,
                    "quantity": quantity,
                    "price": unit_price,
                    "total": total
                }
            ]
        }

        generate_lpo_pdf_document(
            lpo_number=purchase_id,
            lpo_data=lpo_data,
            filename=file_path,
            branch_info={
                "name": "Magen Fuel Enterprise",
                "address": "P.O Box 12345-00100, Nairobi, Kenya",
                "contacts": "Tel: +254 700 123456 | Email: info@magenfuel.co.ke"
            }
        )

        QMessageBox.information(self, "LPO Generated", f"LPO PDF generated at:\n{file_path}")

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)

        self.product_input = QComboBox()
        self.product_input.addItems(["PMS", "AGO", "IK", "Gas"])
        form_layout.addRow("Select Product:", self.product_input)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Quantity")
        form_layout.addRow("Quantity:", self.quantity_input)

        self.unit_price_input = QLineEdit()
        self.unit_price_input.setPlaceholderText("Unit Price")
        form_layout.addRow("Unit Price:", self.unit_price_input)

        self.supplier_input = QComboBox()
        self.supplier_input.addItems(self.fetch_suppliers())
        form_layout.addRow("Select Supplier:", self.supplier_input)

        self.date_picker = QDateEdit(calendarPopup=True)
        self.date_picker.setDate(QDate.currentDate())
        form_layout.addRow("Select Purchase Date:", self.date_picker)

        layout.addLayout(form_layout)

        self.save_button = QPushButton("Save Purchase")
        self.save_button.clicked.connect(self.save_purchase)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_purchase(self):
        product = self.product_input.currentText()
        quantity = self.quantity_input.text()
        unit_price = self.unit_price_input.text()
        supplier = self.supplier_input.currentText()
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

            cursor.execute("""
                INSERT INTO purchases (product, quantity, unit_price, total, supplier, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (product, quantity_val, unit_price_val, total, supplier, date))

            purchase_id = cursor.lastrowid

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

            self.generate_lpo_pdf(purchase_id, product, quantity_val, unit_price_val, total, supplier, date)

            QMessageBox.information(self, "Success", "Purchase recorded and stock updated successfully.")
            self.clear_fields()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving purchase: {e}")

    def clear_fields(self):
        self.quantity_input.clear()
        self.unit_price_input.clear()
        self.date_picker.setDate(QDate.currentDate())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PurchasesWindow()
    window.show()
    sys.exit(app.exec_())
