from playwright.async_api import Page, expect
import pytest
from dataclasses import replace
from pages.SearchPage import SearchPage
from pages.GroceryOutletSearch import GroceryOutletSearchPagePlaywright, SortOption
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright
from utils.stores_test_data import FILTER_CASES, GROCERY_OUTLET_BEEF_URL

@pytest.mark.parametrize("search_page_cls, url, filter_name", FILTER_CASES)
@pytest.mark.asyncio
async def test_filter_products_by_brand(
    page: Page,
    search_page_cls: type[SearchPage],
    url: str,
    filter_name: str
):
    searchPage = search_page_cls(page)
    await searchPage.goTo(url)
    filterOption = await searchPage.applyFilter(filter_name)

    await expect(filterOption).to_be_checked()

    products = await searchPage.scrapeDeals()

    # Assert all products' brand name matches the filter
    valid = [p for p in products if p.name]
    assert all(p.brand == filter_name for p in valid)

@pytest.mark.parametrize("search_page_cls, url, filter_name", FILTER_CASES)
@pytest.mark.asyncio
async def test_clear_filter_returns_default_list(
    page: Page,
    search_page_cls: type[SearchPage],
    url: str,
    filter_name: str,
):
    searchPage = search_page_cls(page)
    await searchPage.goTo(url)

    # Get a reference to the original list before applying filter
    originalList = await searchPage.scrapeDeals()

    await searchPage.applyFilter(filter_name)

    # Clear all the filters and scrape the list
    await searchPage.clickClearAllFilters()
    listAfterClearingFilter = await searchPage.scrapeDeals()

    # Assert the original products are equal to the cleared list. 
    # We ignore the image_url as CDN will transfrom the url
    products_before = [replace(p, image_url="") for p in originalList if p.name]
    products_after  = [replace(p, image_url="") for p in listAfterClearingFilter if p.name]
    assert products_before == products_after

@pytest.mark.parametrize("url, brand_filter_1, brand_filter_2", [
    ("https://foodmaxx.com/categories/Product%2Fmeat_seafood/Product%2Fbeef", "THE SAVE MART COMPANY", "SUNNYSIDE FARMS")
])
@pytest.mark.asyncio
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

@pytest.mark.parametrize("url, sort_filter", [
    ("https://shop.groceryoutlet.com/store/grocery-outlet/collections/n-beef-29419", SortOption.PRICE_LOWEST_FIRST)
])
@pytest.mark.asyncio
async def test_sort_by_price_shows_lowest_first(
    groceryOutletSearchPage: GroceryOutletSearchPagePlaywright,
    url,
    sort_filter
):
    await groceryOutletSearchPage.goTo(url)

    await groceryOutletSearchPage.sortBy(sort_filter)

    # Reopen the sort and verify the correct sort option is applied
    await groceryOutletSearchPage.sortButton.click()
    await expect(groceryOutletSearchPage.page.get_by_role("radio", name=sort_filter.value)).to_be_checked()

@pytest.mark.parametrize("url, brand_filters", [
    (GROCERY_OUTLET_BEEF_URL, ["Thomas Farms", "Randall Farm"])
])
@pytest.mark.asyncio
async def test_applied_filters_remain_checked_when_reopened(
    groceryOutletSearchPage: GroceryOutletSearchPagePlaywright,
    url: str,
    brand_filters: list[str],
):
    await groceryOutletSearchPage.goTo(url)

    appliedFilters = await groceryOutletSearchPage.applyFilters(brand_filters)

    await groceryOutletSearchPage.openFilterSection("Brands")
    for filterOption in appliedFilters:
        await expect(filterOption).to_be_checked()