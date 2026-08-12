"""Category inference for free-text search queries.

Maps a free-text query (e.g. "ground beef 80/20") to one of the meat
categories. Matching is purely keyword-based on tokenized, lowercased
query text; no fuzzy matching is applied here.
"""

import re

CATEGORIES = ["beef", "pork", "chicken", "turkey", "seafood"]

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "beef": [
        "beef", "ground", "hamburger", "steak", "tri-tip", "sirloin",
        "ribeye", "brisket", "roast", "flank", "skirt", "chuck",
        "oxtail", "short rib", "stew meat", "corned beef",
    ],
    "pork": [
        "pork", "bacon", "ham", "spareribs", "ribs", "pork chop",
        "pork shoulder", "pork butt", "pork belly", "pork loin",
        "pork tenderloin", "pork roast",
    ],
    "chicken": ["chicken", "poultry"],
    "turkey": ["turkey", "ground turkey"],
    "seafood": [
        "seafood", "salmon", "shrimp", "fish", "tilapia", "cod",
        "crab", "lobster", "tuna", "trout", "halibut", "scallops",
        "clams", "mussels", "oysters", "catfish", "swai",
    ],
}


def infer_category(query: str) -> str | None:
    """Infer a meat category from a free-text query.

    Lowercases the query and tokenizes on word boundaries. Longer, more
    specific keywords (e.g. "ground turkey") are checked before shorter
    ones (e.g. "ground"), so "ground turkey" resolves to turkey rather
    than beef. Equal-length keywords fall back to CATEGORIES order as a
    stable tiebreak. Returns None when no keyword matches.
    """
    tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
    if not tokens:
        return None

    keywords = [
        (category, keyword)
        for category in CATEGORIES
        for keyword in CATEGORY_KEYWORDS[category]
    ]
    for category, keyword in sorted(keywords, key=lambda ck: -len(ck[1])):
        keyword_tokens = re.findall(r"[a-z0-9]+", keyword)
        if keyword_tokens and all(t in tokens for t in keyword_tokens):
            return category
    return None
