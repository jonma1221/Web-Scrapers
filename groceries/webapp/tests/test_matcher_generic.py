"""Tests for generic vs meat-mode fuzzy product matching."""

from meat_compare.matcher import (
    FUZZY_HIGH,
    FUZZY_LOW,
    NO_MATCH,
    match_products_in_category,
)
from meat_compare.models.MeatDeal import MeatDeal


def _deal(store, name, price, category=""):
    return MeatDeal(
        brand="",
        name=name,
        sale_price=price,
        original_price=None,
        image_url="",
        store_name=store,
        category=category,
    )


def _stores_of(group):
    return {deal.store_name for deal in group.deals}


def test_generic_mode_pairs_egg_products_fuzzy_high():
    deals = [
        _deal("FoodMaxx", "12 count large eggs", "$2.49"),
        _deal("Lucky", "Large Eggs 12 ct", "$2.99"),
    ]
    matched = match_products_in_category(deals, "")
    assert len(matched) == 1, "generic mode should pair the egg products"
    group = matched[0]
    assert group.confidence == FUZZY_HIGH, group
    assert _stores_of(group) == {"FoodMaxx", "Lucky"}


def test_generic_mode_does_not_pair_unrelated_products():
    deals = [
        _deal("FoodMaxx", "Ground Beef 80/20", "$5.99"),
        _deal("Lucky", "Chicken Thighs", "$3.49"),
    ]
    matched = match_products_in_category(deals, "")
    assert len(matched) == 2, "unrelated products must stay on separate rows"
    assert all(group.confidence == NO_MATCH for group in matched)
    assert {next(iter(_stores_of(group))) for group in matched} == {"FoodMaxx", "Lucky"}


def test_meat_mode_chicken_pairs_breast_products_fuzzy_high():
    deals = [
        _deal("FoodMaxx", "B/S Chicken Breast", "$2.99", category="chicken"),
        _deal("Lucky", "Boneless Chicken Breast", "$3.49", category="chicken"),
    ]
    matched = match_products_in_category(deals, "chicken")
    assert len(matched) == 1, "chicken mode should pair the breast products"
    group = matched[0]
    assert group.confidence == FUZZY_HIGH, group
    assert _stores_of(group) == {"FoodMaxx", "Lucky"}


def test_meat_mode_beef_pairs_hamburger_ground_beef_at_least_low():
    deals = [
        _deal("FoodMaxx", "Hamburger", "$4.99", category="beef"),
        _deal("Lucky", "Ground Beef 80/20", "$5.49", category="beef"),
    ]
    matched = match_products_in_category(deals, "beef")
    assert len(matched) == 1, "beef mode should pair hamburger with ground beef"
    group = matched[0]
    assert group.confidence in (FUZZY_HIGH, FUZZY_LOW), group
    assert _stores_of(group) == {"FoodMaxx", "Lucky"}


def test_meat_mode_ratio_conflict_is_no_match():
    deals = [
        _deal("FoodMaxx", "Ground Beef 80/20", "$5.99", category="beef"),
        _deal("Lucky", "Ground Beef 93/7", "$6.49", category="beef"),
    ]
    matched = match_products_in_category(deals, "beef")
    assert len(matched) == 2, "conflicting fat ratios must not pair in meat mode"
    assert all(group.confidence == NO_MATCH for group in matched)
    assert {next(iter(_stores_of(group))) for group in matched} == {"FoodMaxx", "Lucky"}


def test_generic_mode_ignores_ratio_conflict():
    deals = [
        _deal("FoodMaxx", "Ground Beef 80/20", "$5.99"),
        _deal("Lucky", "Ground Beef 93/7", "$6.49"),
    ]
    matched = match_products_in_category(deals, "")
    assert len(matched) == 1, "generic mode skips the ratio guard"
    assert matched[0].confidence == FUZZY_LOW, matched[0]
