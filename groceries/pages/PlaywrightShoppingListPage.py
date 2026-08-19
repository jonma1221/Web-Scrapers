import re

from playwright.async_api import Locator, Page, expect
from shared.BasePage import BasePagePlaywright


class PlaywrightShoppingListPage(BasePagePlaywright):
    searchInputTestId = "shopping-list-search-input"
    searchInputFindProductButtonTestId = "find-products-btn"
    closeSearchInputFindProductsButtonText = "Close"
    addItemButtonTestId = "add-item-button"
    deleteAllItemsButtonTestId = "delete-all-items-button"
    deleteAllItemsConfirmationText = "Delete press control option"
    shareListButtonTestId = "share-list-button"
    emptyListHeadingText = "Empty List"
    itemsListHeadingText = "Items List"
    shoppingListHeadingText = "You are on Shopping List page"
    acceptAllCookiesText = "Accept All"
    writeInsSectionText = "Write-ins"
    productsSectionText = "Products"
    completedSectionText = "Completed"

    # Item cards share a CSS class (no unique testid); scoped actions use this
    # to disambiguate between multiple items.
    itemContainerLocator = ".shopping-list-item-container"
    itemCheckboxTestId = "shopping-list-item-checkbox"
    findProductButtonTestId = "findProductBtn"
    editItemButtonTestId = "editItemBtn"
    removeItemButtonTestId = "deleteItemBtn"
    addProductItemPrefixText = "Click to add "
    addProductItemSuffixText = " to shopping list"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.searchInput = page.get_by_test_id(self.searchInputTestId)
        self.addItemButton = page.get_by_test_id(self.addItemButtonTestId)
        self.deleteAllItemsButton = page.get_by_test_id(self.deleteAllItemsButtonTestId)
        self.confirmDeleteAllButton = self.page.get_by_role("button", name=self.deleteAllItemsConfirmationText)
        self.shareListButton = page.get_by_test_id(self.shareListButtonTestId)
        self.itemContainers = page.locator(self.itemContainerLocator)
        self.emptyListHeading = page.get_by_role("heading", name=self.emptyListHeadingText)
        self.itemsListHeading = page.get_by_role("heading", name=self.itemsListHeadingText)
        self.writeInsSection = page.get_by_role("button", name=self.writeInsSectionText)
        self.productsSection = page.get_by_role("button", name=self.productsSectionText)
        self.completedSection = page.get_by_role("button", name=self.completedSectionText)
        self.itemCheckbox = page.get_by_test_id(self.itemCheckboxTestId)
        self.findProductButton = page.get_by_test_id(self.findProductButtonTestId)
        self.editItemButton = page.get_by_test_id(self.editItemButtonTestId)
        self.removeItemButton = page.get_by_test_id(self.removeItemButtonTestId)
        self.removeWriteInsItemButton = self.page.get_by_role("region", name=re.compile("Write-ins (.*)")).get_by_test_id(self.removeItemButtonTestId)
        self.removeProductsItemButton = self.page.get_by_role("region", name=re.compile("Products(.*)")).get_by_test_id(self.removeItemButtonTestId)
        self.removeProductsCompletedButton = self.page.get_by_role("region", name=re.compile("Completed(.*)")).get_by_test_id(self.removeItemButtonTestId)
        self.addProductItemButtons = self.page.get_by_role("button", name=re.compile("Click to add .*"))
        self.searchInputFindProductButton = self.page.get_by_test_id(self.searchInputFindProductButtonTestId)
        self.closeSearchInputFindProductsButton = self.page.get_by_role("button", name=self.closeSearchInputFindProductsButtonText, exact=True)

    async def acceptCookies(self):
        banner = self.page.get_by_role("alertdialog", name="Cookie banner")
        if await banner.count():
            await self.page.get_by_role("button", name=self.acceptAllCookiesText).click()
            await expect(banner).not_to_be_visible()

    async def enterItem(self, item: str):
        await self.searchInput.click()
        await self.searchInput.fill(item)

    async def addItem(self):
        await self.addItemButton.click()

    async def findProduct(self):
        await self.searchInputFindProductButton.click()

    async def addProductItem(self, index: int = 0) -> str:
        button = self.addProductItemButtons.nth(index)
        ariaLabel = await button.get_attribute("aria-label")
        productName = ariaLabel
        if productName.startswith(self.addProductItemPrefixText):
            productName = productName[len(self.addProductItemPrefixText):]
        if productName.endswith(self.addProductItemSuffixText):
            productName = productName[: -len(self.addProductItemSuffixText)]
        await button.click()
        return productName

    async def closeSearchInputFindProducts(self):
        await self.closeSearchInputFindProductsButton.click()

    def itemNameHeading(self, index: int = 0) -> Locator:
        return self.itemContainers.nth(index).get_by_role("heading")

    def itemAddedConfirmation(self, item: str) -> Locator:
        return self.page.get_by_text(re.compile(rf"^{re.escape(item)} added"))

    async def removeItemFromWriteIns(self, index: int = 0):
        await self.removeWriteInsItemButton.nth(index).click()

    async def removeItemFromProducts(self, index: int = 0):
        await self.removeProductsItemButton.nth(index).click()

    async def removeItemFromCompleted(self, index: int = 0):
        await self.removeProductsCompletedButton.nth(index).click()
    
    async def removeAllItems(self):
        await self.deleteAllItemsButton.click()
        await self.confirmDeleteAllButton.click()