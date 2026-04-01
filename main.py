import json

import json

with open('datasetp1.json', 'r') as file:
    jsondata = json.load(file)

    for item in jsondata:
        print(f"Product: {item.get('productName')}")
        print(f"Color: {', '.join(item.get('colors', []))}")
        print(f"Price: {item.get('price')} {item.get('priceCurrency')}")
        print(f"Size: {item.get('sizeLabel')}")
        print(f"Country: {item.get('country')}")
        print(f"Image: {item.get('imageUrl')}")
        print(f"URL: {item.get('productUrl')}")
        print(f"Description: {item.get('description').strip()}")
        print("-" * 30)