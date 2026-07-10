import time
from shared.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from models.Product import Product

class LuckyMeat(BasePage):

    acceptCookieBtnLocator = (By.ID, "truste-consent-button")
    productCard = (By.XPATH, '//*[@data-testid="product-card" and @aria-label]')
    selectAStoreLink = (By.XPATH, '//button[@data-testid="store-select-link"]')
    autocompleteInputId = (By.ID, "autocompleteInputId")
    setAsMyStoreId = (By.XPATH, '//button[@aria-label="Set as my Store"]')
    def acceptCookies(self):
        """
        <button id="truste-consent-button" tabindex="0">Accept All</button>
        """
        acceptCookieBtn = self.wait.until(EC.presence_of_element_located(self.acceptCookieBtnLocator))
        acceptCookieBtn.click()

        # Wait for cookie banner to be removed (re-render triggered)
        self.wait.until(EC.staleness_of(acceptCookieBtn))
        # Wait for fresh DOM element to confirm re-render completed
        self.wait.until(EC.presence_of_element_located(self.selectAStoreLink))


    def scrapeDeals(self):
        time.sleep(5)
        deals = self.wait.until(EC.presence_of_all_elements_located(self.productCard))
        dump_path = "deals.html"
        with open(dump_path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        print(f"Found {len(deals)} deal(s)")
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
        
    def selectAStore(self):
        for i in range(5):
            print(f"Loop {i}")
            try:
                selectAStoreButton = self.wait.until(EC.element_to_be_clickable(self.selectAStoreLink))
                selectAStoreButton.click()
                break
            except StaleElementReferenceException:
                continue
        print("Set address clicked")
        addressInput = self.wait.until(EC.element_to_be_clickable(self.autocompleteInputId))
        addressInput.click()
        addressInput.send_keys("94506")

        setAsMyStoreBtn = self.wait.until(EC.element_to_be_clickable(self.setAsMyStoreId))
        setAsMyStoreBtn.click()
        setAsMyStoreBtn.click()
         