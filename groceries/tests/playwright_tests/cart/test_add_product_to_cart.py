from asyncio import streams
from playwright.async_api import Browser, Page, expect
import pytest
import pytest_asyncio
import re

from pages.SmartFinalSearch import SmartFinalSearchPagePlaywright
from pages.SmartFinalLoginPage import SmartFinalLoginPagePlaywright
from pages.LuckyMeat import LuckySearchPlaywright, LuckyAddressPlaywright
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright
from pages.PlaywrightLoginPage import FoodMaxxLoginPlaywright
from pages.PlaywrightShoppingListPage import PlaywrightShoppingListPage
from utils.stores_test_data import STORE_SELECT_SCENARIOS, LUCKY_BEEF_URL, FOODMAXX_BEEF_URL, SMART_FINAL_BEEF_URL

@pytest.mark.asyncio
async def test_foodmax_can_add_product_to_shopping_list(
    foodmaxxSearchPage: FoodMaxxSearchPlaywright
):
    await foodmaxxSearchPage.goTo(FOODMAXX_BEEF_URL)
    await foodmaxxSearchPage.addProductToList()

    await expect(foodmaxxSearchPage.addedToListConfirmationPopup).to_be_visible()

@pytest.mark.asyncio
async def test_smart_final_unable_to_add_cart_when_not_signed_in(
    smartFinalSearchPage: SmartFinalSearchPagePlaywright
):
    await smartFinalSearchPage.goTo(SMART_FINAL_BEEF_URL)
    await smartFinalSearchPage.addProductToCart()

    await expect(smartFinalSearchPage.mustSignInToContinue).to_be_visible()

@pytest.mark.parametrize("email,password,expectedSignedInUsername,authenticatedUrl", 
    [
        ("cqrdnnidyuhypyajlh@vtmpj.com", "&%d&IF0NI7", "cqrdnnidyuhypyajlh", "https://foodmaxx.com/account"),
    ]
)
@pytest.mark.asyncio
async def test_foodmax_products_still_added_to_shopping_list_when_signed_in(
    login_to_grocery_site,
    # playwrightShoppingListPage: PlaywrightShoppingListPage,
    email,
    password,
    expectedSignedInUsername,
    authenticatedUrl
):
    foodmaxxSearchPage: FoodMaxxSearchPlaywright = await login_to_grocery_site(
        FOODMAXX_BEEF_URL,
        FoodMaxxSearchPlaywright,
        FoodMaxxLoginPlaywright,
        email,
        password,
        expectedSignedInUsername,
        authenticatedUrl,
    )
    playwrightShoppingListPage = PlaywrightShoppingListPage(foodmaxxSearchPage.page)
    await foodmaxxSearchPage.clickShoppingList()
    await playwrightShoppingListPage.searchInput.click()
    await expect(playwrightShoppingListPage.searchInput).to_be_visible(timeout=10000)

    await foodmaxxSearchPage.page.go_back()

    await expect(foodmaxxSearchPage.removeFromListButtons.first).to_be_visible(timeout=10000)


# Disabled due to cloudfare bot detection for login

# @pytest.mark.parametrize("url,search_page_cls,login_page_cls,email,password,expectedSignedInUsername,authenticatedUrl",
#     [
#         (SMART_FINAL_BEEF_URL,
#          SmartFinalSearchPagePlaywright,
#          SmartFinalLoginPagePlaywright,
#          "niyvbmglqyoqhqgcim@kjkpc.net",
#          "Lbayj0!V%kP5%k7t",
#          "niyvbmglqyoqhqgcim",
#          "https://www.smartandfinal.com/sm/planning/rsid/445/my-account/profile")
#     ]
# )
# @pytest.mark.asyncio
# async def test_smart_final_user_can_add_cart(
#     login_to_grocery_site,
#     url: str,
#     search_page_cls,
#     login_page_cls,
#     email,
#     password,
#     expectedSignedInUsername,
#     authenticatedUrl
# ):
#     searchPage: SearchPage = await login_to_grocery_site(
#         url,
#         search_page_cls,
#         login_page_cls,
#         email,
#         password,
#         expectedSignedInUsername,
#         authenticatedUrl
#     )

#     searchPage.addProductToList()





