import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from playwright.async_api import async_playwright, expect
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright
from pages.FoodMaxxAddress import FoodMaxxAddressPlaywright
from pages.LuckyMeat import LuckyAddressPlaywright, LuckySearchPlaywright
from pages.SearchPage import SearchPage
from pages.AddressPage import AddressPage
from meat_compare.category_urls import CATEGORY_URLS
from utils.stores_test_data import STORES

async def scrape_store(page, store, search: SearchPage, address: AddressPage):
    url = CATEGORY_URLS[store.domain_key][store.category]
    await page.goto(url)

    await search.acceptCookies()
    await search.selectYourStore()

    await address.searchAddress(store.city_or_zip)
    await address.setAsMyStore(store.address)

    await expect(search.selectAStoreButton).not_to_have_text("Select a Store")

    return await search.scrapeDeals()

async def main():
    lucky = STORES[0]
    foodmaxx = STORES[1]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(permissions=["geolocation"])
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page1 = await context.new_page()
        page2 = await context.new_page()
        try:
            foodMaxResults, luckyResults = await asyncio.gather(
                scrape_store(page1, foodmaxx, FoodMaxxSearchPlaywright(page1), FoodMaxxAddressPlaywright(page1)),
                scrape_store(page2, lucky, LuckySearchPlaywright(page2), LuckyAddressPlaywright(page2)),
            )
            print(f"\n\n{lucky.name} -")
            printProducts(luckyResults)
            print(f"\n\n{foodmaxx.name} -")
            printProducts(foodMaxResults)
        finally:
            await context.tracing.stop(path="trace.zip")
            await browser.close()

def printProducts(deals):
    for product in deals:
        orig = product.original_price or "-"
        print(f"{product.brand} | {product.name} | {product.sale_price} | Was: {orig}")

asyncio.run(main())