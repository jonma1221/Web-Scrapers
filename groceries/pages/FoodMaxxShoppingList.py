from selenium.webdriver.remote.webelement import WebElement
from pages.LoginPage import LoginPage
from shared.BasePage import BasePageSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class FoodMaxShoppingListSelenium(BasePageSelenium):
    acceptCookieBtnLocator = (By.ID, "truste-consent-button")
    searchInputTestId = (By.CSS_SELECTOR, "[data-testid='shopping-list-search-input']")
    addSearchItemButtonTestId = (By.CSS_SELECTOR, "[data-testid='add-item-button']")
    searchInputFindProductsButtonTestId = (By.CSS_SELECTOR, "[data-testid='find-products-btn']")
    clearSearchTestId = (By.CSS_SELECTOR, "[data-testid='clear-search-button']")
    deleteAllItemsButtonTestId = (By.CSS_SELECTOR, "[data-testid='delete-all-items-button']")
    deleteAllItemsConfirmationText = (By.XPATH, "//span[text()='Delete']")
    addProductItemButtonsLocator = (By.CSS_SELECTOR, "button[aria-label^='Click to add'][aria-label$='to shopping list']")
    closeSearchInputFindProductsButtonTextLocator = (By.CSS_SELECTOR, "button[aria-label=Close]")

    addProductItemPrefixText = "Click to add "
    addProductItemSuffixText = " to shopping list"
    def acceptCookies(self):
        acceptCookieBtn = self.wait.until(
            EC.presence_of_element_located(self.acceptCookieBtnLocator)
        )
        acceptCookieBtn.click()
        self.wait.until(EC.staleness_of(acceptCookieBtn))
    
    def enterItem(self, item: str):
        searchInput = self.wait.until(EC.element_to_be_clickable(self.searchInputTestId))
        searchInput.click()
        searchInput.send_keys(item)

    def addItem(self):
        addItemButton = self.wait.until(EC.element_to_be_clickable(self.addSearchItemButtonTestId))
        addItemButton.click()

    def addProductItem(self, index: int = 0) -> str:
        addProductButtons = self.wait.until(EC.visibility_of_all_elements_located(self.addProductItemButtonsLocator))
        button = addProductButtons[index]

        ariaLabel = button.get_attribute("aria-label")
        productName = ariaLabel
        if productName.startswith(self.addProductItemPrefixText):
            productName = productName[len(self.addProductItemPrefixText):]
        if productName.endswith(self.addProductItemSuffixText):
            productName = productName[: -len(self.addProductItemSuffixText)]

        print(f"productname - {productName}")

        button.click()
        return productName

    def findProduct(self):
        searchInputFindProductButton = self.wait.until(EC.element_to_be_clickable(self.searchInputFindProductsButtonTestId))
        searchInputFindProductButton.click()

    def closeSearchInputFindProducts(self):
        self.wait.until(EC.element_to_be_clickable(self.closeSearchInputFindProductsButtonTextLocator)).click()

    def removeItemFromWriteIns(self, index: int = 0):
        # removeItemButtonLocator = (By.XPATH, f"//p[text()='{productName}']/following-sibling::button[@data-testid='deleteItemBtn']")
        removeItemButtons = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, f"//button[@data-testid='deleteItemBtn']")))
        removeItemButtons[index].click()

    def removeItemFromProducts(self, index: int = 0):
        removeItemButtons = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, f"//button[@data-testid='deleteItemBtn']")))
        removeItemButtons[index].click()

    def removeItemFromCompleted(self, index: int = 0):
        removeItemButtons = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, f"//button[@data-testid='deleteItemBtn']")))
        removeItemButtons[index].click()

    def removeAllItems(self):
        self.wait.until(EC.element_to_be_clickable(self.deleteAllItemsButtonTestId)).click()
        self.wait.until(EC.element_to_be_clickable(self.deleteAllItemsConfirmationText)).click()

    @property
    def searchInput(self):
        return self.wait.until(EC.element_to_be_clickable(self.searchInputTestId))

    @property
    def emptyListHeading(self):
        return self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//*[text()='Empty List']")))

    def shoppingItemName(self, productName):
        return self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//p[text()='{productName}']")))
