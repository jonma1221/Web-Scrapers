from playwright.async_api import Browser, Page, expect
import pytest
import pytest_asyncio
import re

from pages.AddressPage import AddressPage
from pages.SearchPage import SearchPage
from pages.LuckyMeat import LuckySearchPlaywright, LuckyAddressPlaywright

from utils.stores_test_data import STORE_SELECT_SCENARIOS, LUCKY_BEEF_URL

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
    city: str,
    store: str,
):
    await luckySearchPage.goTo(LUCKY_BEEF_URL)
    await luckySearchPage.selectYourStore()
    await luckyAddressPage.searchAddress(city)
    await luckyAddressPage.setAsMyStore(store)

    await expect(luckySearchPage.selectAStoreButton).to_contain_text(store)

@pytest.mark.parametrize(
    "search_page_cls, address_page_cls, url, city, expected_result",
    [
        (s["search_cls"], s["address_cls"], s["url"], city, expected)
        for s in STORE_SELECT_SCENARIOS
        for city, expected in s["cases"]
    ],
)
@pytest.mark.asyncio
async def test_search_location_appears_in_dropdown(
    page: Page,
    search_page_cls: type[SearchPage],
    address_page_cls: type[AddressPage],
    url: str,
    city: str,
    expected_result: str,
):
    search_page = search_page_cls(page)
    address_page = address_page_cls(page)

    await search_page.goTo(url)
    await search_page.selectYourStore()
    await address_page.searchBar.fill(city)

    await expect(address_page.searchOption(expected_result)).to_be_visible()


@pytest.mark.asyncio
async def test_open_store_directions_navigates_google_maps(
    luckySearchPage: LuckySearchPlaywright,
    luckyAddressPage: LuckyAddressPlaywright,
):
    await luckySearchPage.goTo(LUCKY_BEEF_URL)
    await luckySearchPage.selectYourStore()
    await luckyAddressPage.searchAddress("San Leandro")

    # This matches any button text like "5.8 mi", "12.3 mi",
    mapsPage = await luckyAddressPage.openDirections(re.compile(r"\d+\.\d+\s*mi"))
    await expect(mapsPage).to_have_url(re.compile(r"https://www\.google\.com/maps/"))
