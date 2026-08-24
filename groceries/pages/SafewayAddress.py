from shared.BasePage import BasePageSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class SafewayAddress(BasePageSelenium):
    zipInput = (By.CSS_SELECTOR, "[placeholder='Enter ZIP Code to get started.']")
    selectFirstStore = (By.XPATH, "//a[text()='Select']")
    iconSearch = (By.CSS_SELECTOR, "[aria-label='search Zipcode']")
    addressList = (By.CSS_SELECTOR, ".card-store.row")
    def searchAddress(self, location):
       searchBar = self.wait.until(EC.element_to_be_clickable(self.zipInput))
       searchBar.clear()
       searchBar.send_keys(location)
    
    def clickSearchIcon(self):
        try:
            searchIcon = self.wait.until(EC.element_to_be_clickable(self.iconSearch))
            searchIcon.click()
        except:
            dump_path = "error_dump.html"
            with open(dump_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)

    def waitForAddressList(self):
        addressSearchResults = self.wait.until(EC.visibility_of_element_located(self.addressList))
        print(addressSearchResults)
        
    def selectAddressOption(self):
        searchItem = self.wait.until(EC.presence_of_element_located(self.selectFirstStore))
        searchItem.click()