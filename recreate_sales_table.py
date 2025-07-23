import sqlite3

conn = sqlite3.connect("magen.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS sales")

cursor.execute("""
CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    quantity INTEGER,
    price REAL,
    total REAL,
    date TEXT,
    lpo_path TEXT,
    invoice_path TEXT,
    delivery_note_path TEXT,
    receipt_path TEXT
)
""")

conn.commit()
conn.close()

print("✅ Sales table recreated with required columns.")
