from dataclasses import dataclass
from bs4 import Tag

@dataclass
class Deal:
    price: str
    store: str
    title: str
    url: str
    image_url: str

    @classmethod
    def from_soup(cls, tag: Tag) -> "Deal":
        price_el = tag.find('span', class_='bp-p-dealCard_price')
        store_el = tag.find('span', class_='bp-c-card_subtitle')
        title_el = tag.find('a', class_='bp-c-card_title')
        url_el = tag.find('a', class_='bp-c-card_title')
        img_el = tag.find('img', class_='bp-c-image')

        return cls(
            price=price_el.text.strip() if price_el else "N/A",
            store=store_el.text.strip() if store_el else "N/A",
            title=title_el.text.strip() if title_el else "N/A",
            url=url_el.get('href', '') if url_el else "",
            image_url=img_el.get('src', '') if img_el else "",
        )