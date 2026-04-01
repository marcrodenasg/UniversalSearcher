import json
import os

def map_vestiaire(item):
    return {
        "Shop": "vestiaire",
        "brandName": item.get("brand", {}).get("name", "Unknown"),
        "productName": item.get("name", "Unnamed"),
        "price": item.get("price", {}).get("cents", 0) / 100,
        "imageUrl": "https://images.vestiairecollective.com" + item.get("pictures", [""])[0],
        "productUrl": "https://es.vestiairecollective.com" + item.get("link", ""),
        "description": item.get("description", ""),
        "sizeLabel": item.get("size", {}).get("label", "")
    }
def map_grailed(item):
    return {
        "Shop": "grailed",
        "brandName": item.get("designer_names", "Unknown"),
        "productName": item.get("title", "Unnamed"),
        "price": item.get("price", 0),
        "imageUrl": item.get("cover_photo", {}).get("image_url", ""),
        "productUrl": f"https://www.grailed.com/listings/{item.get('id')}",
        "description": f"{item.get('category_path')} - {item.get('condition')}",
        "sizeLabel": item.get("size", "N/A")
    }

def transform_data(raw_item):
    if "strata" in raw_item:
        return map_grailed(raw_item)
    elif "price" in raw_item and "cents" in raw_item["price"]:
        return map_vestiaire(raw_item)
    else:
        print("Warning: Unknown data format. Skipping item.")
        return None

def update_database():
    if os.path.exists('datasetp1.json'):
        with open('datasetp1.json', 'r') as f:
            db = json.load(f)
    else:
        db = []

    with open('raw_data.json', 'r') as f:
        new_raw = json.load(f)
        if isinstance(new_raw, dict): new_raw = [new_raw]

    existing_urls = {item['productUrl'] for item in db}
    
    for raw in new_raw:
        clean = transform_data(raw)
        if clean and clean['productUrl'] not in existing_urls:
            db.append(clean)

    with open('datasetp1.json', 'w') as f:
        json.dump(db, f, indent=2)
    print(f"Sync complete. DB Size: {len(db)}")

update_database()