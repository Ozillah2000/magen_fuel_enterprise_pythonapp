import sys
import os
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QDateEdit, QFormLayout
)
from PyQt5.QtCore import QDate
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt5.QtGui import QPainter

from stock_manager import update_stock_on_sale, can_sell
from themes import apply_gradient_theme
from pdf_generator import generate_invoice_pdf_document, generate_delivery_note_pdf_document

DB_FILE = 'magen.db'

class SalesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Record Sale")
        self.setGeometry(200, 200, 400, 400)
        self.init_ui()
        apply_gradient_theme(self)

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

        # Editable Customer Dropdown
        self.customer_cb = QComboBox()
        self.customer_cb.setEditable(True)
        self.load_customers()
        form_layout.addRow(QLabel("Customer Name:"), self.customer_cb)

        # Submit Button
        self.submit_btn = QPushButton("Record Sale")
        self.submit_btn.clicked.connect(self.record_sale)

        layout.addLayout(form_layout)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)

    def load_customers(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM customers ORDER BY name ASC")
            customers = cursor.fetchall()
            conn.close()

            self.customer_cb.clear()
            for cust in customers:
                self.customer_cb.addItem(cust[0])
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load customers:\n{e}")

    def record_sale(self):
        product = self.product_cb.currentText()
        quantity = self.quantity_input.text().strip()
        price = self.price_input.text().strip()
        customer_name = self.customer_cb.currentText().strip()
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

            # Add customer if it does not exist
            cursor.execute("SELECT id FROM customers WHERE name = ?", (customer_name,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO customers (name) VALUES (?)", (customer_name,))
                conn.commit()

            cursor.execute("SELECT MAX(invoice_number) FROM sales")
            last_invoice = cursor.fetchone()[0] or 0
            invoice_number = last_invoice + 1

            cursor.execute("SELECT MAX(delivery_note_number) FROM sales")
            last_delivery_note = cursor.fetchone()[0] or 0
            delivery_note_number = last_delivery_note + 1

            cursor.execute("""
                INSERT INTO sales (
                    product, quantity, price, total, date,
                    customer_name, invoice_number, delivery_note_number
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product, quantity, price, total, date,
                customer_name, invoice_number, delivery_note_number
            ))

            conn.commit()
            conn.close()

            update_stock_on_sale(product, quantity)

            sale_data = {
                'product': product,
                'quantity': quantity,
                'price': price,
                'total': total,
                'date': date,
                'customer_name': customer_name
            }

            save_dir = os.path.join(os.getcwd(), "documents")
            os.makedirs(save_dir, exist_ok=True)

            invoice_pdf_path = os.path.join(save_dir, f"Invoice_{invoice_number}.pdf")
            delivery_note_pdf_path = os.path.join(save_dir, f"DeliveryNote_{delivery_note_number}.pdf")

            generate_invoice_pdf_document(invoice_number, sale_data, invoice_pdf_path)
            generate_delivery_note_pdf_document(delivery_note_number, sale_data, delivery_note_pdf_path)

            self.print_pdf_with_preview(invoice_pdf_path)
            self.print_pdf_with_preview(delivery_note_pdf_path)

            QMessageBox.information(
                self,
                "Success",
                f"Sale recorded successfully.\n\n"
                f"Invoice: {invoice_pdf_path}\n"
                f"Delivery Note: {delivery_note_pdf_path}"
            )

            self.clear_inputs()
            self.load_customers()  # Refresh customer list after new entry

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def print_pdf_with_preview(self, file_path):
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            printer.setFullPage(True)

            dialog = QPrintDialog(printer, self)
            dialog.setWindowTitle("Select Printer")

            if dialog.exec_() == QPrintDialog.Accepted:
                preview = QPrintPreviewDialog(printer, self)
                preview.setWindowTitle("Print Preview: " + os.path.basename(file_path))
                preview.paintRequested.connect(lambda p: self.render_pdf_on_printer(file_path, p))
                preview.exec_()

        except Exception as e:
            QMessageBox.warning(self, "Print Error", f"Error printing {file_path}:\n{e}")

    def render_pdf_on_printer(self, file_path, printer):
        try:
            from PyQt5.QtPdf import QPdfDocument

            pdf_doc = QPdfDocument()
            status = pdf_doc.load(file_path)
            if status != QPdfDocument.NoError:
                QMessageBox.warning(self, "PDF Load Error", f"Could not load PDF: {file_path}")
                return

            painter = QPainter(printer)
            for page in range(pdf_doc.pageCount()):
                if page != 0:
                    printer.newPage()
                image = pdf_doc.render(page)
                painter.drawImage(0, 0, image)
            painter.end()

        except ImportError:
            QMessageBox.warning(self, "Missing QtPdf", "Your PyQt5 build lacks QtPdf. Please install it to enable PDF rendering on print preview.")

    def clear_inputs(self):
        self.quantity_input.clear()
        self.price_input.clear()
        self.customer_cb.setEditText("")
        self.date_input.setDate(QDate.currentDate())
        self.product_cb.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SalesWindow()
    window.show()
    sys.exit(app.exec_())
