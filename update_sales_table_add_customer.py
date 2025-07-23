# update_sales_table_add_customer.py
import sqlite3

conn = sqlite3.connect("magen.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE sales ADD COLUMN customer_name TEXT")
    print("✅ 'customer_name' column added to 'sales' table.")
except sqlite3.OperationalError:
    print("⚠️ 'customer_name' column already exists or another error occurred.")

conn.commit()
conn.close()
