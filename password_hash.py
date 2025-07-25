# migrate_add_password_hash.py
import sqlite3

conn = sqlite3.connect("magen.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    print("✅ 'password_hash' column added to users table.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ 'password_hash' column already exists, skipping.")
    else:
        print(f"Error: {e}")

conn.commit()
conn.close()
