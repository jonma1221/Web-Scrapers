from shared.BasePage import BasePageSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from models.Product import Product


class SafewaySearch(BasePageSelenium):
    acceptCookieBtnLocator = (By.ID, "onetrust-accept-btn-handler")
    searchInput = (By.CLASS_NAME, "search-nav__input")
    productCardContainer = (By.CLASS_NAME, "product-card-container")

    def acceptCookies(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.acceptCookieBtnLocator))
        btn.click()

    def searchForProduct(self, query: str):
        box = self.wait.until(EC.element_to_be_clickable(self.searchInput))
        box.clear()
        box.send_keys(query)
        box.send_keys(Keys.RETURN)

    def scrapeDeals(self):
        cards = self.wait.until(
            EC.presence_of_all_elements_located(self.productCardContainer)
        )
        products = []
        for card in cards:
            try:
                product = Product.from_safeway_search(card)
            except Exception:
                continue
            products.append(product)
            orig = product.original_price or "-"
            print(f"{product.name} | {product.sale_price} | Was: {orig}")
        return products