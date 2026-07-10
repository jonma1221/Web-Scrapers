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

safewayWeeklyAdUrl = "https://www.safeway.com/weeklyad"
safeWayMeatProducts = "https://www.safeway.com/shop/aisles/meat-seafood/beef.html?page=1&sort=&offerType=Y&loc=3132"
driver = webdriver.Chrome()
driver.maximize_window()

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

# meatProducts = "https://luckysupermarkets.com/categories/Product%2Fmeat_seafood/Product%2Fbeef"
# porkProducts = "https://luckysupermarkets.com/categories/Product%2Fmeat_seafood/Product%2Fpork"
# driver.get(meatProducts)
# luckyMeat = LuckyMeat(driver)
# luckyMeat.acceptCookies()
# luckyMeat.selectAStore()
# luckyMeat.scrapeDeals()

beefProducts = "https://foodmaxx.com/categories/Product%2Fmeat_seafood/Product%2Fpork"
porkProducts = "https://foodmaxx.com/categories/Product%2Fmeat_seafood/Product%2Fbeef"
driver.get(porkProducts)
foodMaxxSearchResults = FoodMaxxSearch(driver)
foodMaxxSearchResults.acceptCookies()
foodMaxxSearchResults.selectYourStore()

foodMaxxAddressList = FoodMaxxAddress(driver)
foodMaxxAddressList.searchAddress("94506")
foodMaxxAddressList.setAsMyStore()

foodMaxxSearchResults.scrapeDeals()
driver.quit()