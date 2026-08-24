from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.async_api import Page, expect

class BasePageSelenium:
    BASE_TIMEOUT = 10
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.BASE_TIMEOUT)
    
    def getElement(self, selector, *, condition = EC.visibility_of_element_located) -> WebElement:
        return self.wait.until(condition(selector))
    
class BasePagePlaywright:
    def __init__(self, page: Page) -> None:
        self.page = page
    
    async def goTo(self, url):
        await self.page.goto(url)