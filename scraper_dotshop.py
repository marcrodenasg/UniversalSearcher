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
            if any(k in url for k in ["products", "collection", "search", "algolia"]):
                try:
                    data = await response.json()
                    products = []
                    if isinstance(data, dict):
                        products = data.get('products', []) or data.get('results', []) or data.get('hits', [])
                    
                    for item in products:
                        name = item.get('title') or item.get('name')
                        if not name:
                            continue
                        
                        p_id = str(item.get('id') or item.get('objectID'))
                        handle = item.get('handle') or p_id
                        listing_url = f"https://www.dotshop.ai/products/{handle}"
                        
                        # --- IMAGE LOGIC ---
                        img_url = item.get('imageUrl') or item.get('image_url') or ""
                        
                        if isinstance(img_url, list) and len(img_url) > 0:
                            img_url = img_url[0]
                        if isinstance(img_url, dict):
                            img_url = img_url.get('url') or img_url.get('src')

                        if img_url:
                            # Just in case it's missing the protocol
                            if img_url.startswith('//'):
                                img_url = f"https:{img_url}"
                        else:
                            img_url = "https://via.placeholder.com/400?text=No+Image"

                        # --- 💰 PRICE LOGIC ---
                        raw_price = item.get('price', 0)
                        try:
                            price = float(raw_price)
                            # Shopify API often gives cents (e.g. 25000 for $250)
                            if price > 5000: 
                                price = price / 100
                        except:
                            price = 0

                        # --- 📝 DESCRIPTION LOGIC ---
                        raw_desc = item.get('description', '') or item.get('body_html', '') or ""
                        clean_desc = re.sub('<[^<]+?>', '', raw_desc)

                        # --- 💾 STORE DATA ---
                        new_items[listing_url] = {
                            "productName": name,
                            "brandName": item.get('vendor') or item.get('brand', 'Dotshop'),
                            "price": round(price, 2),
                            "imageUrl": img_url,
                            "productUrl": listing_url,
                            "shop": "Dotshop",
                            "category": "New In",
                            "description": clean_desc[:500]
                        }
                    
                    if products:
                        print(f"🎯 Dotshop: Caught {len(products)} potential items...")
                except:
                    pass

        page.on("response", handle_response)

        # --- NAVIGATION LOOP ---
        for url in CATEGORIES:
            print(f"📡 Browsing Dotshop: {url}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                # Scroll to trigger API calls
                for _ in range(5):
                    await page.evaluate("window.scrollBy(0, 800)")
                    await asyncio.sleep(1.5)
            except Exception as e:
                print(f"⚠️ Error on {url}: {e}")

        # --- SYNC TO DATABASE ---
        if new_items:
            print(f"💾 Merging {len(new_items)} Dotshop items into fashion.db...")
            init_db() 
            update_db(new_items)
            print("✅ Dotshop sync complete!")
        else:
            print("❌ No items intercepted.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_dotshop_scraper())