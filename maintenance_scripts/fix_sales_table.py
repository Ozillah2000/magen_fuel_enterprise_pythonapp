import sqlite3

DB_FILE = 'magen.db'

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE sales ADD COLUMN invoice_number INTEGER;")
except sqlite3.OperationalError:
    print("Column 'invoice_number' already exists.")

try:
    cursor.execute("ALTER TABLE sales ADD COLUMN delivery_note_number INTEGER;")
except sqlite3.OperationalError:
    print("Column 'delivery_note_number' already exists.")

conn.commit()
conn.close()

print("Columns ensured.")
