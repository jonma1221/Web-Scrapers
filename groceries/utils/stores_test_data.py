from typing import TypedDict

from models.Store import Store
from pages.AddressPage import AddressPage
from pages.SearchPage import SearchPage
from pages.FoodMaxxSearch import FoodMaxxSearchPlaywright
from pages.LuckyMeat import LuckySearchPlaywright, LuckyAddressPlaywright
from pages.SmartFinalSearch import SmartFinalSearchPagePlaywright
from pages.SmartFinalAddress import SmartFinalAddressPlaywright


# Store URLs
# Beef category URLs used across filter, location, and price tests.

LUCKY_BEEF_URL: str = (
    "https://luckysupermarkets.com/categories/Product%2Fmeat_seafood/Product%2Fbeef"
)
FOODMAXX_BEEF_URL: str = (
    "https://foodmaxx.com/categories/Product%2Fmeat_seafood/Product%2Fbeef"
)
GROCERY_OUTLET_BEEF_URL: str = (
    "https://shop.groceryoutlet.com/store/grocery-outlet/collections/n-beef-29419"
)
SMART_FINAL_BEEF_URL: str = (
    "https://www.smartandfinal.com/sm/pickup/rsid/786/categories/meat-seafood/"
    "fresh-beef-id-M-09-01?f=Breadcrumb%3Ahome%2Fmeat%2C+seafood%2Ffresh+beef"
)


# Store Select Scenarios
# Location search and store selection tests.

class StoreSelectScenario(TypedDict):
    search_cls: type[SearchPage]
    address_cls: type[AddressPage]
    url: str
    cases: list[tuple[str, str]]

STORE_SELECT_SCENARIOS: list[StoreSelectScenario] = [
    {
        "search_cls": LuckySearchPlaywright,
        "address_cls": LuckyAddressPlaywright,
        "url": LUCKY_BEEF_URL,
        "cases": [
            ("San Leandro", "San Leandro, CA US"),
            ("San Lea", "San Leandro, CA US"),       # Partial match
            ("@#$", "No results found"),              # Invalid location
        ],
    },
    {
        "search_cls": SmartFinalSearchPagePlaywright,
        "address_cls": SmartFinalAddressPlaywright,
        "url": SMART_FINAL_BEEF_URL,
        "cases": [
            ("San Leandro", "San Leandro, CA US"),
            ("San Lea", "San Leandro, CA US"),       # Partial match
            ("@#$", "Address Not Found"),             # Invalid location
        ],
    },
]


# Category Filter Test Data
# Brand filtering and filter-clearing tests.

BEEF_STORES = [
    (FoodMaxxSearchPlaywright, FOODMAXX_BEEF_URL, ["THE SAVE MART COMPANY", "SUNNYSIDE FARMS"]),
    (LuckySearchPlaywright, LUCKY_BEEF_URL, ["THE SAVE MART COMPANY", "SUNNYSIDE FARMS"]),
    (SmartFinalSearchPagePlaywright, SMART_FINAL_BEEF_URL, ["FIRST STREET", "Sun Harvest"]),
]

FILTER_CASES = [
    (cls, url, name)
    for cls, url, names in BEEF_STORES
    for name in names
]

# Scraping variations for specific stores
BEEF_STORE_URLS = [(cls, url) for cls, url, _ in BEEF_STORES]


# Store Definitions
# Store metadata for the comparison script.

STORES = [
    Store(
        name="Lucky",
        domain_key="luckysupermarkets.com",
        city_or_zip="San Leandro",
        address="FAIRMONT DR",
    ),
    Store(
        name="FoodMaxx",
        domain_key="foodmaxx.com",
        city_or_zip="San Leandro",
        address="San Leandro",
        expected_store_name="CONCORD",
    ),
]

# Login

# niyvbmglqyoqhqgcim@kjkpc.net
# Lbayj0!V%kP5%k7t