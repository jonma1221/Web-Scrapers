"""Async SQLite cache for per-store scrape results.

Stores JSON-serialized ``Product`` lists keyed by a hash of the
query, location, and store name. Entries expire after a TTL.
"""

import hashlib
import json
import os
import time
from dataclasses import asdict
from pathlib import Path

import aiosqlite

from models.Product import Product

DEFAULT_DB_PATH = Path(__file__).parent.parent / "cache.db"


class Cache:
    """Thin async wrapper around a SQLite table of cached products."""

    def __init__(self, db_path: str, ttl_hours: int = 24):
        self._db_path = db_path
        self._ttl_seconds = ttl_hours * 3600
        self._conn: aiosqlite.Connection | None = None

    async def open(self) -> None:
        """Open the connection and ensure the schema exists (WAL mode)."""
        self._conn = await aiosqlite.connect(self._db_path)
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS cache ("
            "key TEXT PRIMARY KEY, "
            "products TEXT, "
            "fetched_at REAL)"
        )
        await self._conn.commit()

    async def close(self) -> None:
        """Close the underlying connection."""
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def get(self, query: str, location: str, store_name: str) -> list[Product] | None:
        """Return cached products, or None when missing or stale per TTL."""
        key = self._key(query, location, store_name)
        cursor = await self._conn.execute(
            "SELECT products, fetched_at FROM cache WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            return None
        products_json, fetched_at = row
        if time.time() - fetched_at > self._ttl_seconds:
            return None
        data = json.loads(products_json)
        return [Product(**item) for item in data]

    async def put(self, query: str, location: str, store_name: str, products: list[Product]) -> None:
        """Store (or overwrite) the product list for a store."""
        key = self._key(query, location, store_name)
        products_json = json.dumps([asdict(product) for product in products])
        await self._conn.execute(
            "INSERT INTO cache (key, products, fetched_at) VALUES (?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET "
            "products = excluded.products, fetched_at = excluded.fetched_at",
            (key, products_json, time.time()),
        )
        await self._conn.commit()

    @staticmethod
    def _key(query: str, location: str, store_name: str) -> str:
        raw = f"{query}|{location}|{store_name}"
        return hashlib.sha256(raw.encode()).hexdigest()


_cache: Cache | None = None


async def get_cache() -> Cache:
    """Return the module-level Cache singleton, opening it on first use."""
    global _cache
    if _cache is None:
        db_path = os.environ.get("CACHE_DB_PATH", str(DEFAULT_DB_PATH))
        ttl_hours = int(os.environ.get("CACHE_TTL_HOURS", "24"))
        _cache = Cache(db_path, ttl_hours)
        await _cache.open()
    return _cache
