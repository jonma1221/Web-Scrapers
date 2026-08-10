import re

import pytest

from pages.GroceryOutletSearch import GroceryOutletSearchPagePlaywright

GROCERY_OUTLET_BEEF_URL = (
    "https://shop.groceryoutlet.com/store/grocery-outlet/collections/n-beef-29419"
)


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
