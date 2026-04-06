import re

def slugify(text):
    if not text: return "item"
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text) 
    text = re.sub(r'[\s_-]+', '-', text) 
    return text.strip('-')

brand = item.get('brandName') or 'brand'
name = item.get('productName') or 'item'

# Construct the SEO-friendly URL manually
seo_url = f"https://www.dotshop.ai/product/DOTSHOP/{slugify(brand)}/{slugify(name)}"

new_items[v_id] = {
    "productName": name,
    "brandName": brand,
    "price": item.get('price'),
    "imageUrl": item.get('imageUrl'),
    "productUrl": seo_url, # <--- The fix is here!
    "shop": "Dotshop",
    "category": "Luxury"
}