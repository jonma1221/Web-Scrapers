import bs4
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from models.Deal import Deal
from pages.MainPage import MainPage
from pages.CategoriesPage import CategoriesPage
from pages.VideoGamePage import VideoGamePage

driver = webdriver.Chrome()
driver.get("https://slickdeals.net/")
wait = WebDriverWait(driver, 5)

mainPage = MainPage(driver)
mainPage.clickCategories()
mainPage.clickViewAllCategories()

categoryPage = CategoriesPage(driver)
categoryPage.clickCategory()

videoGamesPage = VideoGamePage(driver)
videoGamesPage.clickDropDown()

# parse through the html and find the deals
soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
deals = soup.find_all("li", attrs={"data-catalog-item": "DealCard"})
for deal in deals:
    deal = Deal.from_soup(deal)
    print(f"Title: {deal.title}, Price: {deal.price}, Store: {deal.store}, URL: {deal.url}, Image URL: {deal.image_url}")

driver.quit()