from enum import Enum

from playwright.async_api import Locator, Page, expect
from shared.BasePage import BasePagePlaywright
from pages.SearchPage import SearchPage
from models.Product import Product


class SortOption(Enum):
    BEST_MATCH = "Best match"
    PRICE_LOWEST_FIRST = "Price: Lowest First"
    PRICE_HIGHEST_FIRST = "Price: Highest First"
    UNIT_PRICE_LOW_FIRST = "Unit Price: Low First"
    UNIT_PRICE_HIGH_FIRST = "Unit Price: High First"
    RELEVANCE = "Relevance"


class GroceryOutletSearchPagePlaywright(SearchPage, BasePagePlaywright):
    # Product cards are divs carrying data-item-card; the wrapping li has no stable hook.
    # data-item-card is not a data-testid, so a CSS locator is required.
    productCard = "div[data-item-card='true']"
    loadingSpinner = "shelf-nav-loading"
    clearAllFilters = "Clear all"
    signInLinkText = "Login"
    collectionLoadingTestId = "collections-loading-layout"
    itemsListLoadingContainerTestId = "items-list-loading-container"
    loadingLockupGridItemTestId = "loading-lockup-grid-item"
    searchBarPlaceholder = "Search Grocery Outlet..."
    deliveryToTriggerText = "Delivery to"
    chooseAddressDialogName = "Choose address"
    enterAddressLabel = "Enter your address"
    saveAddressButtonText = "Save Address"
    applyButtonText = "Apply"
    sortButtonText = "Sort"
    brandsFilterButtonText = "Brands"
    filtersRegionText = "Filters"
    resetButtonText = "Reset"
    loadMoreBtnLocator = "button.e-12by0ia"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.searchBar = page.get_by_placeholder(self.searchBarPlaceholder)
        self.productCards = page.locator(self.productCard)
        self.deliveryToTrigger = page.get_by_text(self.deliveryToTriggerText).first
        self.navLoading = page.get_by_test_id(self.loadingSpinner)
        self.collectionLoading = page.get_by_test_id(self.collectionLoadingTestId)
        self.itemsListLoadingContainer = page.get_by_test_id(self.itemsListLoadingContainerTestId)
        self.loadingLockupGridItem = page.get_by_test_id(self.loadingLockupGridItemTestId)
        self.sortButton = self.page.get_by_role("button", name=self.sortButtonText)

    async def acceptCookies(self):
        pass

    async def selectYourStore(self, location: str = ""):
        await expect(self.navLoading).not_to_be_visible()
        await expect(self.itemsListLoadingContainer).not_to_be_visible()
        await expect(self.loadingLockupGridItem.first).not_to_be_visible()
        await self.deliveryToTrigger.click()
        dialog = self.page.get_by_role("dialog", name=self.chooseAddressDialogName)
        await expect(dialog).to_be_visible()

        addressInput = dialog.get_by_label(self.enterAddressLabel)
        await addressInput.fill(location)

        # Suggestions render as listbox options (input has aria-haspopup="listbox").
        # Take the first matching suggestion rather than requiring an exact address,
        # then confirm via the Save Address form revealed on selection.
        option = dialog.get_by_role("option", name=location).first
        await expect(option).to_be_visible()
        await option.click()
        await dialog.get_by_role("button", name=self.saveAddressButtonText).click()
        await expect(dialog).not_to_be_visible()

    async def openFilterSection(self, filterName):
        await self.page.get_by_role("button", name=filterName).click()

    async def applyFilter(self, filterName) -> Locator:
        await self.openFilterSection(self.brandsFilterButtonText)
        filterOption = self.page.get_by_role("checkbox", name=filterName)
        await filterOption.check()
        await self.page.get_by_role("button", name=self.applyButtonText).click()
        return filterOption

    async def applyFilters(self, filterNames: list[str]) -> list[Locator]:
        await self.openFilterSection(self.brandsFilterButtonText)
        filterOptions = [self.page.get_by_role("checkbox", name=filterName) for filterName in filterNames]
        for filterOption in filterOptions:
            await filterOption.check()
        await self.page.get_by_role("button", name=self.applyButtonText).click()
        return filterOptions

    async def resetFilters(self):
        await self.page.get_by_role("button", name=self.resetButtonText).click()

    async def clickClearAllFilters(self):
        clearBtn = self.page.get_by_role("button", name=self.clearAllFilters)
        if await clearBtn.count():
            await clearBtn.click()

    async def clickSignIn(self):
        await self.page.get_by_role("button", name=self.signInLinkText).click()

    async def scrapeDeals(self):
        await expect(self.collectionLoading).not_to_be_visible()
        cards = self.productCards
        await expect(cards.first).to_be_visible()

        products = []
        for card in await cards.all():
            try:
                product = await Product.from_grocery_outlet(card)
            except Exception:
                continue
            products.append(product)
        return products

    async def searchForProduct(self, query: str):
        await self.searchBar.fill(query)
        await self.searchBar.press("Enter")
        await expect(self.productCards.first).to_be_visible()

    async def sortBy(self, sortOption: SortOption):
        await self.sortButton.click()
        sortFilter = self.page.get_by_role("radio", name=sortOption.value)
        await sortFilter.check()