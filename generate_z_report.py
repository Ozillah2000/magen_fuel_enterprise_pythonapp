import sqlite3
from datetime import datetime
from fpdf import FPDF
import os

DB_FILE = 'magen.db'

def generate_z_report(auto_print=False):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Get today's date
        today_str = datetime.now().strftime('%Y-%m-%d')

        # Fetch total sales for today
        cursor.execute("""
            SELECT SUM(total) FROM sales
            WHERE DATE(date) = ?
        """, (today_str,))
        total_sales = cursor.fetchone()[0] or 0

        # Fetch breakdown per product
        cursor.execute("""
            SELECT product, SUM(quantity), SUM(total) FROM sales
            WHERE DATE(date) = ?
            GROUP BY product
        """, (today_str,))
        product_summary = cursor.fetchall()

        # Optional: Fetch sales count
        cursor.execute("""
            SELECT COUNT(*) FROM sales
            WHERE DATE(date) = ?
        """, (today_str,))
        total_transactions = cursor.fetchone()[0] or 0

        conn.close()

        # Prepare report directory
        report_dir = os.path.join(os.getcwd(), "documents", "reports")
        os.makedirs(report_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"Z_Report_{timestamp}.pdf"
        report_path = os.path.join(report_dir, report_filename)

        # Generate PDF report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "End-of-Day Z Report", ln=True, align='C')

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Date: {today_str}", ln=True)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(0, 10, "", ln=True)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Total Sales: NGN {total_sales:,.2f}", ln=True)
        pdf.cell(0, 10, f"Total Transactions: {total_transactions}", ln=True)
        pdf.cell(0, 10, "", ln=True)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Sales Breakdown by Product:", ln=True)
        pdf.set_font("Arial", size=12)
        if product_summary:
            for prod, qty, amt in product_summary:
                pdf.cell(0, 8, f"{prod}: {qty} units, NGN {amt:,.2f}", ln=True)
        else:
            pdf.cell(0, 8, "No sales recorded today.", ln=True)

        pdf.output(report_path)

        print(f"✅ Z Report generated successfully: {report_path}")

        if auto_print:
            auto_print_pdf(report_path)

    except Exception as e:
        print(f"❌ Failed to generate Z Report: {e}")

def auto_print_pdf(file_path):
    """
    Opens the PDF for printing using the default system viewer.
    Works on Windows; adjust if using Linux/Mac.
    """
    try:
        os.startfile(file_path, "print")
        print("✅ Sent Z Report to printer.")
    except Exception as e:
        print(f"❌ Failed to auto-print: {e}")

if __name__ == "__main__":
    generate_z_report(auto_print=False)
