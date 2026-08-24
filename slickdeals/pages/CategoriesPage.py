from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from shared.BasePage import BasePageSelenium, BasePagePlaywright

class CategoriesPage(BasePageSelenium):
    videoGameCategory = (By.XPATH, '//*[@id="pageContent"]/div/div[2]/ul/li[29]/a')

    def clickCategory(self):
        videoGameDeals = self.wait.until(EC.element_to_be_clickable(self.videoGameCategory))
        videoGameDeals.click()

class CategoriesPagePlaywright(BasePagePlaywright):
    videoGameCategory = ''

    async def clickCategory(self):
        videoGameDeals = self.page.get_by_role("link", name=" Video Games")
        await videoGameDeals.click()
