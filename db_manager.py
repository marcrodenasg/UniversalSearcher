import sqlite3
import os

DB_PATH = 'fashion.db'

def update_db(items_dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    for v_id, item in items_dict.items():
        url = item.get('productUrl') or item.get('url') or item.get('link') or item.get('product_url')

        if not url:
            print(f"Skipping item {item.get('productName')} - No URL found!")
            continue

        if url.startswith('/'):
            url = f"https://www.vinted.com{url}"

        # --- Ensure Price is a number, not a dictionary ---
        price_raw = item.get('price')
        price = price_raw.get('amount') if isinstance(price_raw, dict) else price_raw

        c.execute('''
            INSERT OR REPLACE INTO products 
            (productUrl, productName, brandName, price, imageUrl, shop, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            url, 
            item.get('productName'), 
            item.get('brandName'), 
            price, 
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