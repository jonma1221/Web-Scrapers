from shared.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time
from selenium.common.exceptions import TimeoutException

class LuckyMeat(BasePage):

    acceptCookieBtnLocator = (By.ID, "truste-consent-button")
    productCard = (By.XPATH, '//*[@data-testid="product-card" and @aria-label]')
    selectAStoreLink = (By.XPATH, '//button[@data-testid="store-select-link"]')
    autocompleteInputId = (By.ID, "autocompleteInputId")
    setAsMyStoreId = (By.XPATH, '//button[@aria-label="Set as my Store"]')
    productCardSalePrice = (By.XPATH, './/p[@data-testid="product-card-sale-price"]')

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
        print(f"Found {len(deals)} deal(s)")
        for deal in deals:
            sale_prices = deal.find_elements(*self.productCardSalePrice)
            if sale_prices:
                print(f"{deal.text} | SALE: {sale_prices[0].text}\n")
            else:
                print(f"{deal.text}\n")
        
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
         