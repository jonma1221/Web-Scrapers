from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from playwright.async_api import Page, expect

class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    
class BasePagePlaywright:
    def __init__(self, page: Page) -> None:
        self.page = page
    
    async def goTo(self, url):
        await self.page.goto(url)