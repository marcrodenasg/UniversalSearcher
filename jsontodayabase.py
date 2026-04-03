import json
import os

def parse_grailed_network_data(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return

    with open(input_file, 'r') as f:
        data = json.load(f)

    # --- THE EXTRACTION ---
    # We drill down: results -> index 0 -> hits
    try:
        # Check if it's the 'Results' wrapper format you showed
        if isinstance(data, dict) and "results" in data:
            items = data["results"][0].get("hits", [])
        else:
            items = data # Fallback if it's already just a list
    except (KeyError, IndexError):
        print("⚠️ Structure changed! Checking for a fallback 'hits' key...")
        items = data.get("hits", [])

    cleaned_data = []

    for item in items:
        # Map the Grailed API fields to your App's fields
        # item.get() prevents crashing if a field like 'color' is missing
        entry = {
            "productName": item.get("title", "Unknown Item"),
            "brandName": item.get("designer_names", "Designer"),
            "price": item.get("price", 0),
            # Pull the high-res image URL
            "imageUrl": item.get("cover_photo", {}).get("url"),
            # Create the clickable link using the ID
            "productUrl": f"https://www.grailed.com/listings/{item.get('id')}",
            "description": f"{item.get('category')} - {item.get('color')} - Size {item.get('size')}",
            "Shop": "Grailed",
            "condition": item.get("condition", "").replace("is_", "")
        }
        
        # Only add if it's a real item with a name
        if entry["productName"]:
            cleaned_data.append(entry)

    # --- SAVE THE CLEAN DATA ---
    with open(output_file, 'w') as f:
        json.dump(cleaned_data, f, indent=4)
    
    print(f"✅ DONE! Created {output_file} with {len(cleaned_data)} items.")

if __name__ == "__main__":
    # Make sure this filename matches your 'raw' network dump file
    parse_grailed_network_data('api_dump.json', 'datasetp1.json')