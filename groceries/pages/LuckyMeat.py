from pages.AddressPage import AddressPage
from shared.BasePage import BasePageSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from models.Product import Product
from pages.SearchPage import SearchPage
from pages.PlaywrightSearchPage import PlaywrightSearchPage
from pages.PlaywrightAddressPage import PlaywrightAddressPage
from selenium.webdriver.common.action_chains import ActionChains
import time
class LuckySearchSelenium(SearchPage, BasePageSelenium):

    acceptCookieBtnLocator = (By.ID, "truste-consent-button")
    signInLinkText = (By.XPATH, "//button[text()='Select to sign in or sign up']")
    productCard = (By.XPATH, '//*[@data-testid="product-card" and @aria-label]')
    selectAStoreLink = (By.XPATH, '//button[@data-testid="store-select-link"]')
    autocompleteInputId = (By.ID, "autocompleteInputId")
    setAsMyStoreId = (By.XPATH, '//button[@aria-label="Set as my Store"]')
    loadingSpinner = (By.CSS_SELECTOR, '.mantine-Loader-root')
    clearAllFiltersText = (By.CSS_SELECTOR, "[aria-label='Clear all filters. Select to remove all filters']")

    def acceptCookies(self):
        acceptCookieBtn = self.wait.until(EC.presence_of_element_located(self.acceptCookieBtnLocator))
        acceptCookieBtn.click()

        # Wait for cookie banner to be removed (re-render triggered)
        self.wait.until(EC.invisibility_of_element(acceptCookieBtn))

    def scrapeDeals(self):
        self.wait.until(EC.invisibility_of_element(self.loadingSpinner))

        deals = self.wait.until(
            EC.visibility_of_all_elements_located(self.productCard)
        )

        products = []
        for deal in deals:
            try:
                product = Product.from_card(deal)
            except Exception:
                continue
            products.append(product)
            orig = product.original_price or "-"
            print(f"{product.brand} | {product.name} | {product.sale_price} | Was: {orig}")
        return products

    def clickSignIn(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.signInLinkText))
        btn.click()

    def selectYourStore(self, zip_code=""):
        self.wait.until(EC.invisibility_of_element(self.loadingSpinner))
        selectAStoreButton = self.wait.until(
            EC.element_to_be_clickable(self.selectAStoreLink)
        )
        selectAStoreButton.click()

        # print("Set address clicked")
        # addressInput = self.wait.until(EC.element_to_be_clickable(self.autocompleteInputId))
        # addressInput.click()
        # addressInput.send_keys(zip_code)

        # setAsMyStoreBtn = self.wait.until(EC.element_to_be_clickable(self.setAsMyStoreId))
        # setAsMyStoreBtn.click()
        # setAsMyStoreBtn.click()

    def applyFilter(self, filterName):
        filterTextLocator = (By.CSS_SELECTOR, f"[aria-label='{filterName}']")
        filterOption = self.wait.until(EC.element_to_be_clickable(filterTextLocator))
        filterOption.click()
        return filterOption
    
    def clickClearAllFilters(self):
        clearAllFilterButton = self.wait.until(EC.element_to_be_clickable(self.clearAllFiltersText))
        ActionChains(self.driver).move_to_element(clearAllFilterButton).perform()
        
        clearAllFilterButton.click()

    def addProductToList(self):
        pass

class LuckyAddressSelenium(AddressPage, BasePageSelenium):
    selectAStoreLink = (By.XPATH, '//button[@data-testid="store-select-link"]')
    autocompleteInputId = (By.ID, "autocompleteInputId")
    setAsMyStoreId = (By.XPATH, '//button[@aria-label="Set as my Store"]')
    loadingSpinner = (By.CSS_SELECTOR, '.mantine-Loader-root')

    def searchAddress(self, location=""):
        addressInput = self.wait.until(EC.element_to_be_clickable(self.autocompleteInputId))
        addressInput.click()
        addressInput.send_keys(location)

        # Select the first option in the autocomplete suggestion
        autoCompleteOption = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(),'{location}')]")))
        autoCompleteOption.click()
        
    def setAsMyStore(self, store=""):
        cardContainer = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"[aria-label='Information group for store {store}']")))
        setAsMyStoreBtn = cardContainer.find_element(*self.setAsMyStoreId)  
        setAsMyStoreBtn.click()
        self.wait.until(EC.text_to_be_present_in_element(self.selectAStoreLink, store))

    def openDirections(self, buttonText: str):
        button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.direction-btn")))
        button.click()
        self.wait.until(EC.number_of_windows_to_be(2))

class LuckySearchPlaywright(PlaywrightSearchPage):
    acceptCookieBtnLocator = "#truste-consent-button"
    selectAStoreLink = "store-select-link"
    productCard = "product-card"
    loadingSpinner = ".mantine-Loader-root"
    clearAllFilters = "Clear all filters"
    appliedFiltersLocator = ".applied-filters-container"
    selectStoreForPricingLink = "product-card-select-store-button"
    salePriceTestId = "product-card-sale-price"
    signInLinkText = "Select to sign in or sign up"

class LuckyAddressPlaywright(PlaywrightAddressPage):
    currentLocationText = "Current location"
    autocompleteInputId = "#autocompleteInputId"
    setStoreText = "Set as my Store"
