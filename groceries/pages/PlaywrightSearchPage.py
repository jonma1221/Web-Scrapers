import re

from playwright.async_api import Locator, Page, expect
from shared.BasePage import BasePagePlaywright
from pages.SearchPage import SearchPage
from models.Product import Product


class PlaywrightSearchPage(SearchPage, BasePagePlaywright):
    productCountTestId = "products-count"
    shoppingListText = "Shopping List"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.selectAStoreButton = page.get_by_test_id(self.selectAStoreLink)
        self.acceptCookieBtn = page.locator(self.acceptCookieBtnLocator)
        self.loadingSpinnerIcon = page.locator(self.loadingSpinner)
        self.clearAllFiltersButton = self.page.get_by_role("button", name=self.clearAllFilters)
        self.appliedFiltersContainer = self.page.locator(self.appliedFiltersLocator)
        self.selectStoreForPricingButton = self.page.get_by_test_id(self.selectStoreForPricingLink)
        self.productCardItem = self.page.get_by_test_id(self.productCard)
        self.salePriceText = self.page.get_by_test_id(self.salePriceTestId)
        self.signInLinkBtn = page.get_by_role("button", name=self.signInLinkText)
        self.productCountText = page.get_by_test_id(self.productCountTestId)
        self.addedToListConfirmationPopup = page.get_by_text(re.compile(r".* was added to your Shopping list"))
        self.removedFromListConfirmationPopup = page.get_by_text(re.compile(r".* was removed from your Shopping list"))
        self.addToListButtons = self.page.get_by_role("button", name=re.compile(r"Click to add .+ to shopping list"))
        self.removeFromListButtons = self.page.get_by_role("button", name=re.compile(r"Click to remove .* from shopping list"))
        self.shoppingListButton = self.page.get_by_role("button", name=self.shoppingListText)

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

    async def clickShoppingList(self):
        await self.shoppingListButton.click()
        
    async def addProductToList(self, index: int = 0):
        await self.addToListButtons.nth(index).click()

    async def removeProductFromList(self, index: int = 0):
        await self.removeFromListButtons.nth(index).click()

    async def scrapeDeals(self):
        await expect(self.loadingSpinnerIcon).to_be_hidden()

        await self.productCardItem.first.wait_for(state="visible", timeout=30000)
        deals = await self.productCardItem.all()
        products = []
        for deal in deals:
            try:
                product = await Product.from_card_pw(deal)
            except Exception:
                continue
            products.append(product)
        return products
