from playwright.async_api import Browser, expect
import pytest
import pytest_asyncio
import re

from pages.LuckyMeat import LuckySearchPlaywright, LuckyAddressPlaywright
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright
from pages.FoodMaxxAddress import FoodMaxxAddressPlaywright

from utils.stores_test_data import STORES

@pytest_asyncio.fixture(loop_scope="session")
async def context(browser: Browser, request):
    ctx = await browser.new_context(permissions=["geolocation"])
    await ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield ctx
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        await ctx.tracing.stop(path=f"test-results/{request.node.name}-trace.zip")
    await ctx.close()

@pytest.mark.parametrize("city,store", [("San Leandro", "FAIRMONT DR")])
@pytest.mark.asyncio
async def test_select_store_updates_products_list(
    luckySearchPage: LuckySearchPlaywright,
    luckyAddressPage: LuckyAddressPlaywright,
    city,
    store
):
    await luckySearchPage.goTo("https://luckysupermarkets.com/categories/Product%2Fmeat_seafood/Product%2Fbeef")
    await luckySearchPage.selectYourStore()
    await luckyAddressPage.searchAddress(city)
    await luckyAddressPage.setAsMyStore(store)

    await expect(luckySearchPage.selectAStoreButton).to_contain_text(store)


@pytest.mark.parametrize("city, expected_result", [
    ("San Leandro", "San Leandro, CA US"), 
    ("San Lea", "San Leandro, CA US"), # Partial match
    ("@#$", "No results found") # invalid location
])
@pytest.mark.asyncio
async def test_search_location_appears_in_dropdown(
    luckySearchPage: LuckySearchPlaywright,
    luckyAddressPage: LuckyAddressPlaywright,
    city,
    expected_result
):
    await luckySearchPage.goTo("https://luckysupermarkets.com/categories/Product%2Fmeat_seafood/Product%2Fbeef")
    await luckySearchPage.selectYourStore()
    await luckyAddressPage.searchBar.fill(city)

    await expect(luckyAddressPage.searchOption(expected_result)).to_be_visible()

@pytest.mark.asyncio
async def test_open_store_directions_navigates_google_maps(
    luckySearchPage: LuckySearchPlaywright,
    luckyAddressPage: LuckyAddressPlaywright,
):
    await luckySearchPage.goTo("https://luckysupermarkets.com/categories/Product%2Fmeat_seafood/Product%2Fbeef")
    await luckySearchPage.selectYourStore()
    await luckyAddressPage.searchAddress("San Leandro")

    # This matches any button text like "5.8 mi", "12.3 mi",
    mapsPage = await luckyAddressPage.openDirections(re.compile(r"\d+\.\d+\s*mi"))
    await expect(mapsPage).to_have_url(re.compile(r"https://www\.google\.com/maps/"))