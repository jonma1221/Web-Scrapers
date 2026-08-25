import pytest
from playwright.async_api import expect

from pages.GroceryOutletSearch import GroceryOutletSearchPagePlaywright
from utils.stores_test_data import GROCERY_OUTLET_BEEF_URL

@pytest.mark.parametrize("location", [("517 Mantova Court")])
@pytest.mark.asyncio
async def test_select_address_updates_delivery_to(groceryOutletSearchPage: GroceryOutletSearchPagePlaywright, location):
    await groceryOutletSearchPage.goTo(GROCERY_OUTLET_BEEF_URL)

    await groceryOutletSearchPage.selectYourStore(location)

    await expect(groceryOutletSearchPage.deliveryToTrigger).to_contain_text(location)
