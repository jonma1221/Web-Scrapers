from shared.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from models.Product import Product
from pages.SearchPage import SearchPage
from pages.PlaywrightSearchPage import PlaywrightSearchPage

class FoodMaxxSearch(SearchPage, BasePage):
    acceptCookieBtnLocator = (By.ID, "truste-consent-button")
    signInLinkText = (By.XPATH, "//button[text()='Select to sign in or sign up']")
    selectAStoreLink = (By.XPATH, '//button[@data-testid="store-select-link"]')
    productCard = (By.XPATH, '//*[@data-testid="product-card" and @aria-label]')
    nextResultsPage = (By.XPATH, '//button[@aria-label="next-btn"]')
    activePage = (By.CSS_SELECTOR, 'button[data-active="true"][aria-current="page"]')
    loadingSpinner = (By.CSS_SELECTOR, '.mantine-Loader-root')

    def acceptCookies(self):
        acceptCookieBtn = self.wait.until(
            EC.presence_of_element_located(self.acceptCookieBtnLocator)
        )
        acceptCookieBtn.click()
        self.wait.until(EC.staleness_of(acceptCookieBtn))

    def clickSignIn(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.signInLinkText))
        btn.click()

    def selectYourStore(self):
        self.wait.until(EC.invisibility_of_element(self.loadingSpinner))

        selectAStoreButton = self.wait.until(
            EC.element_to_be_clickable(self.selectAStoreLink)
        )
        selectAStoreButton.click()

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

    def scrollToTop(self):
        self.wait.until(EC.presence_of_all_elements_located(self.productCard))
        self.driver.execute_script("window.scrollTo(0, 0);")

    def getCurrentPageNum(self):
        activeBtn = self.wait.until(EC.presence_of_element_located(self.activePage))
        return int(activeBtn.text)

    def clickNextBtn(self):
        current_page = self.getCurrentPageNum()
        nextBtn = self.wait.until(EC.element_to_be_clickable(self.nextResultsPage))
        nextBtn.click()
        expected_page = current_page + 1
        # Wait for the next page to be shown as selected
        self.wait.until(EC.text_to_be_present_in_element(self.activePage, str(expected_page)))
        new_active = self.driver.find_element(*self.activePage)
        print(f"current_page {current_page}, new_active.text: {new_active.text}")
        return int(new_active.text)


class FoodMaxxSearchPlaywright(PlaywrightSearchPage):
    acceptCookieBtnLocator = "#truste-consent-button"
    selectAStoreLink = "store-select-link"
    productCard = "product-card"
    loadingSpinner = ".mantine-Loader-root"
    clearAllFilters = "Clear all filters"
    appliedFiltersLocator = ".applied-filters-container"
    selectStoreForPricingLink = "product-card-select-store-button"
    salePriceTestId = "product-card-sale-price"
    signInLinkText = "Select to sign in or sign up"
