# dashboard.py

from PyQt5 import QtWidgets, QtCore, QtGui
import sys
from datetime import datetime
from sales import SalesWindow
from purchases import PurchasesWindow
from customers import CustomersWindow
from suppliers import SuppliersWindow
from stock_manager import get_low_stock_alerts
from reports import ReportsWindow

class DashboardWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magen Business Enterprise - Dashboard")
        self.setGeometry(100, 100, 1000, 600)
        self.init_ui()

    def init_ui(self):
        # Main container
        self.container = QtWidgets.QWidget()
        self.setCentralWidget(self.container)

        # Layouts
        self.main_layout = QtWidgets.QHBoxLayout(self.container)
        self.sidebar_layout = QtWidgets.QVBoxLayout()
        self.content_layout = QtWidgets.QVBoxLayout()

        # Sidebar
        self.sidebar = QtWidgets.QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #0A2647; color: white;")

        # Date/time label
        self.datetime_label = QtWidgets.QLabel()
        self.datetime_label.setAlignment(QtCore.Qt.AlignCenter)
        self.datetime_label.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))

        self.update_datetime()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

        # Sidebar buttons
        buttons = ["Dashboard", "Sales", "Purchases", "Customers", "Suppliers", "Reports", "Logout"]
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
        self.sidebar_layout.addWidget(self.datetime_label)
        self.sidebar.setLayout(self.sidebar_layout)

        # Content area
        self.content = QtWidgets.QFrame()
        self.content.setStyleSheet("background-color: #f1f1f1;")
        self.content_layout.setAlignment(QtCore.Qt.AlignTop)

        self.header = QtWidgets.QLabel("Welcome to Magen Business Enterprise")
        self.header.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Bold))
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.content_layout.addWidget(self.header)

        self.info_label = QtWidgets.QLabel("Dashboard Content Area")
        self.info_label.setFont(QtGui.QFont("Segoe UI", 12))
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.content_layout.addWidget(self.info_label)

        self.content.setLayout(self.content_layout)

        # Add to main layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content)

    def update_datetime(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alerts = get_low_stock_alerts()
        if alerts:
            self.datetime_label.setText(f"{current_time} | Low Stock Alerts: {', '.join(alerts)}")
        else:
            self.datetime_label.setText(current_time)

    def navigate(self, page_name):
        if page_name == "Sales":
            self.open_sales_window()
        elif page_name == "Purchases":
            self.open_purchases_window()
        elif page_name == "Customers":
            self.open_customers_window()
        elif page_name == "Suppliers":
            self.open_suppliers_window()
        elif page_name == "Reports":
            self.open_reports_window()
        elif page_name == "Logout":
            self.close()
        else:
            self.info_label.setText(f"{page_name} Page (Coming Soon...)")

    def open_sales_window(self):
        self.sales_window = SalesWindow()
        self.sales_window.show()

    def open_purchases_window(self):
        self.purchases_window = PurchasesWindow()
        self.purchases_window.show()

    def open_customers_window(self):
        self.customers_window = CustomersWindow()
        self.customers_window.show()

    def open_suppliers_window(self):
        self.suppliers_window = SuppliersWindow()
        self.suppliers_window.show()

    def open_reports_window(self):
        self.reports_window = ReportsWindow()
        self.reports_window.show()

# For standalone testing
if __name__ == "__main__":
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
