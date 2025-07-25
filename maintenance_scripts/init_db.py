# init_db.py

import sqlite3

DATABASE_NAME = "magen.db"

conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Create customers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    email TEXT,
    address TEXT
)
""")

# Create suppliers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    contact TEXT,
    email TEXT,
    address TEXT
)
""")

# Create stock table
cursor.execute("""
CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    quantity INTEGER,
    reorder_level INTEGER
)
""")

# Create sales table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    quantity INTEGER,
    price REAL,
    total REAL,
    date TEXT,
    customer_name TEXT
)
""")

# Create purchases table
cursor.execute("""
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    quantity INTEGER,
    unit_price REAL,
    total REAL,
    supplier TEXT,
    date TEXT
)
""")

# -------------------------------------------
# Ensure purchases and sales tables have lpo, invoice, receipt, delivery_note columns

def add_column_if_not_exists(table_name, column_name, column_type):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        print(f"✅ Added column '{column_name}' to '{table_name}' table.")
    else:
        print(f"ℹ️ Column '{column_name}' already exists in '{table_name}' table.")

# Add missing columns to purchases
for col in ["lpo", "invoice", "receipt", "delivery_note"]:
    add_column_if_not_exists("purchases", col, "TEXT")

# Add missing columns to sales
for col in ["lpo", "invoice", "receipt", "delivery_note"]:
    add_column_if_not_exists("sales", col, "TEXT")

# -------------------------------------------
# Insert admin user if not exists
cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))
    print("✅ Admin user created with username: admin, password: admin123")
else:
    print("ℹ️ Admin user already exists.")

# Insert sample stock data if empty
cursor.execute("SELECT COUNT(*) FROM stock")
count = cursor.fetchone()[0]
if count == 0:
    sample_stock = [
        ("Fuel A", 50, 60),
        ("Fuel B", 30, 40),
        ("Fuel C", 80, 100),
        ("Fuel D", 15, 50)  # Triggers low stock alert
    ]
    cursor.executemany("INSERT INTO stock (product, quantity, reorder_level) VALUES (?, ?, ?)", sample_stock)
    print("✅ Sample stock data inserted.")
else:
    print("ℹ️ Stock table already has data.")

# Commit and close cleanly
conn.commit()
conn.close()

print("✅ Database initialization and migration complete.")
