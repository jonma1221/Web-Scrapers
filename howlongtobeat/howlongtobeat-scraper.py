import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


from pages.MainPage import MainPage
from pages.LoginPage import LoginPage
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://howlongtobeat.com/")
hltbMainPage = MainPage(driver)
hltbMainPage.clickConsent()
hltbMainPage.clickLogin()

hltbLoginPage = LoginPage(driver)
hltbLoginPage.clickLoginInput()
hltbLoginPage.clickPasswordInput()