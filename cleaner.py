import json
import os

def transform_data(raw_item):
    # Same transformation logic as before
    price_cents = raw_item.get("price", {}).get("cents", 0)
    clean_price = price_cents / 100
    base_img = "https://images.vestiairecollective.com"
    base_site = "https://es.vestiairecollective.com"
    pics = [base_img + p for p in raw_item.get("pictures", [])]
    
    return {
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

# 1. Load EXISTING data (datasetp1.json)
if os.path.exists('datasetp1.json'):
    with open('datasetp1.json', 'r') as f:
        existing_data = json.load(f)
else:
    existing_data = []

# 2. Load NEW raw data (raw_data.json)
with open('raw_data.json', 'r') as f:
    new_raw_items = json.load(f)

# 3. Transform and Add
# We use a set of existing URLs to avoid duplicates
existing_urls = {item['productUrl'] for item in existing_data}
new_count = 0

for raw_item in new_raw_items:
    clean_item = transform_data(raw_item)
    
    # Only add if we haven't seen this URL before
    if clean_item['productUrl'] not in existing_urls:
        existing_data.append(clean_item)
        new_count += 1

# 4. Save the combined list back to datasetp1.json
with open('datasetp1.json', 'w') as f:
    json.dump(existing_data, f, indent=2)

print(f"Update Complete!")
print(f"Added {new_count} new items.")
print(f"Total items in database: {len(existing_data)}")