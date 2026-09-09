import pytest
from dataclasses import replace
from utils.stores_test_data import FILTER_CASES, LUCKY_BEEF_URL, FOODMAXX_BEEF_URL, SMART_FINAL_BEEF_URL
from pages.LuckyMeat import LuckySearchSelenium
from pages.FoodMaxxSearch import FoodMaxxSearchSelenium
from pages.FoodMaxxLogin import FoodMaxxLoginSelenium
from pages.FoodMaxxShoppingList import FoodMaxShoppingListSelenium
from pages.SmartFinalSearch import SmartFinalSearchPageSelenium
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def test_foodmax_can_remove_product_in_search_page(
    foodmaxxSearchSelenium: FoodMaxxSearchSelenium
):
    foodmaxxSearchSelenium.driver.get(FOODMAXX_BEEF_URL)
    foodmaxxSearchSelenium.acceptCookies()
    foodmaxxSearchSelenium.addProductToList()

    assert foodmaxxSearchSelenium.shoppingListConfirmationPopup.is_displayed()
    assert "added to your Shopping list" in foodmaxxSearchSelenium.shoppingListConfirmationPopup.text

    assert foodmaxxSearchSelenium.wait.until(EC.invisibility_of_element_located(foodmaxxSearchSelenium.shoppingListConfirmationPopup))

    foodmaxxSearchSelenium.removeProductFromList()

    assert foodmaxxSearchSelenium.shoppingListConfirmationPopup.is_displayed()
    assert "removed from your Shopping list" in foodmaxxSearchSelenium.shoppingListConfirmationPopup.text

@pytest.mark.parametrize("url,product",[("https://foodmaxx.com/shopping-list", "productWriteIn")])
def test_foodmax_can_remove_write_in_product_from_shopping_list(
    foodmaxxShoppingListSelenium: FoodMaxShoppingListSelenium,
    url,
    product
):
    foodmaxxShoppingListSelenium.driver.get(url)
    foodmaxxShoppingListSelenium.acceptCookies()

    foodmaxxShoppingListSelenium.enterItem(product)
    foodmaxxShoppingListSelenium.addItem()

    assert foodmaxxShoppingListSelenium.shoppingItemName(product).is_displayed()

    foodmaxxShoppingListSelenium.removeItemFromWriteIns()

    # Verify product is successfully removed
    assert foodmaxxShoppingListSelenium.wait.until(EC.invisibility_of_element_located((By.XPATH, f"//p[text()='{product}']")))

@pytest.mark.parametrize("url,product",[("https://foodmaxx.com/shopping-list", "beef")])
def test_foodmax_can_remove_product_from_shopping_list(
    foodmaxxShoppingListSelenium: FoodMaxShoppingListSelenium,
    url,
    product
):
    foodmaxxShoppingListSelenium.driver.get(url)
    foodmaxxShoppingListSelenium.acceptCookies()

    foodmaxxShoppingListSelenium.enterItem(product)
    foodmaxxShoppingListSelenium.findProduct()

    productName = foodmaxxShoppingListSelenium.addProductItem()
    foodmaxxShoppingListSelenium.closeSearchInputFindProducts()
    
    # Verify item was added
    assert foodmaxxShoppingListSelenium.shoppingItemName(productName).is_displayed()

    foodmaxxShoppingListSelenium.removeItemFromProducts()
    
    # # Verify item was removed
    assert foodmaxxShoppingListSelenium.wait.until(EC.invisibility_of_element_located((By.XPATH, f"//p[text()='{productName}']")))


@pytest.mark.parametrize("url,product",[("https://foodmaxx.com/shopping-list", "beef")])
def test_foodmax_can_delete_all_products_from_shopping_list(
    foodmaxxShoppingListSelenium: FoodMaxShoppingListSelenium,
    url,
    product
):
    foodmaxxShoppingListSelenium.driver.get(url)
    foodmaxxShoppingListSelenium.acceptCookies()

    foodmaxxShoppingListSelenium.enterItem(product)
    foodmaxxShoppingListSelenium.findProduct()

    foodmaxxShoppingListSelenium.addProductItem()
    foodmaxxShoppingListSelenium.addProductItem(1)
    foodmaxxShoppingListSelenium.addProductItem(2)
    foodmaxxShoppingListSelenium.closeSearchInputFindProducts()

    foodmaxxShoppingListSelenium.removeAllItems()

    # Verify empty list
    assert foodmaxxShoppingListSelenium.emptyListHeading.is_displayed()