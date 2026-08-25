
import pytest
from dataclasses import replace
from selenium import webdriver
from utils.stores_test_data import FILTER_CASES, LUCKY_BEEF_URL, FOODMAXX_BEEF_URL
from pages.LuckyMeat import LuckySearchSelenium
from pages.FoodMaxxSearch import FoodMaxxSearchSelenium
from pages.SearchPage import SearchPage
from selenium.webdriver.common.by import By

# @pytest.mark.parametrize("search_page_cls, url, filter_name", FILTER_CASES)
# @pytest.mark.asyncio
def test_filter_products_by_brand(
    web_driver,
    # url: str,
    # filter_name: str
):
    filter_name = "THE SAVE MART COMPANY"
    searchPage = LuckySearchSelenium(web_driver)
    web_driver.get(LUCKY_BEEF_URL)
    
    searchPage.acceptCookies()

    filterOption = searchPage.applyFilter(filter_name)

    assert filterOption.is_selected()

    products = searchPage.scrapeDeals()

    # Assert all products' brand name matches the filter
    valid = [p for p in products if p.name]
    assert all(p.brand == filter_name for p in valid)

@pytest.mark.parametrize("search_page_cls, url, filter_name", [
    (LuckySearchSelenium, LUCKY_BEEF_URL, "THE SAVE MART COMPANY"),
    (FoodMaxxSearchSelenium, FOODMAXX_BEEF_URL, "THE SAVE MART COMPANY")
])
def test_clear_filter_returns_default_list(
    web_driver,
    search_page_cls: type[SearchPage],
    url: str,
    filter_name: str,
):
    searchPage = search_page_cls(web_driver)
    web_driver.get(url)

    searchPage.acceptCookies()

    # Get a reference to the original list before applying filter
    originalList = searchPage.scrapeDeals()

    searchPage.applyFilter(filter_name)

    # Clear all the filters and scrape the list
    searchPage.clickClearAllFilters()
    listAfterClearingFilter = searchPage.scrapeDeals()

    # Assert the original products are equal to the cleared list. 
    # We ignore the image_url as CDN will transfrom the url
    products_before = [replace(p, image_url="") for p in originalList if p.name]
    products_after  = [replace(p, image_url="") for p in listAfterClearingFilter if p.name]
    assert products_before == products_after

@pytest.mark.parametrize("url, brand_filter_1, brand_filter_2", [
    (FOODMAXX_BEEF_URL, "THE SAVE MART COMPANY", "SUNNYSIDE FARMS")
])
def test_multiple_filter_by_brand(
    foodmaxxSearchSelenium: FoodMaxxSearchSelenium,
    url: str,
    brand_filter_1: str,
    brand_filter_2: str,
):
    foodmaxxSearchSelenium.driver.get(url)

    foodmaxxSearchSelenium.acceptCookies()

    # Apply the first brand filter and verify it's checked
    filterOption1 = foodmaxxSearchSelenium.applyFilter(brand_filter_1)
    assert filterOption1.is_selected()

    # Apply the second brand filter and verify it's checked
    filterOption2 = foodmaxxSearchSelenium.applyFilter(brand_filter_2)
    assert filterOption2.is_selected()

    # Confirm the applied filters UI container is rendered
    appliedFiltersContainer = foodmaxxSearchSelenium.getElement(foodmaxxSearchSelenium.appliedFiltersLocator)
    assert appliedFiltersContainer.is_displayed()

    # Verify both filter labels appear inside the applied filters container
    filter1Applied = appliedFiltersContainer.find_element(By.XPATH, f'//p[text()="{brand_filter_1}"]')
    filter2Applied = appliedFiltersContainer.find_element(By.XPATH, f'//p[text()="{brand_filter_2}"]')
    
    assert filter1Applied.is_displayed()
    assert filter2Applied.is_displayed()

    assert filter1Applied.text == brand_filter_1
    assert filter2Applied.text == brand_filter_2
