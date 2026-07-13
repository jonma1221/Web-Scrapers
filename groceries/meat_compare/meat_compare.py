#!/usr/bin/env python3
"""CLI entrypoint for the meat price comparison tool."""

import sys
import argparse
import webbrowser
from pathlib import Path

# Add repo root (for shared.BasePage) and groceries/ (for pages.*, models.*, meat_compare.*)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver
from pages.FoodMaxxSearch import FoodMaxxSearch
from pages.FoodMaxxAddress import FoodMaxxAddress
from pages.LuckyMeat import LuckyMeat
from meat_compare.category_urls import CATEGORY_URLS
from meat_compare.models.MeatDeal import MeatDeal
from meat_compare.compare import generate_html

CATEGORIES = ["beef", "pork", "chicken", "turkey", "seafood"]

STORE_CONFIGS = [
    {"name": "FoodMaxx", "domain": "foodmaxx.com"},
    {"name": "Lucky", "domain": "luckysupermarkets.com"},
]


def scrape_foodmaxx(driver, zip_code, category):
    """Navigate to FoodMaxx category page, set store, scrape all pages."""
    url = CATEGORY_URLS["foodmaxx.com"][category]
    driver.get(url)

    search = FoodMaxxSearch(driver)
    search.acceptCookies()
    search.selectYourStore()

    address = FoodMaxxAddress(driver)
    address.searchAddress(zip_code)
    address.setAsMyStore()

    all_products = list(search.scrapeDeals())

    # Paginate through remaining pages
    while True:
        try:
            search.clickNextBtn()
            search.scrollToTop()
            all_products.extend(search.scrapeDeals())
        except Exception:
            break

    return [MeatDeal.from_product(p, "FoodMaxx", category) for p in all_products]


def scrape_lucky(driver, zip_code, category):
    """Navigate to Lucky category page, set store, scrape deals."""
    url = CATEGORY_URLS["luckysupermarkets.com"][category]
    driver.get(url)

    lucky = LuckyMeat(driver)
    lucky.acceptCookies()
    lucky.selectYourStore(zip_code)

    products = lucky.scrapeDeals()
    return [MeatDeal.from_product(p, "Lucky", category) for p in products]


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
    all_deals = []
    stores_failed = 0

    for store in STORE_CONFIGS:
        driver = None
        try:
            driver = webdriver.Chrome()
            driver.maximize_window()

            for category in categories:
                try:
                    if store["domain"] == "foodmaxx.com":
                        deals = scrape_foodmaxx(driver, args.zip, category)
                    else:
                        deals = scrape_lucky(driver, args.zip, category)
                    all_deals.extend(deals)
                except Exception as e:
                    print(
                        f"Error scraping {store['name']} ({category}): {e}",
                        file=sys.stderr,
                    )
        except Exception as e:
            print(f"Error with {store['name']}: {e}", file=sys.stderr)
            stores_failed += 1
        finally:
            if driver:
                driver.quit()

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
