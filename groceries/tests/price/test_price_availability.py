from playwright.async_api import expect, Browser
import pytest
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright
from pages.PlaywrightLoginPage import FoodMaxxLoginPlaywright

import pytest_asyncio

@pytest_asyncio.fixture(loop_scope="session")
async def context(browser: Browser):
    ctx = await browser.new_context(permissions=["geolocation"])
    yield ctx
    await ctx.close()

@pytest.mark.asyncio(loop_scope="session")
async def test_price_shows_unavailable_if_no_store_selected(
    foodmaxxSearchPage: FoodMaxxSearchPlaywright
):
    await foodmaxxSearchPage.goTo("https://foodmaxx.com/categories/Product%2Fmeat_seafood/Product%2Fbeef")
    
    await expect(foodmaxxSearchPage.selectStoreForPricingButton.first).to_be_visible()
    await expect(foodmaxxSearchPage.selectStoreForPricingButton.first).to_contain_text("Select a Store for Pricing")


@pytest.mark.parametrize("email,password,expectedSignedInUsername,authenticatedUrl", [
    ("cqrdnnidyuhypyajlh@vtmpj.com", "&%d&IF0NI7", "cqrdnnidyuhypyajlh", "https://foodmaxx.com/account"),
    ("mztazsysrtikzyayry@vtmpj.com", "uB$q&8i0kfn", "mztazsysrtikzyayry", "https://foodmaxx.com/account")
    ]
)
@pytest.mark.asyncio
async def test_sale_price_is_visible_when_logged_in(
    login_to_grocery_site,
    email,
    password,
    expectedSignedInUsername,
    authenticatedUrl
):
    # Login with an account with selected store
    foodmaxxSearchPage = await login_to_grocery_site(
        "https://foodmaxx.com/categories/Product%2Fmeat_seafood/Product%2Fbeef",
        FoodMaxxSearchPlaywright,
        FoodMaxxLoginPlaywright,
        email,
        password,
        expectedSignedInUsername,
        authenticatedUrl,
    )
    await expect(foodmaxxSearchPage.selectStoreForPricingButton.first).not_to_be_visible()
    await expect(foodmaxxSearchPage.salePriceText.first).to_be_visible(timeout=30000)
