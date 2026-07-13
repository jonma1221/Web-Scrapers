from playwright.async_api import expect
import pytest
from dataclasses import replace
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright

FILTER_CASES = [
    ("https://foodmaxx.com/categories/Product%2Fmeat_seafood/Product%2Fbeef", "THE SAVE MART COMPANY"),
    ("https://foodmaxx.com/categories/Product%2Fmeat_seafood/Product%2Fbeef", "SUNNYSIDE FARMS")
]
@pytest.mark.parametrize("url, filter_name", FILTER_CASES)
@pytest.mark.asyncio(loop_scope="session")
async def test_filter_products_by_brand(
    foodmaxxSearchPage: FoodMaxxSearchPlaywright,
    url: str,
    filter_name: str
):
    await foodmaxxSearchPage.goTo(url)
    filterOption = await foodmaxxSearchPage.applyFilter(filter_name)

    await expect(filterOption).to_be_checked()

    products = await foodmaxxSearchPage.scrapeDeals()

    # Assert all products' brand name matches the filter
    valid = [p for p in products if p.name]
    assert all(p.brand == filter_name for p in valid)

@pytest.mark.parametrize("url, filter_name", FILTER_CASES)
@pytest.mark.asyncio(loop_scope="session")
async def test_clear_filter_returns_default_list(
    foodmaxxSearchPage: FoodMaxxSearchPlaywright,
    url: str,
    filter_name: str,
):
    await foodmaxxSearchPage.goTo(url)

    # Get a reference to the original list before applying filter
    originalList = await foodmaxxSearchPage.scrapeDeals()

    await foodmaxxSearchPage.applyFilter(filter_name)

    # Clear all the filters and scrape the list
    await foodmaxxSearchPage.clickClearAllFilters()
    listAfterClearingFilter = await foodmaxxSearchPage.scrapeDeals()

    # Assert the original products are equal to the cleared list. 
    # We ignore the image_url as CDN will transfrom the url
    products_before = [replace(p, image_url="") for p in originalList if p.name]
    products_after  = [replace(p, image_url="") for p in listAfterClearingFilter if p.name]
    assert products_before == products_after

@pytest.mark.parametrize("url, brand_filter_1, brand_filter_2", [
    ("https://foodmaxx.com/categories/Product%2Fmeat_seafood/Product%2Fbeef", "THE SAVE MART COMPANY", "SUNNYSIDE FARMS")
])
@pytest.mark.asyncio(loop_scope="session")
async def test_multiple_filter_by_brand(
    foodmaxxSearchPage: FoodMaxxSearchPlaywright,
    url: str,
    brand_filter_1: str,
    brand_filter_2: str,
):
    await foodmaxxSearchPage.goTo(url)

    # Apply the first brand filter and verify it's checked
    filterOption1 = await foodmaxxSearchPage.applyFilter(brand_filter_1)
    await expect(filterOption1).to_be_checked()

    # Apply the second brand filter and verify it's checked
    filterOption2 = await foodmaxxSearchPage.applyFilter(brand_filter_2)
    await expect(filterOption2).to_be_checked()

    # Confirm the applied filters UI container is rendered
    await expect(foodmaxxSearchPage.appliedFiltersContainer).to_be_visible()

    # Verify both filter labels appear inside the applied filters container
    filter1Applied = foodmaxxSearchPage.appliedFiltersContainer.filter(has_text=brand_filter_1)
    filter2Applied = foodmaxxSearchPage.appliedFiltersContainer.filter(has_text=brand_filter_2)
    await expect(filter1Applied).to_be_visible()
    await expect(filter2Applied).to_be_visible()