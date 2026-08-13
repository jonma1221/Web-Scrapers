"""Shared search pipeline across stores for free-text queries.

Used by both the CLI entrypoint (meat_compare.py --query) and the future
web API. Launches one browser context with one page per store and runs
each store's search concurrently. Each store's 'search' callable owns its
page-object construction and store-set flow, mirroring the category
scrape in meat_compare.py.
"""

import asyncio
import sys
from urllib.parse import quote

from playwright.async_api import Page, async_playwright, expect

from pages.FoodMaxxAddress import FoodMaxxAddressPlaywright
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright
from pages.GroceryOutletSearch import GroceryOutletSearchPagePlaywright
from pages.LuckyMeat import LuckyAddressPlaywright, LuckySearchPlaywright
from pages.PlaywrightAddressPage import PlaywrightAddressPage
from pages.PlaywrightSearchPage import PlaywrightSearchPage

from meat_compare.inference import infer_category
from meat_compare.models.MeatDeal import MeatDeal
from models.Product import Product


def _shared_search_url(domain: str, query: str) -> str:
    """Build a FoodMaxx/Lucky product search URL for a query."""
    return f"https://{domain}/search/products?q={quote(query)}"


def _grocery_outlet_search_url(query: str) -> str:
    """Build a Grocery Outlet (Instacart) search URL for a query."""
    return f"https://shop.groceryoutlet.com/store/grocery-outlet/s?k={quote(query)}"


async def _search_shared(
    page: Page,
    query: str,
    location: str,
    search_cls: type[PlaywrightSearchPage],
    address_cls: type[PlaywrightAddressPage],
    domain: str,
) -> tuple[list[Product], str]:
    """Shared FoodMaxx/Lucky search: set the store, then re-navigate for store-scoped results.

    Returns (products, location) where location is the store label captured
    from the selected store card (e.g. "Concord — 4505 Clayton Rd, ...").
    """
    url = _shared_search_url(domain, query)
    await page.goto(url)

    search = search_cls(page)
    address = address_cls(page)

    await search.acceptCookies()
    await search.selectYourStore()

    async def set_store() -> None:
        resolved = await address.searchAddress(location)
        await address.setAsMyStore(resolved.split(",")[0] if resolved else "")

    async def store_set() -> bool:
        try:
            await expect(search.selectAStoreButton).not_to_have_text(
                "Select a Store", timeout=15000
            )
            return True
        except Exception:
            return False

    await set_store()
    if not await store_set():
        # The store-card list renders async after the address option is
        # selected; retry once if the first attempt raced it.
        await set_store()
        await expect(search.selectAStoreButton).not_to_have_text(
            "Select a Store", timeout=15000
        )

    # Re-navigate so results are guaranteed store-scoped.
    await page.goto(url)
    products = await search.scrapeDeals()
    return products, address.store_location or ""


async def _search_foodmaxx(page: Page, query: str, location: str) -> tuple[list[Product], str]:
    """Search FoodMaxx for a query, returning first-page products."""
    return await _search_shared(
        page,
        query,
        location,
        FoodMaxxSearchPlaywright,
        FoodMaxxAddressPlaywright,
        "foodmaxx.com",
    )


async def _search_lucky(page: Page, query: str, location: str) -> tuple[list[Product], str]:
    """Search Lucky for a query, returning first-page products."""
    return await _search_shared(
        page,
        query,
        location,
        LuckySearchPlaywright,
        LuckyAddressPlaywright,
        "luckysupermarkets.com",
    )


async def _search_grocery_outlet(page: Page, query: str, location: str) -> tuple[list[Product], str]:
    """Search Grocery Outlet, falling back to the search box if no cards render.

    Store-set is best-effort: Instacart's autocomplete needs a street address
    and can't validate bare ZIPs, but the search page still renders priced
    products without a store, so a failed address must not fail the store.
    """
    url = _grocery_outlet_search_url(query)
    await page.goto(url)

    search = GroceryOutletSearchPagePlaywright(page)
    await search.acceptCookies()
    try:
        await search.selectYourStore(location)
    except Exception:
        pass

    if await search.productCards.count() == 0:
        await search.searchForProduct(query)

    products = await search.scrapeDeals()
    return products, await search.deliveryLocation()


STORE_CONFIGS: list[dict] = [
    {"name": "FoodMaxx", "search": _search_foodmaxx},
    {"name": "Lucky", "search": _search_lucky},
    {"name": "Grocery Outlet", "search": _search_grocery_outlet},
]


async def scrape_store(store_config: dict, page: Page, query: str, location: str) -> tuple[list[Product], str]:
    """Dispatch a query to one store's search callable. May raise on failure."""
    return await store_config["search"](page, query, location)


async def run_search(query: str, location: str) -> tuple[list[MeatDeal], list[str]]:
    """Search all configured stores concurrently.

    Returns (all_deals, failed_store_names). Launches one page per store
    and runs them with asyncio.gather(return_exceptions=True); individual
    store failures are collected rather than aborting the whole run. The
    browser is always closed in a finally block.
    """
    category = infer_category(query) or ""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50, args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-zygote',
                '--single-process'
            ])
        context = await browser.new_context(permissions=["geolocation"])
        pages = [await context.new_page() for _ in STORE_CONFIGS]
        try:
            results = await asyncio.gather(
                *[
                    scrape_store(config, page, query, location)
                    for config, page in zip(STORE_CONFIGS, pages)
                ],
                return_exceptions=True,
            )
        finally:
            await browser.close()

    deals: list[MeatDeal] = []
    failed_stores: list[str] = []
    for config, result in zip(STORE_CONFIGS, results):
        if isinstance(result, Exception):
            print(f"Store failed: {result}", file=sys.stderr)
            failed_stores.append(config["name"])
        else:
            products, _location = result
            deals.extend(
                MeatDeal.from_product(product, config["name"], category)
                for product in products
            )
    return deals, failed_stores
