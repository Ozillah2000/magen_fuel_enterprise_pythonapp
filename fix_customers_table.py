import sqlite3

DB_FILE = 'magen.db'

def fix_customers_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Backup old data if needed
    try:
        cursor.execute("ALTER TABLE customers RENAME TO customers_backup;")
    except Exception:
        pass  # In case it doesn't exist, ignore

    # Create correct table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        address TEXT,
        phone TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("Customers table fixed successfully.")

if __name__ == "__main__":
    fix_customers_table()
