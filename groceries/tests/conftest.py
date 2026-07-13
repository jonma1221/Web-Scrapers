from socket import timeout
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import pytest
import pytest_asyncio

from playwright.async_api import Browser, BrowserContext, Page, expect

from pages.LuckyMeat import LuckySearchPlaywright, LuckyAddressPlaywright
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright
from pages.FoodMaxxAddress import FoodMaxxAddressPlaywright
from pages.PlaywrightLoginPage import FoodMaxxLoginPlaywright


@pytest.fixture
def luckySearchPage(page: Page) -> LuckySearchPlaywright:
    return LuckySearchPlaywright(page)

@pytest.fixture
def foodmaxxSearchPage(page: Page) -> FoodMaxxSearchPlaywright:
    return FoodMaxxSearchPlaywright(page)

@pytest.fixture
def luckyAddressPage(page: Page) -> LuckyAddressPlaywright:
    return LuckyAddressPlaywright(page)

@pytest.fixture
def foodmaxxAddressPage(page: Page) -> FoodMaxxAddressPlaywright:
    return FoodMaxxAddressPlaywright(page)

@pytest_asyncio.fixture(loop_scope="session")
async def login_to_grocery_site(browser: Browser):
    contexts: list[BrowserContext] = []

    async def _login(
        url: str,
        search_page_cls,
        login_page_cls,
        email: str,
        password: str,
        expectedSignedInUsername: str
    ) -> Page:
        # context = await browser.new_context()
        context = await browser.new_context(storage_state=f".auth/login_grocery_state_{expectedSignedInUsername}.json")
        contexts.append(context)
        page = await context.new_page()
        search_page = search_page_cls(page)
        login_page = login_page_cls(page)
        await search_page.goTo(url)
        # await search_page.clickSignIn()
        # await login_page.login(email, password)
        await expect(search_page.loadingSpinnerIcon).not_to_be_visible()
        await expect(page.get_by_role("button", name=expectedSignedInUsername)).to_be_visible(timeout=10000)

        await context.storage_state(path=f".auth/login_grocery_state_{expectedSignedInUsername}.json")
        return search_page

    yield _login

    for ctx in contexts:
        await ctx.close()