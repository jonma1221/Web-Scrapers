import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from shared.BasePage import BasePageSelenium, BasePagePlaywright

class VideoGamePage(BasePageSelenium):
    sortDropdown = (By.CSS_SELECTOR, "[id$='-ListPicker']")

    def clickDropDown(self):
        try:
            select = Select(self.wait.until(EC.presence_of_element_located(self.sortDropdown)))
            print(select.options)
            select.select_by_value("newest")
        except:
            dump_path = "error_dump.html"
            with open(dump_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print(f"HTML DOM dumped successfully to {os.path.abspath(dump_path)}")

class VideoGamePagePlaywright(BasePagePlaywright):
    async def clickDropDown(self):
        # sortBy = self.page.locator("[id$='-ListPicker']")
        sortBy = self.page.get_by_role("combobox")
        await sortBy.select_option("newest")