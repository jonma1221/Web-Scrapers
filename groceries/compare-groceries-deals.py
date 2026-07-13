import sys
import time

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver
from pages.SafewayWeeklyAd import SafewayWeeklyAd
from pages.SafewayAddress import SafewayAddress
from pages.LuckyMeat import LuckyMeat
from pages.FoodMaxxAddress import FoodMaxxAddress
from pages.FoodMaxxSearch import FoodMaxxSearch
from meat_compare.category_urls import CATEGORY_URLS
safewayWeeklyAdUrl = "https://www.safeway.com/weeklyad"
safeWayMeatProducts = "https://www.safeway.com/shop/aisles/meat-seafood/beef.html?page=1&sort=&offerType=Y&loc=3132"
driver = webdriver.Chrome()

# driver.get(safewayWeeklyAdUrl)

# safewayWeeklyAd = SafewayWeeklyAd(driver)
# safewayWeeklyAd.acceptCookies()
# safewayWeeklyAd.clickAddressLocator()

# userAddress = "94506"
# safewayAddress = SafewayAddress(driver)
# safewayAddress.searchAddress(userAddress)
# safewayAddress.clickSearchIcon()
# safewayAddress.waitForAddressList()
# safewayAddress.selectAddressOption()

# safewayWeeklyAd.waitForAdLoaded()
# safewayWeeklyAd.scrapeDeals()

# Scrape Lucky
url = CATEGORY_URLS["luckysupermarkets.com"]["beef"]
driver.get(url)
luckyMeat = LuckyMeat(driver)
luckyMeat.acceptCookies()
luckyMeat.selectYourStore("94506")
luckyMeat.scrapeDeals()

# Scrape Food Maxx
url = CATEGORY_URLS["foodmaxx.com"]["beef"]
driver.get(url)
foodMaxxSearchResults = FoodMaxxSearch(driver)
foodMaxxSearchResults.acceptCookies()
foodMaxxSearchResults.selectYourStore()

foodMaxxAddressList = FoodMaxxAddress(driver)
foodMaxxAddressList.searchAddress("94506")
foodMaxxAddressList.setAsMyStore()

foodMaxxSearchResults.scrapeDeals()

current_page = foodMaxxSearchResults.getCurrentPageNum()
nextPage = foodMaxxSearchResults.clickNextBtn()

# Assert that we are on the next page
assert nextPage == current_page + 1

foodMaxxSearchResults.scrollToTop()
foodMaxxSearchResults.scrapeDeals()
driver.quit()