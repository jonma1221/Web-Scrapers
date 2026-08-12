"""Shared fixtures for the grocery webapp test suite.

Inserts the repo root, groceries, and webapp directories onto sys.path
(mirroring ``groceries/tests/conftest.py``) so the tests can import the
API and its dependencies. The job pipeline in ``api.jobs`` is fully
mocked: a fake Playwright context manager stands in for a real Chromium
launch and a fake ``scrape_store`` replaces the network-bound scrapers,
so no test ever touches a browser or the network.
"""

import asyncio
import sys
import threading
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
GROCERIES_DIR = REPO_ROOT / "groceries"
WEBAPP_DIR = GROCERIES_DIR / "webapp"

for _path in (str(WEBAPP_DIR), str(GROCERIES_DIR), str(REPO_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from api.cache import Cache  # noqa: E402
from models.Product import Product  # noqa: E402


class _FakePage:
    """Dummy page; the mocked scrape_store never inspects it."""


class _FakeContext:
    async def new_page(self):
        return _FakePage()


class _FakeBrowser:
    async def new_context(self):
        return _FakeContext()

    async def close(self):
        return None


class _FakeChromium:
    async def launch(self, **kwargs):
        return _FakeBrowser()


class _FakePlaywright:
    """Async context manager masquerading as ``async_playwright()``."""

    def __init__(self):
        self.chromium = _FakeChromium()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return None


class MockSearchPipeline:
    """Replacement for ``api.jobs.scrape_store`` with an optional gate.

    ``gate`` is a ``threading.Event``: when provided, every scrape blocks
    (in a worker thread) until the test releases it, letting a test hold
    a job in the "running" state while exercising dedupe logic.
    """

    def __init__(self, products_by_store=None, failures=(), gate=None):
        self.products_by_store = dict(products_by_store or {})
        self.failures = set(failures)
        self.gate = gate

    def playwright_factory(self):
        return _FakePlaywright()

    async def scrape_store(self, store_config, page, query, location):
        if self.gate is not None:
            await asyncio.to_thread(self.gate.wait)
        store_name = store_config["name"]
        if store_name in self.failures:
            raise RuntimeError(f"scrape failed for {store_name}")
        return list(self.products_by_store.get(store_name, []))


@pytest.fixture
def make_product():
    """Factory for building ``models.Product`` fixtures quickly."""

    def _make(brand, name, sale_price, original=None, image=""):
        return Product(
            brand=brand,
            name=name,
            sale_price=sale_price,
            original_price=original,
            image_url=image,
        )

    return _make


@pytest.fixture
def mock_pipeline(monkeypatch, tmp_path, make_product):
    """Patch ``api.jobs`` so jobs run without a browser or the network."""
    pipeline = MockSearchPipeline(
        products_by_store={
            "FoodMaxx": [make_product("FoodMaxx", "Large Eggs 12 ct", "$2.49")],
            "Lucky": [make_product("Lucky", "12 count large eggs", "$2.99")],
        },
        failures={"Grocery Outlet"},
    )
    monkeypatch.setattr("api.jobs.async_playwright", pipeline.playwright_factory)
    monkeypatch.setattr("api.jobs.scrape_store", pipeline.scrape_store)

    # Isolate each test behind a fresh Cache on a temp path (never the
    # real webapp/cache.db), opened lazily in the app's event loop.
    cache = Cache(str(tmp_path / "job-cache.db"), ttl_hours=24)

    async def _get_cache():
        if cache._conn is None:
            await cache.open()
        return cache

    monkeypatch.setattr("api.jobs.get_cache", _get_cache)

    # The module-level semaphore caches the event loop that first used it.
    # Reset it per test so each TestClient portal can re-create it safely.
    monkeypatch.setattr("api.jobs._semaphore", None)
    return pipeline


@pytest.fixture
def client(monkeypatch, tmp_path):
    """A TestClient whose shutdown hook never touches the real cache.db."""
    from api.main import app

    shutdown_cache = Cache(str(tmp_path / "shutdown-cache.db"), ttl_hours=24)

    async def _get_cache():
        if shutdown_cache._conn is None:
            await shutdown_cache.open()
        return shutdown_cache

    monkeypatch.setattr("api.main.get_cache", _get_cache)

    with TestClient(app) as test_client:
        yield test_client
