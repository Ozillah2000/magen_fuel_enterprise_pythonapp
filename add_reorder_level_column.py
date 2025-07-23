import sqlite3
import os

def add_reorder_level_column(db_file):
    if not os.path.exists(db_file):
        print(f"[❌] Database {db_file} does not exist.")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(stock)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Columns in 'stock' table of {db_file}:", columns)

    if 'reorder_level' not in columns:
        cursor.execute("ALTER TABLE stock ADD COLUMN reorder_level REAL DEFAULT 500")
        print(f"[✅] 'reorder_level' column added to 'stock' table in {db_file}.")
    else:
        print(f"[ℹ️] 'reorder_level' column already exists in {db_file}.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    for db in ["magen.db", "magen_fuel.db"]:
        add_reorder_level_column(db)
