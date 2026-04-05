import asyncio
import os
from playwright.async_api import async_playwright
from db_manager import init_db, update_db

# --- TARGET VESTIAIRE CATEGORIES ---
# You can find these by browsing Vestiaire and copying the URL
CATEGORIES = [
    "https://us.vestiairecollective.com/men/#gender=Men%232",
    "https://us.vestiairecollective.com/women/#gender=Women%231",
    "https://us.vestiairecollective.com/men-shoes/#categoryParent=Shoes%2313_gender=Men%232",
    "https://us.vestiairecollective.com/women-clothing/#categoryParent=Clothing%232_gender=Women%231",
    "https://us.vestiairecollective.com/women-shoes/#categoryParent=Shoes%233_gender=Women%231",
    "https://us.vestiairecollective.com/search/?q=supreme",
    "https://us.vestiairecollective.com/balenciaga/#brand=Balenciaga%23187",
    "https://us.vestiairecollective.com/search/?q=rick+owens",
    "https://us.vestiairecollective.com/dolce-gabbana/#brand=Dolce%20%26%20Gabbana%2347",
    "https://us.vestiairecollective.com/gucci/#brand=Gucci%232"
]

async def run_vestiaire_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        new_items = {}

        async def handle_response(response):
            # Vestiaire often uses 'catalog' or 'search' in their API calls
            if "catalog" in response.url.lower() or "search" in response.url.lower():
                try:
                    data = await response.json()
                    # Vestiaire's JSON structure is usually under 'results' or 'products'
                    products = data.get('results', []) or data.get('products', [])
                    
                    for item in products:
                        v_id = str(item.get('id'))
                        if v_id:
                            # Mapping Vestiaire's unique fields to YOUR database fields
                            listing_url = f"https://www.vestiairecollective.com/products/{v_id}"
                            new_items[listing_url] = {
                                "productName": item.get('name'),
                                "brandName": item.get('brand', {}).get('name', 'Designer'),
                                "price": item.get('price', {}).get('amount'),
                                "imageUrl": item.get('pictures', [{}])[0].get('url'),
                                "productUrl": listing_url,
                                "Shop": "Vestiaire",
                                "category": item.get('description', 'Luxury')
                            }
                    if products:
                        print(f"🎯 Vestiaire: Caught {len(products)} items!")
                except:
                    pass

        page.on("response", handle_response)

        for url in CATEGORIES:
            print(f"📡 Browsing Vestiaire: {url}")
            try:
                await page.goto(url, wait_until="domcontentloaded")
                await asyncio.sleep(6) # Give it time to load the catalog
                await page.mouse.wheel(0, 3000) # Scroll to trigger API
                await asyncio.sleep(4)
            except Exception as e:
                print(f"Vestiaire Timeout: {e}")

        # --- SYNC TO SAME DB ---
        if new_items:
            print(f"Merging {len(new_items)} Vestiaire items into fashion.db...")
            update_db(new_items)
            print("Database updated with Vestiaire stock!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_vestiaire_scraper())