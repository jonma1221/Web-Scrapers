from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from shared.BasePage import BasePageSelenium, BasePagePlaywright

class MainPage(BasePageSelenium):
    # Locators
    dealCard = (By.CSS_SELECTOR, "[data-catalog-item='DealCard']")
    categoriesDropdown = '[data-qa-header-dropdown-button="categories"]'
    viewAllCategoriesBtn = (By.XPATH, '//a[contains(@class, "slickdealsHeaderDropdownItem__link") and .//span[text()="View All Categories"]]')

    def get_deals(self):
        deals = self.wait.until(EC.presence_of_all_elements_located(self.dealCard))
        return deals

    def clickCategories(self):
        categories = self.driver.find_element(By.CSS_SELECTOR, self.categoriesDropdown)
        categories.click()

    def clickViewAllCategories(self):
        viewAllCategories = self.wait.until(EC.element_to_be_clickable(self.viewAllCategoriesBtn))

        ActionChains(self.driver).scroll_to_element(viewAllCategories).perform()
        viewAllCategories.click()


class MainPagePlaywright(BasePagePlaywright):

    async def clickCategories(self):
        categories = self.page.get_by_text("Categories Popular")
        await categories.click()

    async def clickViewAllCategories(self):
        viewAllCategories = self.page.get_by_role("link", name="View All Categories")
        await viewAllCategories.click()