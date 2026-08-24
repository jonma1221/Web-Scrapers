from shared.BasePage import BasePageSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.AddressPage import AddressPage
from pages.PlaywrightAddressPage import PlaywrightAddressPage


class FoodMaxxAddressSelenium(AddressPage, BasePageSelenium):
    currentLocationText = "Current location"
    setStoreText = "Set as My Store"
    autocompleteInputId = (By.ID, "autocompleteInputId")
    storeCardList = (By.CSS_SELECTOR, ".store-cards-list")
    storeCard = (By.CSS_SELECTOR, ".swiftly-address-item")

    selectAStoreLink = (By.XPATH, '//button[@data-testid="store-select-link"]')
    setAsMyStoreId = (By.XPATH, './/button[@aria-label="Set as my Store"]')
    loadingSpinner = (By.CSS_SELECTOR, '.mantine-Loader-root')

    def searchAddress(self, location):
        addressInput = self.wait.until(EC.element_to_be_clickable(self.autocompleteInputId))
        addressInput.click()
        addressInput.send_keys(location)

        # Select the first option in the autocomplete suggestion
        autoCompleteOption = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(),'{location}')]")))
        autoCompleteOption.click()

    def setAsMyStore(self, store=""):
        cardContainer = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"[aria-label='Information group for store {store}']")))
        print(cardContainer.text)
        setAsMyStoreBtn = cardContainer.find_element(*self.setAsMyStoreId)  
        print(setAsMyStoreBtn.text)
        setAsMyStoreBtn.click()
        self.wait.until(EC.text_to_be_present_in_element(self.selectAStoreLink, store))

    def openDirections(self, buttonText: str):
        pass
    
class FoodMaxxAddressPlaywright(PlaywrightAddressPage):
    currentLocationText = "Current location"
    autocompleteInputId = "#autocompleteInputId"
    setStoreText = "Set as My Store"
