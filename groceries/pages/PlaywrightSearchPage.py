from playwright.async_api import Locator, Page, expect
from shared.BasePage import BasePagePlaywright
from pages.SearchPage import SearchPage
from models.Product import Product


class PlaywrightSearchPage(SearchPage, BasePagePlaywright):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.selectAStoreButton = page.get_by_test_id(self.selectAStoreLink)
        self.acceptCookieBtn = page.locator(self.acceptCookieBtnLocator)
        self.loadingSpinnerIcon = page.locator(self.loadingSpinner)
        self.clearAllFiltersButton = self.page.get_by_role("button", name=self.clearAllFilters)
        self.appliedFiltersContainer = self.page.locator(self.appliedFiltersLocator)
        self.selectStoreForPricingButton = self.page.get_by_test_id(self.selectStoreForPricingLink)
        self.salePriceText = self.page.get_by_test_id(self.salePriceTestId)
        self.signInLinkBtn = page.get_by_role("button", name=self.signInLinkText)

    async def acceptCookies(self):
        await self.acceptCookieBtn.click()

    async def selectYourStore(self):
        await self.page.wait_for_load_state("networkidle")
        await self.selectAStoreButton.click()

    async def applyFilter(self, filterName) -> Locator:
        filterOption = self.page.get_by_role("checkbox", name=filterName)
        await filterOption.check()
        await expect(self.loadingSpinnerIcon).to_be_hidden()
        return filterOption

    async def clickClearAllFilters(self):
        await self.clearAllFiltersButton.click()
        await expect(self.loadingSpinnerIcon).to_be_hidden()

    async def clickSignIn(self):
        await expect(self.loadingSpinnerIcon).to_be_hidden()
        await self.signInLinkBtn.click()

    async def scrapeDeals(self):
        await expect(self.loadingSpinnerIcon).to_be_hidden()

        deals = await self.page.get_by_test_id(self.productCard).all()
        products = []
        for deal in deals:
            try:
                product = await Product.from_card_pw(deal)
            except Exception:
                continue
            products.append(product)
        return products
