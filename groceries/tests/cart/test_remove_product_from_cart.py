from asyncio import streams
from playwright.async_api import Browser, Page, expect
import pytest

from pages.PlaywrightShoppingListPage import PlaywrightShoppingListPage
from pages.SmartFinalSearch import SmartFinalSearchPagePlaywright
from pages.SmartFinalLoginPage import SmartFinalLoginPagePlaywright
from pages.AddressPage import AddressPage
from pages.SearchPage import SearchPage
from pages.LuckyMeat import LuckySearchPlaywright, LuckyAddressPlaywright
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright
from utils.stores_test_data import STORE_SELECT_SCENARIOS, LUCKY_BEEF_URL, FOODMAXX_BEEF_URL, SMART_FINAL_BEEF_URL

@pytest.mark.asyncio
async def test_foodmax_can_remove_product_in_search_page(
    foodmaxxSearchPage: FoodMaxxSearchPlaywright
):
    await foodmaxxSearchPage.goTo(FOODMAXX_BEEF_URL)
    await foodmaxxSearchPage.addProductToList()

    await expect(foodmaxxSearchPage.addedToListConfirmationPopup).to_be_visible()
    
    # Wait for popup to auto dismiss before trying to remove from list
    await expect(foodmaxxSearchPage.addedToListConfirmationPopup).not_to_be_visible(timeout=10000)
    await foodmaxxSearchPage.removeProductFromList()
    
    await expect(foodmaxxSearchPage.removedFromListConfirmationPopup).to_be_visible()

@pytest.mark.parametrize("url,product",[("https://foodmaxx.com/shopping-list", "productWriteIn")])
@pytest.mark.asyncio
async def test_foodmax_can_remove_write_in_product_from_shopping_list(
    playwrightShoppingListPage: PlaywrightShoppingListPage,
    url,
    product
):
    await playwrightShoppingListPage.goTo(url)

    await playwrightShoppingListPage.enterItem(product)
    await playwrightShoppingListPage.addItem()

    await expect(playwrightShoppingListPage.page.get_by_role("heading", name=product, exact=True)).to_be_visible()

    await playwrightShoppingListPage.removeItemFromWriteIns()

    # Verify product is successfully removed
    await expect(playwrightShoppingListPage.page.get_by_role("heading", name=product, exact=True)).not_to_be_visible()


@pytest.mark.parametrize("url,product",[("https://foodmaxx.com/shopping-list", "beef")])
@pytest.mark.asyncio
async def test_foodmax_can_remove_product_from_shopping_list(
    playwrightShoppingListPage: PlaywrightShoppingListPage,
    url,
    product
):
    await playwrightShoppingListPage.goTo(url)

    await playwrightShoppingListPage.enterItem(product)
    await playwrightShoppingListPage.findProduct()

    productName = await playwrightShoppingListPage.addProductItem()
    await playwrightShoppingListPage.closeSearchInputFindProducts()

    # Verify item was added
    await expect(playwrightShoppingListPage.page.get_by_role("link", name=productName)).to_be_visible()

    await playwrightShoppingListPage.removeItemFromProducts()

    # Verify item was removed
    await expect(playwrightShoppingListPage.page.get_by_role("link", name=productName)).not_to_be_visible()

@pytest.mark.parametrize("url,product",[("https://foodmaxx.com/shopping-list", "beef")])
@pytest.mark.asyncio
async def test_foodmax_can_delete_all_products_from_shopping_list(
    playwrightShoppingListPage: PlaywrightShoppingListPage,
    url,
    product
):
    await playwrightShoppingListPage.goTo(url)

    await playwrightShoppingListPage.enterItem(product)
    await playwrightShoppingListPage.findProduct()

    await playwrightShoppingListPage.addProductItem()
    await playwrightShoppingListPage.addProductItem(1)
    await playwrightShoppingListPage.addProductItem(2)
    await playwrightShoppingListPage.closeSearchInputFindProducts()

    await playwrightShoppingListPage.removeAllItems()

    # Verify empty list
    await expect(playwrightShoppingListPage.emptyListHeading).to_be_visible()