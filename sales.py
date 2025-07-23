import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QFileDialog, QDateEdit, QFormLayout
)
from PyQt5.QtCore import QDate
from stock_manager import update_stock_on_sale, can_sell

DB_FILE = 'magen.db'

class SalesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Record Sale")
        self.setGeometry(200, 200, 400, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Product Dropdown
        self.product_cb = QComboBox()
        self.product_cb.addItems(["PMS", "AGO", "IK", "Gas"])
        form_layout.addRow(QLabel("Select Product:"), self.product_cb)

        # Quantity
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Enter Quantity")
        form_layout.addRow(QLabel("Quantity:"), self.quantity_input)

        # Price
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Enter Price per Unit")
        form_layout.addRow(QLabel("Price per Unit:"), self.price_input)

        # Date Picker
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Select Date:"), self.date_input)

        # Customer Name
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Enter Customer Name")
        form_layout.addRow(QLabel("Customer Name:"), self.customer_name_input)

        # Attachments
        self.lpo_btn = QPushButton("Attach LPO")
        self.lpo_btn.clicked.connect(lambda: self.attach_file('lpo'))
        self.invoice_btn = QPushButton("Attach Invoice")
        self.invoice_btn.clicked.connect(lambda: self.attach_file('invoice'))
        self.delivery_btn = QPushButton("Attach Delivery Note")
        self.delivery_btn.clicked.connect(lambda: self.attach_file('delivery'))
        self.receipt_btn = QPushButton("Attach Receipt")
        self.receipt_btn.clicked.connect(lambda: self.attach_file('receipt'))

        form_layout.addRow(self.lpo_btn, self.invoice_btn)
        form_layout.addRow(self.delivery_btn, self.receipt_btn)

        # Submit Button
        self.submit_btn = QPushButton("Record Sale")
        self.submit_btn.clicked.connect(self.record_sale)

        layout.addLayout(form_layout)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)

        # Attachment paths
        self.lpo_path = ""
        self.invoice_path = ""
        self.delivery_note_path = ""
        self.receipt_path = ""

    def attach_file(self, file_type):
        path, _ = QFileDialog.getOpenFileName(self, f"Attach {file_type.upper()}", "", "All Files (*)")
        if path:
            if file_type == 'lpo':
                self.lpo_path = path
                QMessageBox.information(self, "File Attached", f"LPO attached successfully.")
            elif file_type == 'invoice':
                self.invoice_path = path
                QMessageBox.information(self, "File Attached", f"Invoice attached successfully.")
            elif file_type == 'delivery':
                self.delivery_note_path = path
                QMessageBox.information(self, "File Attached", f"Delivery Note attached successfully.")
            elif file_type == 'receipt':
                self.receipt_path = path
                QMessageBox.information(self, "File Attached", f"Receipt attached successfully.")

    def record_sale(self):
        product = self.product_cb.currentText()
        quantity = self.quantity_input.text().strip()
        price = self.price_input.text().strip()
        customer_name = self.customer_name_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")

        if not quantity or not price or not customer_name:
            QMessageBox.warning(self, "Input Error", "Please fill all required fields.")
            return

        try:
            quantity = float(quantity)
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Quantity and Price must be numeric.")
            return

        # 🚩 Enforce reorder level check before allowing sale
        can_proceed, current_qty, reorder_level = can_sell(product, quantity)
        if not can_proceed:
            QMessageBox.warning(
                self,
                "Reorder Level Warning",
                f"Cannot proceed:\n"
                f"Selling {quantity} {product} would drop stock below reorder level.\n\n"
                f"Current Stock: {current_qty}\n"
                f"Reorder Level: {reorder_level}"
            )
            return

        total = quantity * price

        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sales (product, quantity, price, total, date,
                                   lpo_path, invoice_path, delivery_note_path, receipt_path, customer_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product, quantity, price, total, date,
                self.lpo_path, self.invoice_path,
                self.delivery_note_path, self.receipt_path,
                customer_name
            ))
            conn.commit()
            conn.close()

            update_stock_on_sale(product, quantity)

            QMessageBox.information(self, "Success", "Sale recorded successfully.")
            self.clear_inputs()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def clear_inputs(self):
        self.quantity_input.clear()
        self.price_input.clear()
        self.customer_name_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.lpo_path = ""
        self.invoice_path = ""
        self.delivery_note_path = ""
        self.receipt_path = ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SalesWindow()
    window.show()
    sys.exit(app.exec_())
