import re
from enum import Enum

from playwright.async_api import Locator, Page, expect
from shared.BasePage import BasePagePlaywright
from pages.SearchPage import SearchPage
from models.Product import Product


class SortOption(Enum):
    RELEVANCE = "Relevance"
    BRAND_A_Z = "Brand A-Z"
    BRAND_Z_A = "Brand Z-A"
    PRICE_LOWEST_FIRST = "Price - Lowest First"
    PRICE_HIGHEST_FIRST = "Price - Highest First"


class SmartFinalSearchPagePlaywright(SearchPage, BasePagePlaywright):
    # Header
    searchInputTestId = "desktop-searchInputBox-testId"
    searchSubmitText = "Submit search query"
    signInButtonTestId = "accountHeader-button-testId"

    # Header popover trigger: open it, then click "Change Store" to reveal the dialog.
    storeHeaderTestId = "storeHeader-button-testId"
    changeStoreTestId = "storeDetails-button-testId-change-store"
    
    # Cookie banner
    privacyDialogText = "Privacy"
    acceptAllCookiesText = "Accept All"

    # Breadcrumb / category heading
    backLinkText = "Back"
    meatSeafoodLinkText = "Meat, Seafood"

    # Subcategory pills: data-testid="pillButtonTextLink-<name>-testId"
    subcategoryPillTestIdPrefix = "pillButtonTextLink-"

    # Sort-by custom select: data-testid="custom-select-button-data-testId"
    sortByTestId = "custom-select-button-data-testId"

    # Product cards are <article data-testid^="ProductCardWrapper">.
    # The prefix is a data-testid, so a CSS locator is required.
    productCardLocator = "article[data-testid^='ProductCardWrapper']"

    # Pagination
    paginationInfoTestId = "pagination-info-testId"
    nextPageText = "Next Page"
    previousPageText = "Previous Page"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.searchInput = page.get_by_test_id(self.searchInputTestId)
        self.searchSubmit = page.get_by_role("button", name=self.searchSubmitText)
        self.signInButton = page.get_by_test_id(self.signInButtonTestId)
        self.productCards = page.locator(self.productCardLocator)
        self.paginationInfo = page.get_by_test_id(self.paginationInfoTestId)

    async def acceptCookies(self):
        dialog = self.page.get_by_role("dialog", name=self.privacyDialogText)
        if await dialog.count():
            await self.page.get_by_role("button", name=self.acceptAllCookiesText).click()
            await expect(dialog).not_to_be_visible()

    async def selectYourStore(self):
        # The store header popover must be expanded first; then "Change Store"
        await self.page.get_by_test_id(self.storeHeaderTestId).click()
        await self.page.get_by_test_id(self.changeStoreTestId).click()

    async def searchFor(self, query: str):
        await self.searchInput.fill(query)
        await self.searchSubmit.click()

    async def clickSignIn(self):
        await self.signInButton.click()

    def subcategoryPill(self, name: str) -> Locator:
        return self.page.get_by_test_id(f"{self.subcategoryPillTestIdPrefix}{name}-testId")

    async def openSubcategory(self, name: str):
        await self.subcategoryPill(name).click()

    async def applyFilter(self, filterName: str) -> Locator:
        # Filter checkboxes include a product count in their accessible name
        # (e.g. "35 products in FIRST STREET"). Match case-sensitively so the
        # distinct brands "FIRST STREET" and "First Street" don't collide.
        checkbox = self.page.get_by_role(
            "checkbox", name=re.compile(re.escape(filterName))
        )
        await checkbox.check()
        return checkbox

    async def clickClearAllFilters(self):
        clearBtn = self.page.get_by_role("button", name="Clear all")
        if await clearBtn.count():
            await clearBtn.click()

    async def sortBy(self, sortOption: SortOption):
        await self.page.get_by_test_id(self.sortByTestId).click()
        await self.page.get_by_role("option", name=sortOption.value).click()

    async def scrapeDeals(self):
        await expect(self.productCards.first).to_be_visible(timeout=30000)

        products = []
        for card in await self.productCards.all():
            try:
                product = await Product.from_smartfinal(card)
            except Exception:
                continue
            products.append(product)
        return products

    async def resultsInfo(self) -> str:
        return (await self.paginationInfo.text_content() or "").strip()

    async def clickNextPage(self):
        await self._click_page(self.nextPageText)

    async def clickPreviousPage(self):
        await self._click_page(self.previousPageText)

    async def _click_page(self, buttonText: str):
        firstCardTestId = await self._firstCardTestId()
        before = await self.resultsInfo()
        await self.page.get_by_role("button", name=buttonText).click()
        # Product cards from the previous page linger in the DOM while the SPA
        # re-renders; wait for both the pagination range to advance AND the
        # first card to change (each card's data-testid embeds its unique SKU)
        # so scrapeDeals() never captures a stale mix of old and new cards.
        await expect(self.paginationInfo).not_to_have_text(before, timeout=30000)
        if firstCardTestId:
            await expect(self.productCards.first).not_to_have_attribute(
                "data-testid", firstCardTestId, timeout=30000
            )

    async def _firstCardTestId(self) -> str:
        first = self.productCards.first
        if not await first.count():
            return ""
        return (await first.get_attribute("data-testid")) or ""