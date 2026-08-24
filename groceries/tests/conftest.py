from socket import timeout
import re
import sys
from pathlib import Path



sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import pytest
import pytest_asyncio
import allure

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
from playwright.async_api import Browser, BrowserContext, Page, async_playwright, expect

from pages.LuckyMeat import LuckySearchPlaywright, LuckyAddressPlaywright, LuckyAddressSelenium, LuckySearchSelenium
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright, FoodMaxxSearchSelenium
from pages.FoodMaxxAddress import FoodMaxxAddressPlaywright, FoodMaxxAddressSelenium
from pages.PlaywrightLoginPage import FoodMaxxLoginPlaywright
from pages.PlaywrightShoppingListPage import PlaywrightShoppingListPage
from pages.GroceryOutletSearch import GroceryOutletSearchPagePlaywright
from pages.SmartFinalSearch import SmartFinalSearchPagePlaywright
from pages.SmartFinalAddress import SmartFinalAddressPlaywright
from pages.SmartFinalLoginPage import SmartFinalLoginPagePlaywright
from pages.SearchPage import SearchPage


def sanitize_test_name(name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_.\-]+", "_", name)
    return sanitized[:200]

@pytest.fixture
def luckySearchPage(page: Page) -> LuckySearchPlaywright:
    return LuckySearchPlaywright(page)

@pytest.fixture
def luckyAddressPage(page: Page) -> LuckyAddressPlaywright:
    return LuckyAddressPlaywright(page)

@pytest.fixture
def luckySearchPageSelenium(web_driver: WebDriver) -> LuckySearchSelenium:
    return LuckySearchSelenium(web_driver)

@pytest.fixture
def luckyAddressPageSelenium(web_driver: WebDriver) -> LuckyAddressSelenium:
    return LuckyAddressSelenium(web_driver)

@pytest.fixture
def foodmaxxSearchPage(page: Page) -> FoodMaxxSearchPlaywright:
    return FoodMaxxSearchPlaywright(page)

@pytest.fixture
def foodmaxxAddressPage(page: Page) -> FoodMaxxAddressPlaywright:
    return FoodMaxxAddressPlaywright(page)

@pytest.fixture
def foodmaxxSearchSelenium(web_driver: WebDriver) -> FoodMaxxSearchSelenium:
    return FoodMaxxSearchSelenium(web_driver)

@pytest.fixture
def foodmaxxAddressSelenium(web_driver: WebDriver) -> FoodMaxxAddressSelenium:
    return FoodMaxxAddressSelenium(web_driver)

@pytest.fixture
def groceryOutletSearchPage(page: Page) -> GroceryOutletSearchPagePlaywright:
    return GroceryOutletSearchPagePlaywright(page)

@pytest.fixture
def smartFinalSearchPage(page: Page) -> SmartFinalSearchPagePlaywright:
    return SmartFinalSearchPagePlaywright(page)

@pytest.fixture
def smartFinalAddressPage(page: Page) -> SmartFinalAddressPlaywright:
    return SmartFinalAddressPlaywright(page)

@pytest.fixture
def smartFinalLoginPage(page: Page) -> SmartFinalLoginPagePlaywright:
    return SmartFinalLoginPagePlaywright(page)

@pytest.fixture
def playwrightShoppingListPage(page: Page) -> PlaywrightShoppingListPage:
    return PlaywrightShoppingListPage(page)

@pytest_asyncio.fixture(loop_scope="session")
async def login_to_grocery_site(browser: Browser, request):
    contexts: list[BrowserContext] = []

    async def _login(
        url: str,
        search_page_cls,
        login_page_cls,
        email: str,
        password: str,
        expectedSignedInUsername: str,
        authenticatedUrl: str = "",
    ) -> Page:
        storage_state_path = f".auth/login_grocery_state_{expectedSignedInUsername}.json"
        Path(storage_state_path).parent.mkdir(parents=True, exist_ok=True)
        if Path(storage_state_path).exists():
            context = await browser.new_context(storage_state=storage_state_path)
        else:
            context = await browser.new_context()
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
        contexts.append(context)
        page = await context.new_page()
        search_page = search_page_cls(page)
        login_page = login_page_cls(page)

        # Check if authenticated 
        is_authenticated = await login_state_valid(authenticatedUrl, storage_state_path)
        
        # Refresh login state if needed, else go to url
        if not is_authenticated:
            await search_page.goTo(url)
            await search_page.clickSignIn()
            await login_page.login(email, password)
            await expect(search_page.loadingSpinnerIcon).not_to_be_visible()
            await expect(page.get_by_role("button", name=expectedSignedInUsername)).to_be_visible(timeout=30000)
            await context.storage_state(path=storage_state_path)
        else:
            await search_page.goTo(url)
        return search_page

    yield _login

    rep = getattr(request.node, "rep_call", None)
    sanitized_name = sanitize_test_name(request.node.name)
    for ctx in contexts:
        if rep is not None and rep.failed:
            await ctx.tracing.stop(path=f"test-results/{sanitized_name}-trace.zip")

            allure.attach.file(
                f"test-results/{sanitized_name}-trace.zip",
                name=f"{sanitized_name} Trace",
                attachment_type="application/vnd.allure.playwright-trace"
            )
        await ctx.close()

async def login_state_valid(authenticatedUrl: str, storage_state_path: str) -> bool:
    if not Path(storage_state_path).exists():
        return False

    # Check if authenticated
    async with async_playwright() as p:
        request = await p.request.new_context(storage_state=str(storage_state_path))
        try:
            response = await request.get(authenticatedUrl)
            print("Authenticated")
            return response.status == 200
        except Exception:
            return False
        finally:
            await request.dispose()

@pytest.fixture
def web_driver(request) -> WebDriver:
    driver = webdriver.Chrome()

    yield driver

    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        name = sanitize_test_name(request.node.name)
        results_dir = Path("test-results")
        results_dir.mkdir(parents=True, exist_ok=True)
        try:
            png_path = results_dir / f"{name}-failure.png"
            driver.save_screenshot(str(png_path))
            allure.attach.file(str(png_path), name=f"{name} Failure",
                               attachment_type=allure.attachment_type.PNG)

            html_path = results_dir / f"{name}-failure.html"
            html_path.write_text(driver.page_source, encoding="utf-8")
            allure.attach.file(str(html_path), name=f"{name} Page HTML",
                               attachment_type=allure.attachment_type.HTML)
        except WebDriverException:
            pass

    driver.quit()