_CATEGORIES = ["beef", "pork", "chicken", "turkey", "seafood"]

_DOMAINS = {
    "foodmaxx.com": "foodmaxx.com",
    "lucky": "luckysupermarkets.com",
}

CATEGORY_URLS = {
    domain: {
        cat: f"https://{domain}/categories/Product%2Fmeat_seafood/Product%2F{cat}"
        for cat in _CATEGORIES
    }
    for domain in _DOMAINS.values()
}
