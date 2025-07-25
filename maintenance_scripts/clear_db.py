import sqlite3

# Connect to your database
conn = sqlite3.connect("magen.db")
cursor = conn.cursor()

# List of tables to clear (excluding 'users')
tables = ["stock", "customers", "suppliers", "purchases", "sales"]

# Disable foreign key checks for clearing
cursor.execute("PRAGMA foreign_keys = OFF;")

# Clear each table
for table in tables:
    try:
        cursor.execute(f"DELETE FROM {table}")
        print(f"✅ Cleared all records in '{table}' table.")
    except Exception as e:
        print(f"⚠️ Could not clear table '{table}': {e}")

# Enable foreign key checks back
cursor.execute("PRAGMA foreign_keys = ON;")

conn.commit()
conn.close()
print("✅ Database records cleared successfully (users preserved).")
