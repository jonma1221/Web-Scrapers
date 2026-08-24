import re

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
        self.store_location: str | None = None

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

    async def setAsMyStore(self, store=""):
        await self.storeCards.first.wait_for(state="visible", timeout=15000)
        if store:
            card = self.storeCards.filter(has_text=store).first
            if await card.count() == 0:
                card = self.storeCards.first
        else:
            card = self.storeCards.first

        label = (await card.get_attribute("aria-label") or "").strip()
        text = (await card.text_content() or "").strip()
        self.store_location = self._location_from_card(label, text)
        await card.get_by_role("button", name=self.setStoreText).click()

    @staticmethod
    def _location_from_card(label: str, text: str) -> str:
        """Derive a 'Store — Address' label from a store-card's aria-label + body."""
        name = re.sub(r"^.*\bstore\b\s*", "", label, flags=re.IGNORECASE).strip()
        match = re.search(r"Address:\s*(.*?)(?:\.\s*Distance:|$)", text)
        address = match.group(1).strip() if match else ""
        return " — ".join(part for part in (name, address) if part)

    async def openDirections(self, buttonText: str) -> Page:
        async with self.page.expect_popup() as popup_info:
            await self.page.get_by_role("button", name=buttonText).first.click()
        return await popup_info.value
