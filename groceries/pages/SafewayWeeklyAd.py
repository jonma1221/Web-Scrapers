
from shared.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import bs4

class SafewayWeeklyAd(BasePage):
    address = (By.ID, "openFulfillmentModalButton")
    acceptCookieBtnLocator = (By.ID, "onetrust-accept-btn-handler")
    all_deals = (By.CSS_SELECTOR, ".item-overlay")
    flipp_main_iframe = (By.CSS_SELECTOR, "iframe.flippiframe.mainframe")

    def acceptCookies(self):
        acceptCookiesBtn = self.wait.until(EC.element_to_be_clickable(self.acceptCookieBtnLocator))
        acceptCookiesBtn.click()

    def waitForAdLoaded(self):
        iframe = self.wait.until(EC.presence_of_element_located(self.flipp_main_iframe))
        self.driver.switch_to.frame(iframe)
        try:
            self.wait.until(EC.presence_of_element_located(self.all_deals))
        except:
            dump_path = "error_dump.html"
            with open(dump_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
        finally:
            self.driver.switch_to.default_content()

    def clickAddressLocator(self):
        addressUpdate = self.wait.until(EC.element_to_be_clickable(self.address))
        addressUpdate.click()

    def scrapeDeals(self):
        iframe = self.wait.until(EC.presence_of_element_located(self.flipp_main_iframe))
        self.driver.switch_to.frame(iframe)

        deals = self.wait.until(
            EC.presence_of_all_elements_located(self.all_deals)
        )
        # for deal in deals:
        #     print(deal.get_attribute("aria-label"))


        soup = bs4.BeautifulSoup(self.driver.page_source, "html.parser")
        deals = soup.find_all(class_="item-overlay")
        for deal in deals:
            print(deal)
            
        self.driver.switch_to.default_content()