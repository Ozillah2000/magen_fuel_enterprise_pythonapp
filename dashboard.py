from PyQt5 import QtWidgets, QtCore, QtGui 
import pyqtgraph as pg
import sqlite3
from datetime import datetime
from sales import SalesWindow
from purchases import PurchasesWindow
from customers import CustomersWindow
from suppliers import SuppliersWindow
from reports import ReportsWindow
from stock_manager import get_low_stock_alerts, get_current_stock_levels
from themes1 import apply_gradient_theme
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QMessageBox
)

DB_PATH = "magen.db"

class DashboardWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magen Business Enterprise - Dashboard")
        self.setGeometry(100, 100, 1100, 650)
        apply_gradient_theme(self, theme="dark")
        self.init_ui()

    def init_ui(self):
        self.container = QtWidgets.QWidget()
        self.setCentralWidget(self.container)

        self.main_layout = QtWidgets.QVBoxLayout(self.container)
        self.body_layout = QtWidgets.QHBoxLayout()

        # === Header ===
        header = QtWidgets.QLabel("Magen Business Enterprise - Dashboard")
        header.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Bold))
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("background-color: #0A2647; color: white; padding: 12px;")
        self.main_layout.addWidget(header)

        # === Sidebar ===
        self.sidebar = QtWidgets.QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #0A2647; color: white;")
        self.sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar)

        # Marquee
        self.marquee_label = QtWidgets.QLabel()
        self.marquee_label.setAlignment(QtCore.Qt.AlignCenter)
        self.marquee_label.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
        self.marquee_label.setStyleSheet("color: yellow; background-color: #0A2647;")
        self.sidebar_layout.addWidget(self.marquee_label)

        self.marquee_text = ""
        self.marquee_index = 0
        self.update_marquee_text()

        self.marquee_timer = QtCore.QTimer()
        self.marquee_timer.timeout.connect(self.scroll_marquee)
        self.marquee_timer.start(150)

        self.alert_refresh_timer = QtCore.QTimer()
        self.alert_refresh_timer.timeout.connect(self.update_marquee_text)
        self.alert_refresh_timer.start(10000)

        # Navigation buttons
        buttons = ["Dashboard", "Sales", "Purchases", "Customers", "Suppliers", "Reports", "Toggle Theme", "Logout"]
        for btn_text in buttons:
            btn = QtWidgets.QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #144272;
                    color: white;
                    padding: 10px;
                    border: none;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #205295;
                }
            """)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.clicked.connect(lambda checked, t=btn_text: self.navigate(t))
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch()

        # Clock
        self.datetime_label = QtWidgets.QLabel()
        self.datetime_label.setAlignment(QtCore.Qt.AlignCenter)
        self.datetime_label.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
        self.datetime_label.setStyleSheet("color: white; background-color: #0A2647; padding: 5px;")
        self.sidebar_layout.addWidget(self.datetime_label)

        self.update_datetime()
        self.clock_timer = QtCore.QTimer()
        self.clock_timer.timeout.connect(self.update_datetime)
        self.clock_timer.start(1000)

        # === Content ===
        self.content = QtWidgets.QFrame()
        self.content.setStyleSheet("background-color: #f1f1f1;")
        self.content_layout = QtWidgets.QVBoxLayout(self.content)

        # Summary Cards
        summary_layout = QtWidgets.QHBoxLayout()
        summary_layout.setSpacing(20)

        sales_total, purchases_total = self.get_summary_totals()
        stock_levels = get_current_stock_levels()
        total_stock_items = sum(stock_levels.values())

        self.sales_card, self.sales_value_label = self.create_summary_card(
            "Total Sales", f"Ksh {sales_total:,.2f}", "#0A2647"
        )
        self.purchases_card, self.purchases_value_label = self.create_summary_card(
            "Total Purchases", f"Ksh {purchases_total:,.2f}", "#144272"
        )
        self.stock_card, self.stock_value_label = self.create_summary_card(
            "Current Stock Units", f"{total_stock_items} Lts", "#205295"
        )

        summary_layout.addWidget(self.sales_card)
        summary_layout.addWidget(self.purchases_card)
        summary_layout.addWidget(self.stock_card)

        self.content_layout.addLayout(summary_layout)
        self.content_layout.addSpacing(10)

        # Refresh Button
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #144272;
                color: white;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #205295;
            }
        """)
        refresh_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        refresh_btn.clicked.connect(self.refresh_summary_cards)
        self.content_layout.addWidget(refresh_btn, alignment=QtCore.Qt.AlignCenter)

        # ✅ Z Report Button (added visibly below refresh button)
        self.generate_z_report_button = QtWidgets.QPushButton("🧾 Generate Z Report")
        self.generate_z_report_button.setStyleSheet("""
            QPushButton {
                background-color: #144272;
                color: white;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #205295;
            }
        """)
        self.generate_z_report_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.generate_z_report_button.clicked.connect(self.generate_z_report)
        self.content_layout.addWidget(self.generate_z_report_button, alignment=QtCore.Qt.AlignCenter)

        # Graph
        self.graph_widget = pg.PlotWidget(title="Daily Sales & Purchases")
        self.graph_widget.setBackground('w')
        self.graph_widget.showGrid(x=True, y=True)
        self.graph_widget.addLegend()

        # Placeholder data for now
        days = list(range(1, 8))
        sales_data = [150, 200, 180, 250, 300, 280, 320]
        purchases_data = [100, 150, 130, 200, 180, 170, 210]

        self.graph_widget.plot(days, sales_data, pen=pg.mkPen(color='b', width=2), name='Sales')
        self.graph_widget.plot(days, purchases_data, pen=pg.mkPen(color='g', width=2), name='Purchases')
        self.graph_widget.setFixedHeight(350)

        self.content_layout.addWidget(self.graph_widget)

        self.body_layout.addWidget(self.sidebar)
        self.body_layout.addWidget(self.content)
        self.main_layout.addLayout(self.body_layout)

        # Auto-refresh every 15 seconds
        self.summary_refresh_timer = QtCore.QTimer()
        self.summary_refresh_timer.timeout.connect(self.refresh_summary_cards)
        self.summary_refresh_timer.start(15000)

    def update_datetime(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.datetime_label.setText(current_time)

    def create_summary_card(self, title, value, color):
        card = QtWidgets.QFrame()
        card.setFixedSize(250, 100)
        card.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px;")
        card_layout = QtWidgets.QVBoxLayout(card)

        title_label = QtWidgets.QLabel(title)
        title_label.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold))
        title_label.setAlignment(QtCore.Qt.AlignCenter)

        value_label = QtWidgets.QLabel(value)
        value_label.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold))
        value_label.setAlignment(QtCore.Qt.AlignCenter)

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)

        return card, value_label

    def get_summary_totals(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT SUM(total) FROM sales")
            sales_total = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(total) FROM purchases")
            purchases_total = cursor.fetchone()[0] or 0

            conn.close()
            return sales_total, purchases_total

        except Exception as e:
            print(f"Error fetching summary totals: {e}")
            return 0, 0

    def refresh_summary_cards(self):
        sales_total, purchases_total = self.get_summary_totals()
        self.sales_value_label.setText(f"Ksh {sales_total:,.2f}")
        self.purchases_value_label.setText(f"Ksh {purchases_total:,.2f}")

        stock_levels = get_current_stock_levels()
        total_stock_items = sum(stock_levels.values())
        self.stock_value_label.setText(f"{total_stock_items} Lts")

    def update_marquee_text(self):
        alerts = get_low_stock_alerts()
        if alerts:
            self.marquee_text = " | ".join([f"{item} is low" for item in alerts]) + "     "
        else:
            self.marquee_text = "All stocks are sufficient.     "
        self.marquee_index = 0

    def scroll_marquee(self):
        if self.marquee_text:
            display_text = self.marquee_text[self.marquee_index:] + self.marquee_text[:self.marquee_index]
            self.marquee_label.setText(display_text)
            self.marquee_index = (self.marquee_index + 1) % len(self.marquee_text)

    def navigate(self, page_name):
        if page_name == "Sales":
            self.sales_window = SalesWindow()
            self.sales_window.show()
        elif page_name == "Purchases":
            self.purchases_window = PurchasesWindow()
            self.purchases_window.show()
        elif page_name == "Customers":
            self.customers_window = CustomersWindow()
            self.customers_window.show()
        elif page_name == "Suppliers":
            self.suppliers_window = SuppliersWindow()
            self.suppliers_window.show()
        elif page_name == "Reports":
            self.reports_window = ReportsWindow()
            self.reports_window.show()
        elif page_name == "Toggle Theme":
            current_theme = getattr(self, 'current_theme', 'dark')
            new_theme = 'light' if current_theme == 'dark' else 'dark'
            apply_gradient_theme(self, theme=new_theme)
            self.current_theme = new_theme
        elif page_name == "Logout":
            self.close()

    def generate_z_report(self):
        import generate_z_report
        generate_z_report.generate_z_report()
        QMessageBox.information(self, "Z Report", "Z Report generated successfully!")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    from login import LoginWindow

    login_window = LoginWindow()

    def on_login_success():
        login_window.close()
        dashboard = DashboardWindow()
        dashboard.show()

    login_window.login_success.connect(on_login_success)
    login_window.show()
    sys.exit(app.exec_())
