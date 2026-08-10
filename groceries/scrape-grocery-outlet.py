import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from playwright.async_api import async_playwright
from pages.GroceryOutletSearch import GroceryOutletSearchPagePlaywright

BEEF_URL = "https://shop.groceryoutlet.com/store/grocery-outlet/collections/n-beef-29419"
ADDRESS = "517 Mantova Court"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        page = await browser.new_page()
        try:
            search = GroceryOutletSearchPagePlaywright(page)
            await search.goTo(BEEF_URL)
            await search.selectYourStore(ADDRESS)

            products = await search.scrapeDeals()
            print(f"\nFound {len(products)} products:\n")
            for product in products:
                print(f"{product.name}")
                print(f"  Price: {product.sale_price}")
                print(f"  Image: {product.image_url}")
                print()
        finally:
            await browser.close()


asyncio.run(main())
