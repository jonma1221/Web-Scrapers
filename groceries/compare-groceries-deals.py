import sys
from pathlib import Path



sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver

from pages.SafewayWeeklyAd import SafewayWeeklyAd
from pages.SafewayAddress import SafewayAddress
from pages.LuckyMeat import LuckyMeat

driver = webdriver.Chrome()
# driver.get("https://www.safeway.com/weeklyad")

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

meatProducts = "https://luckysupermarkets.com/categories/Product%2Fmeat_seafood/Product%2Fbeef"
porkProducts = "https://luckysupermarkets.com/categories/Product%2Fmeat_seafood/Product%2Fpork"
driver.get(meatProducts)
luckyMeat = LuckyMeat(driver)
luckyMeat.acceptCookies()
luckyMeat.selectAStore()
luckyMeat.scrapeDeals()

driver.quit()