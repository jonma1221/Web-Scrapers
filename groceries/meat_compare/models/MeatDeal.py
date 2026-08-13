from dataclasses import dataclass
from models.Product import Product


@dataclass
class MeatDeal:
    brand: str
    name: str
    sale_price: str
    original_price: str | None
    image_url: str
    store_name: str
    category: str
    url: str = ""

    @classmethod
    def from_product(cls, product: Product, store_name: str, category: str) -> "MeatDeal":
        return cls(
            brand=product.brand,
            name=product.name,
            sale_price=product.sale_price,
            original_price=product.original_price,
            image_url=product.image_url,
            store_name=store_name,
            category=category,
            url=product.url,
        )
