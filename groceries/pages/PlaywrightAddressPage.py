from playwright.async_api import Page, expect
from shared.BasePage import BasePagePlaywright
from pages.AddressPage import AddressPage


class PlaywrightAddressPage(AddressPage, BasePagePlaywright):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # self.searchBar = page.get_by_role("combobox", name=self.currentLocationText)
        self.searchBar = page.get_by_role("combobox").and_(page.locator(self.autocompleteInputId))

    def searchOption(self, location: str):
        return self.page.get_by_role("option", name=location)

    async def searchAddress(self, location):
        await self.searchBar.fill(location)
        await self.searchOption(location).click()

    async def setAsMyStore(self, address=""):
        if address:
            setStoreBtn = self.page.get_by_label(text=address).get_by_role("button", name=self.setStoreText)
        else:
            setStoreBtn = self.page.get_by_role("button", name=self.setStoreText).first
        await setStoreBtn.click()

    async def openDirections(self, buttonText: str) -> Page:
        async with self.page.expect_popup() as popup_info:
            await self.page.get_by_role("button", name=buttonText).first.click()
        return await popup_info.value
