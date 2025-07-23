import sqlite3

def get_connection():
    return sqlite3.connect('magen.db')

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Sales Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        quantity REAL,
        price REAL,
        total REAL,
        date TEXT,
        lpo_path TEXT,
        invoice_path TEXT,
        delivery_note_path TEXT,
        receipt_path TEXT,
        customer_name TEXT
    )
    """)

    # Purchases Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        quantity REAL,
        unit_price REAL,
        total REAL,
        supplier TEXT,
        date TEXT,
        lpo_path TEXT,
        invoice_path TEXT,
        delivery_note_path TEXT,
        receipt_path TEXT
    )
    """)

    # Customers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        phone TEXT,
        email TEXT,
        address TEXT
    )
    """)

    # Suppliers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        products_supplied TEXT
    )
    """)
    # Stock table for automated stock tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT UNIQUE,
            quantity REAL DEFAULT 0
        )
    """)

    # Prepopulate stock with products if not already
    products = ["PMS", "AGO", "IK", "Gas"]
    for product in products:
        cursor.execute("INSERT OR IGNORE INTO stock (product, quantity) VALUES (?, ?)", (product, 0))

    conn.commit()
    conn.close()

# Create tables automatically when the script is run
if __name__ == "__main__":
    create_tables()
    print("All tables created or verified successfully.")
