import json
import os

def transform_data(raw_item):
    price_cents = raw_item.get("price", {}).get("cents", 0)
    clean_price = price_cents / 100
    base_img = "https://images.vestiairecollective.com"
    base_site = "https://es.vestiairecollective.com"
    pics = [base_img + p for p in raw_item.get("pictures", [])]
    
    return {
        "Shop": "vestiaire",  # <-- New property added here
        "brandName": raw_item.get("brand", {}).get("name", "Unknown"),
        "colors": [c.get("name") for c in raw_item.get("colors", {}).get("all", [])],
        "description": raw_item.get("description", ""),
        "imageUrl": pics[0] if pics else "",
        "imageUrls": pics,
        "likes": raw_item.get("likes", 0),
        "price": clean_price,
        "priceCurrency": raw_item.get("price", {}).get("currency", "USD"),
        "productName": raw_item.get("name", "Unnamed"),
        "productUrl": base_site + raw_item.get("link", ""),
        "sellerId": raw_item.get("seller", {}).get("id"),
        "sellerName": raw_item.get("seller", {}).get("firstname"),
        "sizeLabel": raw_item.get("size", {}).get("label", ""),
        "country": raw_item.get("country", "US")
    }

# 1. Load EXISTING data
if os.path.exists('datasetp1.json'):
    with open('datasetp1.json', 'r') as f:
        existing_data = json.load(f)
else:
    existing_data = []

# 2. Load NEW raw data
try:
    with open('raw_data.json', 'r') as f:
        new_raw_items = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    print("raw_data.json is empty or missing. Skipping new additions.")
    new_raw_items = []

# 3. Add new items with the 'Shop' tag
existing_urls = {item.get('productUrl') for item in existing_data}
for raw_item in new_raw_items:
    clean_item = transform_data(raw_item)
    if clean_item['productUrl'] not in existing_urls:
        existing_data.append(clean_item)

# 4. FINAL CLEANUP: Ensure even OLD items have the 'Shop' property
for item in existing_data:
    if "Shop" not in item:
        item["Shop"] = "vestiaire"

# 5. Save
with open('datasetp1.json', 'w') as f:
    json.dump(existing_data, f, indent=2)

print(f"Success! Total items: {len(existing_data)}")