#!/usr/bin/env python3
"""CLI entrypoint for the meat price comparison tool (Playwright, concurrent)."""

import sys
import asyncio
import argparse
import webbrowser
from pathlib import Path

# Add repo root (for shared.BasePage) and groceries/ (for pages.*, models.*, meat_compare.*)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright, expect
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright
from pages.FoodMaxxAddress import FoodMaxxAddressPlaywright
from pages.LuckyMeat import LuckySearchPlaywright, LuckyAddressPlaywright
from meat_compare.category_urls import CATEGORY_URLS
from meat_compare.models.MeatDeal import MeatDeal
from meat_compare.compare import generate_html

CATEGORIES = ["beef", "pork", "chicken", "turkey", "seafood"]

STORE_CONFIGS = [
    {
        "name": "FoodMaxx",
        "domain_key": "foodmaxx.com",
        "search": FoodMaxxSearchPlaywright,
        "address": FoodMaxxAddressPlaywright,
    },
    {
        "name": "Lucky",
        "domain_key": "luckysupermarkets.com",
        "search": LuckySearchPlaywright,
        "address": LuckyAddressPlaywright,
    },
]


async def scrape_store(page, store_config, category, zip_code):
    """Navigate to the category page, set the store, and scrape deals."""
    url = CATEGORY_URLS[store_config["domain_key"]][category]
    await page.goto(url)

    search = store_config["search"](page)
    address = store_config["address"](page)

    await search.acceptCookies()
    await search.selectYourStore()

    await address.searchAddress(zip_code)
    await address.setAsMyStore()

    await expect(search.selectAStoreButton).not_to_have_text("Select a Store")

    all_products = list(await search.scrapeDeals())

    if store_config["domain_key"] == "foodmaxx.com":
        while True:
            try:
                await search.clickNextBtn()
                await search.scrollToTop()
                all_products.extend(await search.scrapeDeals())
            except Exception:
                break

    return [MeatDeal.from_product(p, store_config["name"], category) for p in all_products]


async def scrape_store_categories(page, store_config, categories, zip_code):
    """Scrape all requested categories for one store sequentially on its page."""
    deals = []
    for category in categories:
        try:
            deals.extend(await scrape_store(page, store_config, category, zip_code))
        except Exception as e:
            print(
                f"Error scraping {store_config['name']} ({category}): {e}",
                file=sys.stderr,
            )
    return deals


async def run(zip_code, categories):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(permissions=["geolocation"])
        page1 = await context.new_page()
        page2 = await context.new_page()
        try:
            results = await asyncio.gather(
                *[
                    scrape_store_categories(page, store_config, categories, zip_code)
                    for page, store_config in zip((page1, page2), STORE_CONFIGS)
                ],
                return_exceptions=True,
            )
        finally:
            await browser.close()

    all_deals = []
    stores_failed = 0
    for result in results:
        if isinstance(result, Exception):
            print(f"Store failed: {result}", file=sys.stderr)
            stores_failed += 1
        else:
            all_deals.extend(result)
    return all_deals, stores_failed


def main():
    parser = argparse.ArgumentParser(
        description="Compare meat prices across FoodMaxx and Lucky"
    )
    parser.add_argument("--zip", required=True, help="ZIP code for store search")
    parser.add_argument(
        "-c",
        "--category",
        choices=CATEGORIES,
        help="Meat category to compare (default: all categories)",
    )
    args = parser.parse_args()

    categories = [args.category] if args.category else CATEGORIES
    all_deals, stores_failed = asyncio.run(run(args.zip, categories))

    if stores_failed == len(STORE_CONFIGS):
        print("All stores failed.", file=sys.stderr)
        sys.exit(1)

    if not all_deals:
        print("No deals found from any store.", file=sys.stderr)
        sys.exit(1)

    html = generate_html(all_deals, args.zip)
    output_path = Path(__file__).parent / "meat-deals.html"
    output_path.write_text(html)
    print(f"Generated {output_path}")
    webbrowser.open(output_path.as_uri())


if __name__ == "__main__":
    main()
