import re
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


@dataclass
class Product:
    brand: str
    name: str
    sale_price: str
    original_price: str | None
    image_url: str

    @classmethod
    def from_card(cls, card: WebElement) -> "Product":
        aria = card.get_attribute("aria-label")

        brand_m = re.search(r"Product Brand:\s*(.+?)\.", aria)
        name_m = re.search(r"Product Name:\s*(.+?)\.\s+(?:Sale Price:|Price:)", aria)
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
