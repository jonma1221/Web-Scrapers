from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


@dataclass
class Coupon:
    brand: str
    value: str
    description: str
    expiration: str
    image_url: str
    clip_label: str = ""

    @classmethod
    def from_card_selenium(cls, card: WebElement) -> "Coupon":
        def text_of(selector: str) -> str:
            els = card.find_elements(By.CSS_SELECTOR, selector)
            return els[0].text.strip() if els else ""

        image_url = ""
        img_els = card.find_elements(By.CSS_SELECTOR, ".coupon-card-img")
        if img_els:
            image_url = img_els[0].get_attribute("src") or ""

        clip_label = ""
        clip_els = card.find_elements(By.CSS_SELECTOR, "[data-testid='coupon-clip-button']")
        if clip_els:
            clip_label = clip_els[0].get_attribute("aria-label") or ""

        return cls(
            brand=text_of("[data-testid='coupon-card-brand']"),
            value=text_of("[data-testid='coupon-card-value']"),
            description=text_of("[data-testid='coupon-card-description']"),
            expiration=(
                text_of("[data-testid='coupon-card-expiration'] .expiration-date")
                or text_of("[data-testid='coupon-card-expiration']")
            ),
            image_url=image_url,
            clip_label=clip_label,
        )