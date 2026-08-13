"""In-memory job registry and asyncio task runner for price searches.

Each search request becomes a Job. The job scrapes every configured
store (one shared Chromium browser, one page per store, concurrently),
caches per-store results, then fuzzy-matches the collected deals into
product rows mirroring ``meat_compare.compare`` decision logic.
"""

import asyncio
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from playwright.async_api import async_playwright

from api.cache import Cache, get_cache
from meat_compare.compare import _parse_price
from meat_compare.matcher import FUZZY_LOW, MatchedProduct, match_products_in_category
from meat_compare.models.MeatDeal import MeatDeal
from models.Product import Product

try:
    from meat_compare.inference import infer_category
except ImportError:
    infer_category = lambda query: None  # noqa: E731  (parallel agent lands this)
    infer_category.__doc__ = "Placeholder until meat_compare.inference lands."

try:
    from meat_compare.search import STORE_CONFIGS, scrape_store
except ImportError:
    STORE_CONFIGS: list[dict] = []
    async def scrape_store(store_config: dict, page, query: str, location: str) -> tuple[list[Product], str]:  # noqa: E704
        raise NotImplementedError("meat_compare.search is not available yet")

JOB_STATUSES = ("queued", "running", "done", "failed")
STORE_STATUSES = ("pending", "scraping", "cached", "done", "failed")

_MAX_CONCURRENT = int(os.environ.get("MAX_CONCURRENT_JOBS", "2"))
_JOB_TIMEOUT_SECONDS = int(os.environ.get("JOB_TIMEOUT_SECONDS", "300"))


@dataclass
class StoreStatus:
    """Scrape status for a single store within a job."""

    name: str
    status: str = "pending"
    product_count: int = 0
    error: str | None = None
    cached: bool = False
    address: str | None = None


@dataclass
class Job:
    """A single price-comparison search and its lifecycle state."""

    id: str
    query: str
    location: str
    status: str = "queued"
    created_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    generated_at: str | None = None
    inferred_category: str | None = None
    stores: list[StoreStatus] = field(default_factory=list)
    products: list[dict] = field(default_factory=list)
    scoreboard: dict = field(default_factory=lambda: {"wins": {}, "ties": 0})
    error: str | None = None
    cached: bool = False
    force_refresh: bool = False

    def to_dict(self) -> dict:
        """Serialize to the API contract shape."""
        return {
            "id": self.id,
            "status": self.status,
            "query": self.query,
            "location": self.location,
            "inferred_category": self.inferred_category,
            "generated_at": self.generated_at,
            "cached": self.cached,
            "error": self.error,
            "stores": [asdict(store) for store in self.stores],
            "scoreboard": self.scoreboard,
            "products": self.products,
        }


jobs: dict[str, Job] = {}
_semaphore: asyncio.Semaphore | None = None


def _get_semaphore() -> asyncio.Semaphore:
    """Return the job concurrency semaphore, created lazily."""
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(_MAX_CONCURRENT)
    return _semaphore


def _headless() -> bool:
    return os.environ.get("HEADLESS", "true").lower() == "true"


def create_job(query: str, location: str, force_refresh: bool = False) -> str:
    """Create (or dedupe) a search job and start its background task.

    Returns the job id. When an identical (query, location) job is
    already queued or running, its id is returned instead.
    """
    for existing in jobs.values():
        if (
            existing.query == query
            and existing.location == location
            and existing.status in {"queued", "running"}
        ):
            return existing.id

    job_id = uuid.uuid4().hex
    job = Job(
        id=job_id,
        query=query,
        location=location,
        stores=[StoreStatus(name=config["name"]) for config in STORE_CONFIGS],
        force_refresh=force_refresh,
    )
    jobs[job_id] = job
    asyncio.get_running_loop().create_task(_run_job(job_id))
    return job_id


def get_job(job_id: str) -> Job | None:
    """Return a job by id, or None when unknown."""
    return jobs.get(job_id)


async def _run_job(job_id: str) -> None:
    """Execute a job under the concurrency semaphore with a timeout."""
    job = jobs[job_id]
    job.status = "running"
    async with _get_semaphore():
        try:
            await asyncio.wait_for(_execute(job), timeout=_JOB_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            job.status = "failed"
            job.error = "Job timed out"
        except Exception as exc:
            job.status = "failed"
            job.error = f"Job failed: {exc}"
    job.finished_at = time.time()
    job.generated_at = datetime.now(timezone.utc).isoformat()


async def _execute(job: Job) -> None:
    """Scrape stores, build product rows, and finalize job status."""
    cache = await get_cache()

    store_products: dict[str, list[Product]] = {}
    to_scrape: list[StoreStatus] = []

    for store_status in job.stores:
        if not job.force_refresh:
            cached = await cache.get(job.query, job.location, store_status.name)
            if cached is not None:
                store_status.status = "cached"
                store_status.cached = True
                store_status.product_count = len(cached)
                store_products[store_status.name] = cached
                continue
        to_scrape.append(store_status)

    if to_scrape:
        await _scrape_stores(job, to_scrape, store_products, cache)

    job.inferred_category = _safe_infer(job.query)

    deals = [
        MeatDeal.from_product(product, store_name, job.inferred_category or "")
        for store_name, products in store_products.items()
        for product in products
    ]

    if deals:
        matched = match_products_in_category(deals, job.inferred_category or "")
        job.products, job.scoreboard = _build_products(matched, deals)
    else:
        job.products = []
        job.scoreboard = {"wins": {}, "ties": 0}

    failed = [store for store in job.stores if store.status == "failed"]
    if failed and len(failed) == len(job.stores):
        job.status = "failed"
        job.error = "All stores failed"
    else:
        job.status = "done"
        job.cached = bool(job.stores) and all(store.cached for store in job.stores)


async def _scrape_stores(
    job: Job,
    to_scrape: list[StoreStatus],
    store_products: dict[str, list[Product]],
    cache: Cache,
) -> None:
    """Scrape the stores that missed the cache using one shared browser."""
    configs = {config["name"]: config for config in STORE_CONFIGS}

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=_headless(),
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            context = await browser.new_context()
            pages = [await context.new_page() for _ in to_scrape]

            async def scrape_one(store_status: StoreStatus, page) -> None:
                store_status.status = "scraping"
                try:
                    products, address = await scrape_store(
                        configs[store_status.name], page, job.query, job.location
                    )
                    if products:
                        # Only cache non-empty scrapes; a flaky/empty scrape
                        # would otherwise poison the cache for its whole TTL.
                        await cache.put(job.query, job.location, store_status.name, products)
                    store_status.status = "done"
                    store_status.cached = False
                    store_status.product_count = len(products)
                    store_status.address = address or None
                    store_products[store_status.name] = products
                except Exception as exc:
                    store_status.status = "failed"
                    store_status.error = str(exc)

            await asyncio.gather(
                *(scrape_one(status, page) for status, page in zip(to_scrape, pages)),
                return_exceptions=True,
            )
        finally:
            await browser.close()


def _safe_infer(query: str) -> str | None:
    try:
        return infer_category(query)
    except Exception:
        return None


def _build_products(
    matched: list[MatchedProduct], deals: list[MeatDeal]
) -> tuple[list[dict], dict]:
    """Build the products JSON and scoreboard, mirroring compare.py logic.

    Fuzzy-low rows carry a "~ likely match" tag, a "~" winner, and are
    excluded from is_best/delta and the scoreboard. Rows found at a
    single store get a "{store} only" tag. Otherwise the winner is the
    single lowest-price store, or "Tie" when prices are equal.
    """
    store_names: list[str] = []
    for deal in deals:
        if deal.store_name not in store_names:
            store_names.append(deal.store_name)

    wins = {store: 0 for store in store_names}
    ties = 0
    rows: list[dict] = []

    for group in sorted(matched, key=lambda g: g.display_name.lower()):
        low_conf = group.confidence == FUZZY_LOW
        by_store = {deal.store_name: deal for deal in group.deals}

        parsed_prices = {
            store: price
            for store, price in (
                (store, _parse_price(deal.sale_price))
                for store, deal in by_store.items()
            )
            if price is not None
        }
        best_price = min(parsed_prices.values()) if parsed_prices else None

        winner: str | None = None
        if best_price is None:
            pass
        elif low_conf:
            winner = "~"
        else:
            winning_stores = {
                store
                for store, price in parsed_prices.items()
                if abs(price - best_price) < 0.005
            }
            if len(winning_stores) == 1:
                winner = next(iter(winning_stores))
                wins[winner] += 1
            else:
                winner = "Tie"
                ties += 1

        brands = " / ".join(
            dict.fromkeys(deal.brand for deal in group.deals if deal.brand)
        )

        present_stores = [store for store in store_names if store in by_store]
        only_store = (
            present_stores[0]
            if len(present_stores) == 1 and len(store_names) > 1
            else None
        )

        if low_conf:
            tag = "~ likely match"
        elif only_store:
            tag = f"{only_store} only"
        else:
            tag = ""

        prices: list[dict[str, Any]] = []
        for store in store_names:
            deal = by_store.get(store)
            if deal is None:
                continue
            price = parsed_prices.get(store)
            is_best = (
                not low_conf
                and price is not None
                and best_price is not None
                and abs(price - best_price) < 0.005
            )
            delta = None
            if (
                not low_conf
                and price is not None
                and best_price is not None
                and not is_best
            ):
                delta = round(price - best_price, 2)
            prices.append(
                {
                    "store": store,
                    "sale_price": deal.sale_price,
                    "parsed_price": price,
                    "original_price": deal.original_price,
                    "image_url": deal.image_url,
                    "is_best": is_best,
                    "delta": delta,
                }
            )

        rows.append(
            {
                "display_name": group.display_name,
                "brand": brands,
                "confidence": group.confidence,
                "tag": tag,
                "winner": winner,
                "only_store": only_store,
                "prices": prices,
            }
        )

    return rows, {"wins": wins, "ties": ties}
