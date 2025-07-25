# migrate_users_table.py
import sqlite3

conn = sqlite3.connect("magen.db")
cursor = conn.cursor()

# Add 'role' column if it does not exist
try:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'employee'")
    print("✅ 'role' column added to users table with default 'employee'")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ 'role' column already exists, skipping.")
    else:
        print(f"Error: {e}")

conn.commit()
conn.close()
