import asyncio
import json
import os
from playwright.async_api import async_playwright

# --- TARGET CATEGORIES ---
CATEGORIES = [
    "https://www.grailed.com/categories/denim",
    "https://www.grailed.com/categories/polos",
    "https://www.grailed.com/categories/womenswear/blouses",
    "https://www.grailed.com/categories/footwear",
    "https://www.grailed.com/categories/outerwear",
    "https://www.grailed.com/categories/streetwear"
]

CLEAN_DB = "datasetp1.json"

async def run_updater_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # This will hold only the new items found in THIS specific run
        new_session_items = {}

        # --- THE NETWORK INTERCEPTOR ---
        async def handle_response(response):
            if response.request.resource_type in ["fetch", "xhr"]:
                url = response.url.lower()
                if any(k in url for k in ["algolia", "queries", "listings", "search"]):
                    try:
                        data = await response.json()
                        hits = []
                        if isinstance(data, dict) and "results" in data:
                            hits = data["results"][0].get("hits", [])
                        elif isinstance(data, dict):
                            hits = data.get("hits", [])

                        for item in hits:
                            p_id = str(item.get("id"))
                            if p_id:
                                # We map the data to your DB format
                                new_session_items[f"https://www.grailed.com/listings/{p_id}"] = {
                                    "productName": item.get("title"),
                                    "brandName": item.get("designer_names"),
                                    "price": item.get("price"),
                                    "imageUrl": item.get("cover_photo", {}).get("url"),
                                    "productUrl": f"https://www.grailed.com/listings/{p_id}",
                                    "Shop": "Grailed",
                                    "category": item.get("category_path", "General")
                                }
                        if hits:
                            print(f"🎯 Intercepted {len(hits)} items...")
                    except:
                        pass

        page.on("response", handle_response)

        # --- NAVIGATION LOOP ---
        for url in CATEGORIES:
            print(f"\n📂 UPDATING CATEGORY: {url.split('/')[-1].upper()}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(5)
                # Scroll to get more depth per category
                await page.mouse.wheel(0, 3000)
                await asyncio.sleep(4)
            except Exception as e:
                print(f"⚠️ Skip {url}: {e}")

        # --- THE SMART MERGE ---
        print("\n💾 Merging new data into database...")
        
        # 1. Load the existing items from your JSON file
        master_db = {}
        if os.path.exists(CLEAN_DB):
            try:
                with open(CLEAN_DB, 'r') as f:
                    old_list = json.load(f)
                    # Use URL as key to ensure uniqueness
                    master_db = {item['productUrl']: item for item in old_list}
                    print(f"📁 Loaded {len(master_db)} existing items from {CLEAN_DB}")
            except Exception as e:
                print(f"⚠️ Could not read existing DB, starting fresh. ({e})")

        # 2. Update master_db with the items from this session
        added_count = 0
        updated_count = 0
        
        for url, data in new_session_items.items():
            if url in master_db:
                # If price changed, update it
                if master_db[url]['price'] != data['price']:
                    master_db[url] = data
                    updated_count += 1
            else:
                # Brand new item
                master_db[url] = data
                added_count += 1

        # 3. Save the final merged list back to the file
        with open(CLEAN_DB, 'w') as f:
            json.dump(list(master_db.values()), f, indent=4)
        
        print(f"✅ UPDATE COMPLETE.")
        print(f"✨ New items added: {added_count}")
        print(f"🔄 Prices/Info updated: {updated_count}")
        print(f"📊 Total items in DB: {len(master_db)}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_updater_scraper())