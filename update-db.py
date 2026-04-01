import json
import os

# 1. Load your existing clean database
filename = 'datasetp1.json'

if os.path.exists(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    
    # 2. Loop through and add the property
    count = 0
    for item in data:
        if "Shop" not in item:
            item["Shop"] = "vestiaire"
            count += 1
    
    # 3. Save it back
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Done! Updated {count} items with the 'Shop' property.")
    print(f"Total items in database: {len(data)}")
else:
    print(f"Error: {filename} not found in this folder.")