from shared.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.AddressPage import AddressPage
from pages.PlaywrightAddressPage import PlaywrightAddressPage


class FoodMaxxAddress(AddressPage, BasePage):
    currentLocationText = "Current location"
    setStoreText = "Set as My Store"
    autocompleteInput = (By.ID, "autocompleteInputId")
    storeCardList = (By.CSS_SELECTOR, ".store-cards-list")
    storeCard = (By.CSS_SELECTOR, ".swiftly-address-item")
    setAsMyStoreBtn = (By.XPATH, '//button[@aria-label="Set as my Store"]')

    def __init__(self, driver):
        BasePage.__init__(self, driver)

    def searchAddress(self, location):
        searchBar = self.wait.until(
            EC.element_to_be_clickable(self.autocompleteInput)
        )
        searchBar.clear()
        searchBar.send_keys(location)

    def setAsMyStore(self, index=0):
        stores = self.wait.until(
            EC.presence_of_all_elements_located(self.storeCard)
        )
        setStoreBtn = stores[index].find_element(*self.setAsMyStoreBtn)
        setStoreBtn.click()
        setStoreBtn.click()
        print("Set as my store clicked")


class FoodMaxxAddressPlaywright(PlaywrightAddressPage):
    currentLocationText = "Current location"
    setStoreText = "Set as My Store"
