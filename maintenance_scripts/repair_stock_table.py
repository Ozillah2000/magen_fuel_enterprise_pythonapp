import sqlite3

def repair_stock_table():
    conn = sqlite3.connect('magen.db')
    cursor = conn.cursor()

    # Create stock table if missing
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT UNIQUE,
            quantity REAL DEFAULT 0
        )
    """)

    # Prepopulate essential products if not already
    products = ["PMS", "AGO", "IK", "Gas"]
    for product in products:
        cursor.execute("INSERT OR IGNORE INTO stock (product, quantity) VALUES (?, ?)", (product, 0))

    conn.commit()
    conn.close()
    print("[✅] Stock table verified and repaired successfully.")

if __name__ == "__main__":
    repair_stock_table()
