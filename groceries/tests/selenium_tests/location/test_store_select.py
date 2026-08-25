
import pytest
import re

from dataclasses import replace
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils.stores_test_data import FILTER_CASES, LUCKY_BEEF_URL, FOODMAXX_BEEF_URL, STORE_SELECT_SCENARIOS, STORE_SELECT_SCENARIOS_SELENIUM
from pages.LuckyMeat import LuckySearchSelenium, LuckyAddressSelenium
from pages.FoodMaxxSearch import FoodMaxxSearchSelenium
from pages.SearchPage import SearchPage
from pages.AddressPage import AddressPage

@pytest.mark.parametrize("city,store", [("San Leandro", "FAIRMONT DR")])
def test_select_store_updates_products_list(
    luckySearchPageSelenium: LuckySearchSelenium,
    luckyAddressPageSelenium: LuckyAddressSelenium,
    city: str,
    store: str,
):
    luckySearchPageSelenium.driver.get(LUCKY_BEEF_URL)
    luckySearchPageSelenium.acceptCookies()
    luckySearchPageSelenium.selectYourStore()
    luckyAddressPageSelenium.searchAddress(city)
    luckyAddressPageSelenium.setAsMyStore(store)

    assert luckySearchPageSelenium.getElement(luckySearchPageSelenium.selectAStoreLink).text == store

@pytest.mark.parametrize(
    "search_page_cls, address_page_cls, url, city, expected_result",
    [
        (s["search_cls"], s["address_cls"], s["url"], city, expected)
        for s in STORE_SELECT_SCENARIOS_SELENIUM
        for city, expected in s["cases"]
    ],
)
def test_search_location_appears_in_dropdown(
    web_driver,
    search_page_cls: type[SearchPage],
    address_page_cls: type[AddressPage],
    url: str,
    city: str,
    expected_result: str,
):
    search_page = search_page_cls(web_driver)
    address_page = address_page_cls(web_driver)

    web_driver.get(url)
    search_page.selectYourStore()
    address_page.getElement(address_page.autocompleteInputId).send_keys(city)

    address_page.wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(),'{expected_result}')]")))

def test_open_store_directions_navigates_google_maps(
    luckySearchPageSelenium: LuckySearchSelenium,
    luckyAddressPageSelenium: LuckyAddressSelenium,
):
    luckySearchPageSelenium.driver.get(LUCKY_BEEF_URL)
    luckySearchPageSelenium.selectYourStore()
    luckyAddressPageSelenium.searchAddress("San Leandro")

    # This matches any button text like "5.8 mi", "12.3 mi",
    luckyAddressPageSelenium.openDirections(re.compile(r"\d+\.\d+\s*mi"))

    luckyAddressPageSelenium.driver.switch_to.window(luckyAddressPageSelenium.driver.window_handles[-1])

    assert "https://www.google.com/maps/" in luckyAddressPageSelenium.driver.current_url 