import re
from dataclasses import dataclass
from playwright.async_api import Locator
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def _resolve_href(url: str, base: str = "") -> str:
    """Resolve a possibly-relative product href against a store domain.

    Returns "" when there is no usable href. Skips obviously non-product
    links (hashes, search URLs, generic anchors) so a card's "Add to list"
    or "Sign in" anchor never masquerades as a product page.
    """
    href = (url or "").strip()
    if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
        return ""
    if href.startswith("/search"):
        return ""
    if href.startswith("//"):
        return f"https:{href}"
    if href.startswith("/"):
        return f"{base.rstrip('/')}{href}" if base else ""
    return href


def _selenium_product_href(card: WebElement) -> str:
    """Best-effort product-page URL from a Selenium card element."""
    try:
        anchors = card.find_elements(By.CSS_SELECTOR, "a[href]")
        for anchor in anchors:
            href = anchor.get_attribute("href") or ""
            if "product-details" in href or "products/" in href:
                return _resolve_href(href)
        for anchor in anchors:
            resolved = _resolve_href(anchor.get_attribute("href") or "")
            if resolved:
                return resolved
    except Exception:
        pass
    return ""


async def _playwright_product_href(card: Locator) -> str:
    """Best-effort product-page URL from a Playwright card locator."""
    try:
        anchors = await card.locator("a[href]").all()
        for anchor in anchors:
            href = await anchor.get_attribute("href") or ""
            if "product-details" in href or "products/" in href:
                return _resolve_href(href)
        for anchor in anchors:
            resolved = _resolve_href(await anchor.get_attribute("href") or "")
            if resolved:
                return resolved
    except Exception:
        pass
    return ""


@dataclass
class Product:
    brand: str
    name: str
    sale_price: str
    original_price: str | None
    image_url: str
    url: str = ""

    @classmethod
    def from_card(cls, card: WebElement) -> "Product":
        aria = card.get_attribute("aria-label")

        brand_m = re.search(r"Product Brand:\s*(.+?)\.", aria)
        name_m = re.search(r"Product Name:\s*(.+?)\.\s*(?:Sale Price:|Price:|$)", aria)
        brand = brand_m.group(1).strip() if brand_m else ""
        name = name_m.group(1).strip() if name_m else ""

        image_els = card.find_elements(By.CSS_SELECTOR, "[data-testid='product-card-image']")
        image_url = image_els[0].get_attribute("src") or "" if image_els else ""

        sale_els = card.find_elements(
            By.CSS_SELECTOR, "[data-testid='product-card-sale-price']"
        )
        if sale_els:
            sale_price = sale_els[0].text.strip()
            try:
                orig = sale_els[0].find_element(
                    By.XPATH, "./parent::div/following-sibling::div/p"
                )
                original_price = orig.text.strip()
            except Exception:
                original_price = None
        else:
            price_els = card.find_elements(By.CSS_SELECTOR, "p[aria-label^='Price:']")
            sale_price = price_els[0].text.strip() if price_els else ""
            original_price = None

        return cls(
            brand=brand,
            name=name,
            sale_price=sale_price,
            original_price=original_price,
            image_url=image_url,
            url=_selenium_product_href(card),
        )

    @classmethod
    async def from_card_pw(cls, card: Locator) -> "Product":
        aria = await card.get_attribute("aria-label") or ""

        brand_m = re.search(r"Product Brand:\s*(.+?)\.", aria)
        name_m = re.search(r"Product Name:\s*(.+?)\.\s*(?:Sale Price:|Price:|$)", aria)
        brand = brand_m.group(1).strip() if brand_m else ""
        name = name_m.group(1).strip() if name_m else ""

        image_els = await card.locator("[data-testid='product-card-image']").all()
        image_url = await image_els[0].get_attribute("src") or "" if image_els else ""

        sale_els = await card.locator("[data-testid='product-card-sale-price']").all()
        if sale_els:
            sale_price = (await sale_els[0].text_content() or "").strip()
            orig = sale_els[0].locator("xpath=./parent::div/following-sibling::div/p")
            original_price = (await orig.text_content() or "").strip() or None
        else:
            price_els = await card.locator("p[aria-label^='Price:']").all()
            sale_price = (await price_els[0].text_content() or "").strip() if price_els else ""
            original_price = None

        return cls(
            brand=brand,
            name=name,
            sale_price=sale_price,
            original_price=original_price,
            image_url=image_url,
            url=await _playwright_product_href(card),
        )

    @classmethod
    def from_safeway_ad(cls, overlay: WebElement) -> "Product":
        aria = overlay.get_attribute("aria-label") or ""

        sale_price = ""
        multi_m = re.search(r"\d+\s+for\s+\$[\d.]+", aria)
        if multi_m:
            sale_price = multi_m.group(0)
        else:
            price_m = re.search(r"\$[\d.]+(?:\s*(?:ea|lb|/lb|each))?", aria)
            if price_m:
                sale_price = price_m.group(0)

        name = re.sub(
            r",\s*(?:\d+\s+for\s+\$[\d.]+|\$[\d.]+(?:\s*(?:ea|lb|/lb|each))?)\s*member price.*$",
            "", aria
        )
        name = re.sub(
            r",\s*(?:BUY\s+\d+\s+GET\s+\d+\s+FREE|EARN\s+[\dXx]+\s+POINTS?)\s*,?\s*(?:Member Price.*)?$",
            "", name
        )
        name = re.sub(r",\s*,?\s*$", "", name)
        name = name.strip().rstrip(",").strip()

        return cls(
            brand="",
            name=name,
            sale_price=sale_price,
            original_price=None,
            image_url="",
        )

    @classmethod
    async def from_smartfinal(cls, card: Locator) -> "Product":
        """Parse a Smart & Final (Mercatus) product card."""
        name_el = card.locator("[data-testid$='-ProductNameTestId']")
        name = (await name_el.text_content() or "").strip()
        name = name.removesuffix("Open Product Description").strip()

        brand_el = card.locator("[data-testid='ProductCardAQABrand']")
        brand = (await brand_el.text_content() or "").strip()

        image_els = await card.locator("img").all()
        image_url = await image_els[0].get_attribute("src") or "" if image_els else ""

        price_el = card.locator("[data-testid='productCardPricing-div-testId']").first
        sale_price = (await price_el.text_content() or "").strip()

        was_el = card.locator("[data-testid='ProductCardWasPrice-testid']")
        original_price = None
        if await was_el.count():
            text = (await was_el.text_content() or "").strip()
            original_price = re.sub(r"^was\s*", "", text, flags=re.IGNORECASE).strip() or None

        return cls(
            brand=brand,
            name=name,
            sale_price=sale_price,
            original_price=original_price,
            image_url=image_url,
            url=await _playwright_product_href(card),
        )

    @classmethod
    async def from_grocery_outlet(cls, card: Locator) -> "Product":
        name_el = card.locator("h3.e-1gh06cz")
        name = (await name_el.text_content() or "").strip()

        image_els = await card.locator("[data-testid='item-card-image']").all()
        image_url = await image_els[0].get_attribute("src") or "" if image_els else ""

        price_els = await card.locator("span", has_text="Current price:").all()
        sale_price = ""
        if price_els:
            price_text = (await price_els[0].text_content() or "").strip()
            price_m = re.search(r"\$[\d.]+", price_text)
            if price_m:
                sale_price = price_m.group(0)

        return cls(
            brand="",
            name=name,
            sale_price=sale_price,
            original_price=None,
            image_url=image_url,
            url=await _playwright_product_href(card),
        )

    @classmethod
    def from_safeway_search(cls, card: WebElement) -> "Product":
        name_el = card.find_element(By.CLASS_NAME, "product-title__name")
        name = name_el.text.strip()

        image_url = ""
        try:
            img = card.find_element(By.CLASS_NAME, "product-card-container__product-image")
            image_url = img.get_attribute("src") or ""
        except Exception:
            pass

        sale_price = ""
        try:
            price_el = card.find_element(By.CSS_SELECTOR, "[data-qa='prd-itm-prc']")
            sr = price_el.find_element(By.CLASS_NAME, "sr-only")
            sale_price = sr.text.strip()
        except Exception:
            pass

        original_price = None
        try:
            orig_el = card.find_element(By.CSS_SELECTOR, "[data-qa='prd-itm-prc-del']")
            sr = orig_el.find_element(By.CLASS_NAME, "sr-only")
            original_price = sr.text.strip()
        except Exception:
            pass

        return cls(
            brand="",
            name=name,
            sale_price=sale_price,
            original_price=original_price,
            image_url=image_url,
        )
