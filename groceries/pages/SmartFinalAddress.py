import re

from playwright.async_api import Locator, Page, expect
from shared.BasePage import BasePagePlaywright
from pages.AddressPage import AddressPage


class SmartFinalAddressPlaywright(AddressPage, BasePagePlaywright):
    # AddressPage interface attributes.
    currentLocationText = "Location"
    autocompleteInputId = "AddressIntegrationSubmitButton-TestId"
    setStoreText = "My Store"

    # Header popover trigger: open it, then click "Change Store" to reveal the dialog.
    storeHeaderTestId = "storeHeader-button-testId"
    changeStoreTestId = "storeDetails-button-testId-change-store"

    # Address search dialog
    dialogName = "Shop for Pickup"

    # Address search input + submit (input is role=combobox "Location", the
    # wrapper uses a dynamic data-testid, so key off the testid directly).
    locationInputTestId = "AddressIntegrationInputField-TestId"
    submitSearchTestId = "AddressIntegrationSubmitButton-TestId"
    suggestionWrapperTestId = "AddressIntegrationSuggestionsWrapper-TestId"
    suggestionFieldTestIdPrefix = "AddressIntegrationSuggestionField-TestId-"

    # Tabs: Recent Stores / List View / Map View
    recentStoresTabTestId = "Recent Stores-tabBtn-button-testId"
    listViewTabTestId = "List View-tabBtn-button-testId"
    mapViewTabTestId = "Map View-tabBtn-button-testId"

    # Store lists: <ul> of store cards; list view (after a search) vs recent.
    recentStoresListTestId = "RecentStoresContainer-testId"
    listViewListTestId = "ListContainer-testId"
    storeNameTestId = "storeNameTestId"
    selectStoreButtonTestIdPrefix = "selectStore-button-testId-"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.dialog = page.get_by_role("dialog", name=self.dialogName)
        self.searchBar = self.dialog.get_by_test_id(self.locationInputTestId)
        self.submitSearch = self.dialog.get_by_test_id(self.submitSearchTestId)
        self.recentStoresTab = self.dialog.get_by_test_id(self.recentStoresTabTestId)
        self.listViewTab = self.dialog.get_by_test_id(self.listViewTabTestId)
        self.mapViewTab = self.dialog.get_by_test_id(self.mapViewTabTestId)
        self.recentStoresList = self.dialog.get_by_test_id(self.recentStoresListTestId)
        self.listViewList = self.dialog.get_by_test_id(self.listViewListTestId)

    async def selectYourStore(self):
        # The store header popover must be expanded first; then "Change Store"
        # swaps in the address-search dialog.
        await self.page.get_by_test_id(self.storeHeaderTestId).click()
        await self.page.get_by_test_id(self.changeStoreTestId).click()
        await expect(self.dialog).to_be_visible(timeout=15000)

    async def searchAddress(self, location):
        # Typing into the combobox surfaces a listbox of address suggestions
        # (role=option). Pick the first one; selecting it loads the List View
        # tabpanel with the matching stores.
        await self.searchBar.fill(location)
        suggestion = self.dialog.get_by_role("option").first
        await expect(suggestion).to_be_visible(timeout=10000)
        await suggestion.click()
        await expect(self.listViewList.first).to_be_visible(timeout=15000)

    def searchOption(self, location: str):
        return self.page.get_by_role("option", name=location)

    async def storeName(self, card: Locator) -> str:
        name = await card.get_by_test_id(self.storeNameTestId).text_content()
        return (name or "").strip()

    async def setAsMyStore(self, address=""):
        # The select button's accessible name is "Make <store> My Store" (or
        # "Your Active Store" when it's already the active pickup location).
        await self.dialog.get_by_role("button", name=re.compile(
            rf"Make {re.escape(address)} My Store"
        )).click()

    async def isActiveStore(self, card: Locator) -> bool:
        selectBtn = card.locator(f"[data-testid^='{self.selectStoreButtonTestIdPrefix}']")
        # The active store's select button is disabled and reads "Your Active Store".
        return await selectBtn.count() > 0 and not await selectBtn.is_enabled()

    async def openDirections(self, buttonText: str):
        # No in-dialog directions flow on this page; the store cards link to
        # "Browse Store" pages instead. Intentional no-op.
        pass

    async def close(self):
        closeBtn = self.dialog.get_by_role("button", name=re.compile(r"^Close"))
        await closeBtn.click()