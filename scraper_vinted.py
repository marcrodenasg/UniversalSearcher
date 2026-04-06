import asyncio
import os
from playwright.async_api import async_playwright
from db_manager import update_db
import sqlite3

CATEGORIES = [
    "https://www.vinted.com/catalog/5-men",
    "https://www.vinted.com/catalog/2983-designer-women",
    "https://www.vinted.com/catalog/2050-clothing",
    "https://www.vinted.com/catalog/257-jeans",
    "https://www.vinted.com/catalog/80-shorts",
    "https://www.vinted.com/catalog/76-tops-and-t-shirts",
    "https://www.vinted.com/catalog/79-jumpers-and-sweaters"
]

async def run_vinted_scraper():
    # Store items in a dictionary to prevent duplicates
    new_items = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # --- THIS ATTACHES THE LISTENER TO THE PAGE ---
        async def handle_response(response):
            # Target the specific request name seen in your screenshot
            if "promoted_closets" in response.url.lower() or "catalog/items" in response.url.lower():
                try:
                    data = await response.json()
                    final_items_list = []

                    # Check for the 'items' list seen at the bottom of your screenshot
                    if 'items' in data:
                        final_items_list.extend(data['items'])
                    
                    # Check inside promoted_closets (the top part of your screenshot)
                    if 'promoted_closets' in data:
                        for closet in data['promoted_closets']:
                            if 'items' in closet:
                                final_items_list.extend(closet['items'])

                    for item in final_items_list:
                        v_id = str(item.get('id'))
                        if v_id:
                            raw_url = item.get('url')
                            if raw_url and not raw_url.startswith('http'):
                                full_url = f"https://www.vinted.com{raw_url}"
                            else:
                                full_url = raw_url or f"https://www.vinted.com/items/{v_id}"

                        photo = item.get('photo', {})
                        img = photo.get('url') if isinstance(photo, dict) else item.get('image')

                        # Mapping based on your screenshot's JSON structure
                        new_items[v_id] = {
                            "productName": item.get('title') or item.get('name'),
                            "brandName": item.get('brand_title') or item.get('brand') or "Vinted",
                            "price": item.get('price'), 
                            "imageUrl": img,
                            "productUrl": full_url, # THIS IS THE KEY ONE
                            "shop": "Vinted",
                            "category": "Luxury"
                        }
                        print(f"Captured: {item.get('title')}")

                except Exception as e:
                    # Occasionally Vinted sends encoded text instead of JSON
                    pass

        # Tell Playwright to run handle_response every time a network request finishes
        page.on("response", handle_response)

        for url in CATEGORIES:
            print(f"Scraping Vinted Category: {url}")
            try:
                await page.goto(url, wait_until="load")
                await asyncio.sleep(5) 
                
                # Scroll down slowly to trigger more API calls
                for _ in range(3):
                    await page.mouse.wheel(0, 2000)
                    await asyncio.sleep(3)
                    
            except Exception as e:
                print(f"Vinted Error on {url}: {e}")

        # --- SAVE TO DATABASE ---
        if new_items:
            print(f"Found {len(new_items)} total items. Updating fashion.db...")
            update_db(new_items) # This calls the function in db_manager.py
            print("Database sync complete!")
        else:
            print("No items captured. Vinted might be blocking the request.")

        await browser.close()

if __name__ == "__main__":
    run_vinted_scraper_task = run_vinted_scraper()
    asyncio.run(run_vinted_scraper_task)