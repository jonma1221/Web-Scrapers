"""Table-driven tests for free-text category inference."""

import pytest

from meat_compare.inference import CATEGORIES, CATEGORY_KEYWORDS, infer_category

# (query, expected category). None means no meat category matches.
_CASES = [
    ("ground turkey", "turkey"),
    ("ground beef 80/20", "beef"),
    ("ground", "beef"),
    ("eggs", None),
    ("salmon fillets", "seafood"),
    ("chicken breast", "chicken"),
    ("ham", "pork"),
    ("GROUND TURKEY", "turkey"),
    ("", None),
    ("   ", None),
    ("12 pack sparkling water", None),
]


@pytest.mark.parametrize("query,expected", _CASES)
def test_infer_category(query, expected):
    assert infer_category(query) == expected, f"infer_category({query!r})"


def test_category_metadata_is_consistent():
    assert CATEGORIES == ["beef", "pork", "chicken", "turkey", "seafood"]
    assert set(CATEGORY_KEYWORDS) == set(CATEGORIES)
    for category, keywords in CATEGORY_KEYWORDS.items():
        assert keywords, f"category {category!r} has no keywords"
