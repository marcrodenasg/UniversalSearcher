import asyncio
import os
import re
from playwright.async_api import async_playwright
from db_manager import init_db, update_db

# --- DOTSHOP TARGETS ---
CATEGORIES = [
    "https://www.dotshop.ai/new-in",
    "https://www.dotshop.ai/category?filter.ss_category_hierarchy=shoes",
    "https://www.dotshop.ai/curator-store/ella-richards",
    "https://www.dotshop.ai/category?filter.ss_category_hierarchy=bags"
]

async def run_dotshop_scraper():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        new_items = {} 

        async def handle_response(response):
            url = response.url.lower()
            if "category.json" in url or "products" in url or "search" in url:
                try:
                    data = await response.json()
                    
                    # Based on your screenshot, the items are in 'results'
                    items_list = data.get('results', [])
                    
                    for item in items_list:
                        # Exact keys from your screenshot
                        name = item.get('name')
                        brand = item.get('brand') or "Dotshop"
                        brand_slug = item.get('brand_slug') or "brand"
                        
                        # We use 'id' to create a unique key for the dictionary
                        v_id = str(item.get('id'))
                        
                        if not name or not v_id:
                            continue

                        # --- CONSTRUCT THE PERFECT LINK ---
                        # We use the 'brand_slug' and 'name' logic here
                        def slugify_simple(text):
                            return re.sub(r'[\s_-]+', '-', str(text).lower().strip())

                        name_slug = slugify_simple(name)
                        listing_url = f"https://www.dotshop.ai/product/DOTSHOP/{brand_slug}/{name_slug}"
                        
                        # --- CAPTURE THE REST ---
                        img_url = item.get('imageUrl')
                        price = item.get('price') or item.get('msrp')

                        new_items[listing_url] = {
                            "productName": name,
                            "brandName": brand,
                            "price": price,
                            "imageUrl": img_url,
                            "productUrl": listing_url,
                            "shop": "Dotshop",
                            "category": "New In"
                        }
                    
                    if items_list:
                        print(f"Dotshop: Successfully mapped {len(items_list)} items from results.")
                except Exception as e:
                    # Silence JSON errors from non-json responses
                    pass

        page.on("response", handle_response)

        # --- NAVIGATION LOOP ---
        for url in CATEGORIES:
            print(f"Browsing Dotshop: {url}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                # Scroll to trigger API calls
                for _ in range(5):
                    await page.evaluate("window.scrollBy(0, 800)")
                    await asyncio.sleep(1.5)
            except Exception as e:
                print(f"Error on {url}: {e}")

        # --- SYNC TO DATABASE ---
        if new_items:
            print(f"Merging {len(new_items)} Dotshop items into fashion.db...")
            init_db() 
            update_db(new_items)
            print("Dotshop sync complete!")
        else:
            print("No items intercepted.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_dotshop_scraper())