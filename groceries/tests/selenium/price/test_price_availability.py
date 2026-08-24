from playwright.async_api import expect, Browser
import pytest
from utils.stores_test_data import FOODMAXX_BEEF_URL
from pages.FoodMaxxSearch import FoodMaxxSearchSelenium
from pages.FoodMaxxAddress import FoodMaxxAddressSelenium

async def test_price_shows_unavailable_if_no_store_selected(
    foodmaxxSearchSelenium: FoodMaxxSearchSelenium
):
    foodmaxxSearchSelenium.driver.get("https://foodmaxx.com/categories/Product%2Fmeat_seafood/Product%2Fbeef")
    
    selectStoreForPricingButton = foodmaxxSearchSelenium.getSelectStoreForPricingButton()
    assert selectStoreForPricingButton.is_displayed()
    assert selectStoreForPricingButton.text == "Select a Store for Pricing"

@pytest.mark.parametrize("city,store", [("San Leandro", "SAN LEANDRO")])
def test_sale_price_is_visible_when_store_selected(
    foodmaxxSearchSelenium: FoodMaxxSearchSelenium,
    foodmaxxAddressSelenium: FoodMaxxAddressSelenium,
    city,
    store
):
    foodmaxxSearchSelenium.driver.get(FOODMAXX_BEEF_URL)
    foodmaxxSearchSelenium.acceptCookies()

    foodmaxxSearchSelenium.selectYourStore()
    foodmaxxAddressSelenium.searchAddress(city)
    foodmaxxAddressSelenium.setAsMyStore(store)

    assert len(foodmaxxSearchSelenium.driver.find_elements(*foodmaxxSearchSelenium.selectStoreForPricingLink)) == 0