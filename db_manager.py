import sqlite3
import os

DB_PATH = 'fashion.db'

def update_db(items_dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    for v_id, item in items_dict.items():
        url = item.get('productUrl')
        if not url: continue

        # --- Ensure Price is a number, not a dictionary ---
        price_raw = item.get('price')
        if isinstance(price_raw, dict):
            price = price_raw.get('amount') # Extract '25.00' from the dict
        else:
            price = price_raw

        c.execute('''
            INSERT OR REPLACE INTO products 
            (productUrl, productName, brandName, price, imageUrl, shop, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            url, 
            item.get('productName'), 
            item.get('brandName'), 
            price, # Now a safe string/number
            item.get('imageUrl'), 
            item.get('shop'), 
            item.get('category')
        ))
    
    conn.commit()
    conn.close()
    print(f"Successfully synced {len(items_dict)} items to {DB_PATH}")

def get_all_products():
    """Fetches all items from the database for the AI to read."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # This is CRITICAL for app.py to work
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows