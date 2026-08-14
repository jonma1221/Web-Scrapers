from typing import TypedDict

from models.Store import Store
from pages.AddressPage import AddressPage
from pages.SearchPage import SearchPage
from pages.LuckyMeat import LuckySearchPlaywright, LuckyAddressPlaywright
from pages.SmartFinalSearch import SmartFinalSearchPagePlaywright
from pages.SmartFinalAddress import SmartFinalAddressPlaywright


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

LUCKY_BEEF_URL: str = (
    "https://luckysupermarkets.com/categories/Product%2Fmeat_seafood/Product%2Fbeef"
)
SMART_FINAL_BEEF_URL: str = (
    "https://www.smartandfinal.com/sm/pickup/rsid/786/categories/meat-seafood/"
    "fresh-beef-id-M-09-01?f=Breadcrumb%3Ahome%2Fmeat%2C+seafood%2Ffresh+beef"
)


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
            ("San Lea", "San Leandro, CA US"),  # Partial match
            ("@#$", "No results found"),  # Invalid location
        ],
    },
    {
        "search_cls": SmartFinalSearchPagePlaywright,
        "address_cls": SmartFinalAddressPlaywright,
        "url": SMART_FINAL_BEEF_URL,
        "cases": [
            ("San Leandro", "San Leandro, CA US"),
            ("San Lea", "San Leandro, CA US"),  # Partial match
            ("@#$", "Address Not Found"),  # Invalid location
        ],
    },
]
