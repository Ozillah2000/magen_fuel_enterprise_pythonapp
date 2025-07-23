import sqlite3

conn = sqlite3.connect("magen.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS purchases")

cursor.execute("""
CREATE TABLE purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    quantity INTEGER,
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

conn.commit()
conn.close()

print("✅ Purchases table recreated with attachment columns.")
