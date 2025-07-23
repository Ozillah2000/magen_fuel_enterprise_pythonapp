import sys
import csv
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QTabWidget,
    QDateEdit, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QDate
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

def get_connection():
    return sqlite3.connect('magen.db')

class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reports")
        self.resize(900, 500)
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_sales_report_tab(), "Sales Report")
        self.tabs.addTab(self.create_purchases_report_tab(), "Purchases Report")
        self.tabs.addTab(self.create_stock_report_tab(), "Stock Levels")
        self.tabs.addTab(self.create_low_stock_alerts_tab(), "Low Stock Alerts")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_sales_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Start Date:"))
        self.sales_start_date = QDateEdit(calendarPopup=True)
        self.sales_start_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.sales_start_date)

        date_layout.addWidget(QLabel("End Date:"))
        self.sales_end_date = QDateEdit(calendarPopup=True)
        self.sales_end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.sales_end_date)

        load_button = QPushButton("Load Sales Report")
        load_button.clicked.connect(self.load_sales_report)
        date_layout.addWidget(load_button)

        export_csv_button = QPushButton("Export CSV")
        export_csv_button.clicked.connect(lambda: self.export_to_csv(self.sales_table, "sales_report.csv"))
        date_layout.addWidget(export_csv_button)

        export_pdf_button = QPushButton("Export PDF")
        export_pdf_button.clicked.connect(lambda: self.export_to_pdf(self.sales_table, "sales_report.pdf", "Sales Report"))
        date_layout.addWidget(export_pdf_button)

        layout.addLayout(date_layout)

        self.sales_table = QTableWidget()
        layout.addWidget(self.sales_table)

        tab.setLayout(layout)
        return tab

    def create_purchases_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Start Date:"))
        self.purchases_start_date = QDateEdit(calendarPopup=True)
        self.purchases_start_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.purchases_start_date)

        date_layout.addWidget(QLabel("End Date:"))
        self.purchases_end_date = QDateEdit(calendarPopup=True)
        self.purchases_end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.purchases_end_date)

        load_button = QPushButton("Load Purchases Report")
        load_button.clicked.connect(self.load_purchases_report)
        date_layout.addWidget(load_button)

        export_csv_button = QPushButton("Export CSV")
        export_csv_button.clicked.connect(lambda: self.export_to_csv(self.purchases_table, "purchases_report.csv"))
        date_layout.addWidget(export_csv_button)

        export_pdf_button = QPushButton("Export PDF")
        export_pdf_button.clicked.connect(lambda: self.export_to_pdf(self.purchases_table, "purchases_report.pdf", "Purchases Report"))
        date_layout.addWidget(export_pdf_button)

        layout.addLayout(date_layout)

        self.purchases_table = QTableWidget()
        layout.addWidget(self.purchases_table)

        tab.setLayout(layout)
        return tab

    def create_stock_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        load_button = QPushButton("Load Stock Levels")
        load_button.clicked.connect(self.load_stock_report)
        btn_layout.addWidget(load_button)

        export_csv_button = QPushButton("Export CSV")
        export_csv_button.clicked.connect(lambda: self.export_to_csv(self.stock_table, "stock_levels_report.csv"))
        btn_layout.addWidget(export_csv_button)

        export_pdf_button = QPushButton("Export PDF")
        export_pdf_button.clicked.connect(lambda: self.export_to_pdf(self.stock_table, "stock_levels_report.pdf", "Stock Levels Report"))
        btn_layout.addWidget(export_pdf_button)

        layout.addLayout(btn_layout)

        self.stock_table = QTableWidget()
        layout.addWidget(self.stock_table)

        tab.setLayout(layout)
        return tab

    def create_low_stock_alerts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        load_button = QPushButton("Load Low Stock Alerts")
        load_button.clicked.connect(self.load_low_stock_alerts)
        btn_layout.addWidget(load_button)

        export_csv_button = QPushButton("Export CSV")
        export_csv_button.clicked.connect(lambda: self.export_to_csv(self.low_stock_table, "low_stock_alerts.csv"))
        btn_layout.addWidget(export_csv_button)

        export_pdf_button = QPushButton("Export PDF")
        export_pdf_button.clicked.connect(lambda: self.export_to_pdf(self.low_stock_table, "low_stock_alerts.pdf", "Low Stock Alerts Report"))
        btn_layout.addWidget(export_pdf_button)

        layout.addLayout(btn_layout)

        self.low_stock_table = QTableWidget()
        layout.addWidget(self.low_stock_table)

        tab.setLayout(layout)
        return tab

    def load_sales_report(self):
        conn = get_connection()
        cursor = conn.cursor()
        start_date = self.sales_start_date.date().toString("yyyy-MM-dd")
        end_date = self.sales_end_date.date().toString("yyyy-MM-dd")

        cursor.execute("""
            SELECT id, product, quantity, price, total, date, customer_name
            FROM sales
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC
        """, (start_date, end_date))

        data = cursor.fetchall()
        headers = ["ID", "Product", "Quantity", "Price", "Total", "Date", "Customer"]

        self.populate_table(self.sales_table, data, headers)
        conn.close()

        if data:
            total_sales = sum(float(row[4]) for row in data)
            total_qty = sum(int(row[2]) for row in data)
            QMessageBox.information(self, "Sales Summary",
                                    f"Total Quantity Sold: {total_qty}\nTotal Sales Amount: {total_sales:.2f}")

    def load_purchases_report(self):
        conn = get_connection()
        cursor = conn.cursor()
        start_date = self.purchases_start_date.date().toString("yyyy-MM-dd")
        end_date = self.purchases_end_date.date().toString("yyyy-MM-dd")

        cursor.execute("""
            SELECT id, product, quantity, unit_price, total, supplier, date
            FROM purchases
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC
        """, (start_date, end_date))

        data = cursor.fetchall()
        headers = ["ID", "Product", "Quantity", "Unit Price", "Total", "Supplier", "Date"]

        self.populate_table(self.purchases_table, data, headers)
        conn.close()

    def load_stock_report(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, product, quantity, reorder_level
            FROM stock
            ORDER BY product ASC
        """)
        data = cursor.fetchall()
        headers = ["ID", "Product", "Quantity", "Reorder Level"]

        self.populate_table(self.stock_table, data, headers)
        conn.close()

    def load_low_stock_alerts(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, product, quantity, reorder_level
            FROM stock
            WHERE quantity <= reorder_level
            ORDER BY product ASC
        """)
        data = cursor.fetchall()
        headers = ["ID", "Product", "Quantity", "Reorder Level"]

        self.populate_table(self.low_stock_table, data, headers)
        conn.close()

    def populate_table(self, table, data, headers):
        table.clear()
        table.setRowCount(len(data))
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        for row_idx, row in enumerate(data):
            for col_idx, item in enumerate(row):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

    def export_to_csv(self, table, default_filename):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV Report", default_filename, "CSV Files (*.csv)")
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
                    writer.writerow(headers)
                    for row in range(table.rowCount()):
                        row_data = []
                        for col in range(table.columnCount()):
                            item = table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                QMessageBox.information(self, "Success", f"Report exported successfully:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export CSV:\n{e}")

    def export_to_pdf(self, table, default_filename, report_title):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", default_filename, "PDF Files (*.pdf)")
        if file_path:
            try:
                c = canvas.Canvas(file_path, pagesize=A4)
                width, height = A4
                c.setFont("Helvetica-Bold", 16)
                c.drawString(30, height - 50, report_title)

                data = []
                headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
                data.append(headers)
                for row in range(table.rowCount()):
                    row_data = []
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)

                table_obj = Table(data, repeatRows=1)
                table_obj.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))

                table_width, table_height = table_obj.wrapOn(c, width - 60, height - 100)
                table_obj.drawOn(c, 30, height - 80 - table_height)

                c.save()
                QMessageBox.information(self, "Success", f"Report exported successfully:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export PDF:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportsWindow()
    window.show()
    sys.exit(app.exec_())
