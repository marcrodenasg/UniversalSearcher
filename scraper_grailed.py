import asyncio
import json
import os
from playwright.async_api import async_playwright
from db_manager import init_db, update_db

# --- TARGET CATEGORIES ---
CATEGORIES = [
    "https://www.grailed.com/categories/denim",
    "https://www.grailed.com/categories/polos",
    "https://www.grailed.com/categories/womenswear/blouses",
    "https://www.grailed.com/categories/footwear",
    "https://www.grailed.com/categories/outerwear",
    "https://www.grailed.com/categories/streetwear"
]

async def run_updater_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

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
                                listing_url = f"https://www.grailed.com/listings/{p_id}"
                                new_session_items[listing_url] = {
                                    "productName": item.get("title"),
                                    "brandName": item.get("designer_names"),
                                    "price": item.get("price"),
                                    "imageUrl": item.get("cover_photo", {}).get("url"),
                                    "productUrl": listing_url,
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
            print(f"\nUPDATING CATEGORY: {url.split('/')[-1].upper()}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(5)
                await page.mouse.wheel(0, 3000)
                await asyncio.sleep(4)
            except Exception as e:
                print(f"Skip {url}: {e}")

        # --- THE SQL SYNC ---
        if new_session_items:
            print(f"\n💾 Syncing {len(new_session_items)} items to fashion.db...")
            init_db() # Ensure table exists
            update_db(new_session_items)
            print("Database sync complete.")
        else:
            print("No items found this session.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_updater_scraper())