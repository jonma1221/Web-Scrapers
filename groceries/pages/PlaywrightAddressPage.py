from playwright.async_api import Page, expect
from shared.BasePage import BasePagePlaywright
from pages.AddressPage import AddressPage


class PlaywrightAddressPage(AddressPage, BasePagePlaywright):
    storeCardList = ".swiftly-address-item"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # self.searchBar = page.get_by_role("combobox", name=self.currentLocationText)
        self.searchBar = page.get_by_role("combobox").and_(page.locator(self.autocompleteInputId))
        self.storeCards = page.locator(self.storeCardList)

    def searchOption(self, location: str):
        return self.page.get_by_role("option", name=location)

    async def searchAddress(self, location) -> str:
        await self.searchBar.fill(location)
        exact = self.searchOption(location)
        try:
            await exact.first.wait_for(state="visible", timeout=15000)
            resolved = exact.first
        except Exception:
            resolved = None
            for option in await self.page.get_by_role("option").all():
                text = (await option.text_content() or "").strip()
                if text and "No results" not in text:
                    resolved = option
                    break
            if resolved is None:
                raise
        text = await resolved.text_content()
        await resolved.click()
        return (text or "").strip()

    async def setAsMyStore(self, address=""):
        await self.storeCards.first.wait_for(state="visible", timeout=15000)
        if address:
            card = self.storeCards.filter(has_text=address).first
            if await card.count() == 0:
                card = self.storeCards.first
        else:
            card = self.storeCards.first
        await card.get_by_role("button", name=self.setStoreText).click()

    async def openDirections(self, buttonText: str) -> Page:
        async with self.page.expect_popup() as popup_info:
            await self.page.get_by_role("button", name=buttonText).first.click()
        return await popup_info.value
