import re

import pytest
from playwright.async_api import Page

from pages.GroceryOutletSearch import GroceryOutletSearchPagePlaywright
from pages.SearchPage import SearchPage
from utils.stores_test_data import BEEF_STORE_URLS, GROCERY_OUTLET_BEEF_URL


@pytest.mark.asyncio
async def test_scrape_deals_returns_beef_products(
    groceryOutletSearchPage: GroceryOutletSearchPagePlaywright,
):
    await groceryOutletSearchPage.goTo(GROCERY_OUTLET_BEEF_URL)
    await groceryOutletSearchPage.selectYourStore("517 Mantova Court")

    products = await groceryOutletSearchPage.scrapeDeals()
    print(products)
    assert len(products) > 0, "Expected at least one product to be scraped"
    assert all(p.name for p in products), "Every product must have a name"
    assert all(
        re.fullmatch(r"\$\d+\.\d{2}", p.sale_price) for p in products
    ), "Every product must have a dollar sale price"


@pytest.mark.parametrize("search_page_cls, url", BEEF_STORE_URLS)
@pytest.mark.asyncio
async def test_scrape_deals_returns_beef_products_for_store(
    page: Page,
    search_page_cls: type[SearchPage],
    url: str,
):
    searchPage = search_page_cls(page)
    await searchPage.goTo(url)

    products = await searchPage.scrapeDeals()

    valid = [p for p in products if p.name]
    assert len(valid) > 0, "Expected at least one product with a name"
    with_price = [p for p in valid if p.sale_price]
    if with_price:
        assert all(
            p.sale_price.startswith("$") for p in with_price
        ), "Every priced product must have a sale price starting with $"
