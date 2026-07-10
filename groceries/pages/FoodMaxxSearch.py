import time
from shared.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from models.Product import Product


class FoodMaxxSearch(BasePage):
    acceptCookieBtnLocator = (By.ID, "truste-consent-button")
    selectAStoreLink = (By.XPATH, '//button[@data-testid="store-select-link"]')
    productCard = (By.XPATH, '//*[@data-testid="product-card" and @aria-label]')

    def acceptCookies(self):
        acceptCookieBtn = self.wait.until(
            EC.presence_of_element_located(self.acceptCookieBtnLocator)
        )
        acceptCookieBtn.click()
        self.wait.until(EC.staleness_of(acceptCookieBtn))
        self.wait.until(EC.presence_of_element_located(self.selectAStoreLink))

    def selectYourStore(self):
        for i in range(5):
            try:
                selectAStoreButton = self.wait.until(
                    EC.element_to_be_clickable(self.selectAStoreLink)
                )
                selectAStoreButton.click()
                return
            except StaleElementReferenceException:
                continue

    def scrapeDeals(self):
        time.sleep(5)
        deals = self.wait.until(
            EC.presence_of_all_elements_located(self.productCard)
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
