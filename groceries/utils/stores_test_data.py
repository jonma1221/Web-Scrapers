from models.Store import Store


STORES = [
    Store(
        name="Lucky",
        domain_key="luckysupermarkets.com",
        city_or_zip="San Leandro",
        address="FAIRMONT DR",
    ),
    Store(
        name="FoodMaxx",
        domain_key="foodmaxx.com",
        city_or_zip="San Leandro",
        address="San Leandro",
        expected_store_name="CONCORD",
    ),
]
