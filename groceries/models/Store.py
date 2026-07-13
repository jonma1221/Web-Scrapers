from dataclasses import dataclass

@dataclass
class Store:
    name: str
    domain_key: str
    city_or_zip: str
    address: str
    category: str = "beef"
    expected_store_name: str = ""
