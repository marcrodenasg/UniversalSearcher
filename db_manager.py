import sqlite3
import os

DB_PATH = 'fashion.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Using productUrl as PRIMARY KEY automatically prevents duplicates
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            productUrl TEXT PRIMARY KEY, 
            productName TEXT,
            brandName TEXT,
            price REAL,
            imageUrl TEXT,
            shop TEXT,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database 'fashion.db' initialized!")

def update_db(items_dict):
    """Takes a dictionary of items and syncs them to the SQL database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # INSERT OR REPLACE: If the URL exists, it updates the price/info. If not, it adds it.
    for url, item in items_dict.items():
        c.execute('''
            INSERT OR REPLACE INTO products 
            (productUrl, productName, brandName, price, imageUrl, shop, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            url, 
            item.get('productName'), 
            item.get('brandName'), 
            item.get('price'), 
            item.get('imageUrl'), 
            item.get('Shop'), 
            item.get('category')
        ))
    
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect('fashion.db')
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()
    c.execute("SELECT * FROM products") # Make sure there is NO "WHERE" clause here
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()