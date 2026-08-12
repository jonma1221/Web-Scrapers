"""Tests for the async SQLite cache layer."""

from dataclasses import asdict

import pytest

from api.cache import Cache
from models.Product import Product

pytestmark = pytest.mark.asyncio


def _products():
    return [
        Product(
            brand="FoodMaxx",
            name="Ground Beef 80/20",
            sale_price="$5.99",
            original_price="$7.99",
            image_url="http://img/foodmaxx.jpg",
        ),
        Product(
            brand="",
            name="Chicken Thighs",
            sale_price="$3.49",
            original_price=None,
            image_url="",
        ),
    ]


async def test_put_get_roundtrip_returns_equivalent_products(tmp_path):
    cache = Cache(str(tmp_path / "cache.db"), ttl_hours=24)
    await cache.open()
    try:
        products = _products()
        await cache.put("ground beef", "94110", "FoodMaxx", products)

        result = await cache.get("ground beef", "94110", "FoodMaxx")
        assert result is not None, "get() should return products after put()"
        assert [asdict(p) for p in result] == [asdict(p) for p in products]
        assert result[0].brand == "FoodMaxx"
        assert result[0].original_price == "$7.99"
        assert result[1].original_price is None
    finally:
        await cache.close()


async def test_get_returns_none_for_unknown_key(tmp_path):
    cache = Cache(str(tmp_path / "cache.db"), ttl_hours=24)
    await cache.open()
    try:
        assert await cache.get("ground beef", "94110", "FoodMaxx") is None

        await cache.put("ground beef", "94110", "FoodMaxx", _products())
        assert await cache.get("ground beef", "94110", "FoodMaxx") is not None
        assert (
            await cache.get("ground beef", "94110", "Lucky") is None
        ), "another store for the same query/location must not collide"
        assert (
            await cache.get("ground beef", "95050", "FoodMaxx") is None
        ), "another location for the same query/store must not collide"
    finally:
        await cache.close()


async def test_keys_differ_across_stores(tmp_path):
    cache = Cache(str(tmp_path / "cache.db"), ttl_hours=24)
    await cache.open()
    try:
        await cache.put("ground beef", "94110", "FoodMaxx", _products())
        await cache.put("ground beef", "94110", "Lucky", _products())

        assert await cache.get("ground beef", "94110", "FoodMaxx") is not None
        assert await cache.get("ground beef", "94110", "Lucky") is not None
        assert cache._key("ground beef", "94110", "FoodMaxx") != cache._key(
            "ground beef", "94110", "Lucky"
        )
    finally:
        await cache.close()


async def test_get_returns_none_after_ttl_expiry(tmp_path, monkeypatch):
    cache = Cache(str(tmp_path / "cache.db"), ttl_hours=24)
    fake_now = {"t": 1_000_000.0}
    monkeypatch.setattr("api.cache.time.time", lambda: fake_now["t"])
    await cache.open()
    try:
        await cache.put("ground beef", "94110", "FoodMaxx", _products())

        fresh = await cache.get("ground beef", "94110", "FoodMaxx")
        assert fresh is not None, "entry should be valid before the TTL elapses"

        fake_now["t"] += 24 * 3600 + 1
        stale = await cache.get("ground beef", "94110", "FoodMaxx")
        assert stale is None, "entry should expire after the TTL elapses"
    finally:
        await cache.close()
