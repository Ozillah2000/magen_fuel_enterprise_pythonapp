import sqlite3

DB_FILE = 'magen.db'

def get_connection():
    return sqlite3.connect(DB_FILE)

def get_current_stock_levels():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product, quantity FROM stock")
    stocks = cursor.fetchall()
    conn.close()
    return {product: quantity for product, quantity in stocks}

def update_stock_on_sale(product, quantity_sold):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM stock WHERE product = ?", (product,))
    result = cursor.fetchone()
    if result:
        current_quantity = result[0]
        new_quantity = current_quantity - quantity_sold
        if new_quantity < 0:
            new_quantity = 0  # Prevent negative quantities; adjust as needed
        cursor.execute("UPDATE stock SET quantity = ? WHERE product = ?", (new_quantity, product))
        conn.commit()
    conn.close()

def update_stock_on_purchase(product, quantity_purchased):
    """
    Adds purchased quantity to stock.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM stock WHERE product = ?", (product,))
    result = cursor.fetchone()
    if result:
        current_quantity = result[0]
        new_quantity = current_quantity + quantity_purchased
        cursor.execute("UPDATE stock SET quantity = ? WHERE product = ?", (new_quantity, product))
        conn.commit()
    conn.close()

def can_sell(product, quantity_requested):
    """
    Prevent sales if it will drop stock below reorder level.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity, reorder_level FROM stock WHERE product = ?", (product,))
    result = cursor.fetchone()
    conn.close()
    if result:
        current_qty, reorder_level = result
        if current_qty - quantity_requested < reorder_level:
            return False, current_qty, reorder_level
        else:
            return True, current_qty, reorder_level
    else:
        return False, 0, 0

def get_low_stock_alerts():
    """
    Returns a list of products where current stock <= reorder level.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product, quantity, reorder_level FROM stock")
    products = cursor.fetchall()
    conn.close()
    alerts = []
    for product, qty, reorder in products:
        if qty <= reorder:
            alerts.append(f"{product} is low: {qty}L left (Reorder Level: {reorder}L)")
    return alerts

if __name__ == "__main__":
    print("Current stock levels:", get_current_stock_levels())
    alerts = get_low_stock_alerts()
    if alerts:
        print("Low stock alerts:")
        for alert in alerts:
            print(alert)
    else:
        print("All stocks are above reorder levels.")
