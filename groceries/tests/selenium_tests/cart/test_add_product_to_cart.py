import pytest
from dataclasses import replace
from utils.stores_test_data import FILTER_CASES, LUCKY_BEEF_URL, FOODMAXX_BEEF_URL, SMART_FINAL_BEEF_URL
from pages.FoodMaxxSearch import FoodMaxxSearchSelenium
from pages.FoodMaxxLogin import FoodMaxxLoginSelenium
from pages.FoodMaxxShoppingList import FoodMaxShoppingListSelenium
from pages.SmartFinalSearch import SmartFinalSearchPageSelenium

def test_foodmax_can_add_product_to_shopping_list(
    foodmaxxSearchSelenium: FoodMaxxSearchSelenium
):
    foodmaxxSearchSelenium.driver.get(FOODMAXX_BEEF_URL)
    foodmaxxSearchSelenium.acceptCookies()
    foodmaxxSearchSelenium.addProductToList()

    assert foodmaxxSearchSelenium.shoppingListConfirmationPopup.is_displayed()

def test_smart_final_unable_to_add_cart_when_not_signed_in(
    smartFinalSearchPageSelenium: SmartFinalSearchPageSelenium
):
    smartFinalSearchPageSelenium.driver.get(SMART_FINAL_BEEF_URL)
    smartFinalSearchPageSelenium.acceptCookies()
    smartFinalSearchPageSelenium.addProductToList()

    assert smartFinalSearchPageSelenium.mustSignInToContinue.is_displayed()
    assert smartFinalSearchPageSelenium.mustSignInToContinue.text == "Sign in to continue."

@pytest.mark.parametrize("email,password,expectedSignedInUsername,authenticatedUrl", 
    [
        ("cqrdnnidyuhypyajlh@vtmpj.com", "&%d&IF0NI7", "cqrdnnidyuhypyajlh", "https://foodmaxx.com/account"),
    ]
)
def test_foodmax_products_still_added_to_shopping_list_when_signed_in(
    login_to_grocery_site,
    foodmaxxShoppingListSelenium: FoodMaxShoppingListSelenium,
    email,
    password,
    expectedSignedInUsername,
    authenticatedUrl
):
    foodmaxxSearchPage: FoodMaxxSearchSelenium = login_to_grocery_site(
        FOODMAXX_BEEF_URL,
        FoodMaxxSearchSelenium,
        FoodMaxxLoginSelenium,
        email,
        password,
        expectedSignedInUsername,
        authenticatedUrl,
    )
    assert foodmaxxSearchPage.signInButton(expectedSignedInUsername).is_displayed()
    foodmaxxSearchPage.clickShoppingList()
    foodmaxxShoppingListSelenium.searchInput.click()
    assert foodmaxxShoppingListSelenium.searchInput.is_displayed()
    foodmaxxSearchPage.driver.back()

    aria_label_text = foodmaxxSearchPage.removeFromListButtons[0].get_attribute("aria-label")
    assert "Click to remove" in aria_label_text
    