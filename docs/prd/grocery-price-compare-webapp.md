# Product Requirements Document (PRD): Grocery Price Compare Webapp

**Last Updated:** 2026-08-11
**Version:** v1.0

## 1. Executive Summary & Objective

* **Goal:** A website where a user enters a location and a product, and sees a side-by-side comparison of that product's prices across FoodMaxx, Lucky, and Grocery Outlet — the store with the lowest price highlighted per product.
* **Core Value:** Replaces the manual step of checking multiple grocery websites for the same item. Extends the v1 CLI meat-comparison tool (`docs/prd/grocery-meat-compare.md`) from a category-scraping, HTML-file tool into an on-demand, any-product search backed by a live web UI.

## 2. Technical Context & Constraints

* **Tech Stack:** Python 3.11, FastAPI, Playwright (async), SQLite (`aiosqlite`), Vite + vanilla TypeScript, pytest.
* **Architecture Rules:**
  * Reuse the existing Page Object Model — page objects live in `groceries/pages/` and inherit `shared.BasePage` / `BasePagePlaywright`
  * Reuse existing page objects (`FoodMaxxSearch`, `LuckyMeat`, `GroceryOutletSearch`, address pages) with minimal modification; product search adds thin adapters on top
  * Reuse `Product` / `MeatDeal` data models and the `meat_compare` fuzzy matcher; search decision logic (matching, winner, delta, tags) stays in Python and is served as JSON
  * New code lives in `groceries/meat_compare/` (search core) and `groceries/webapp/` (backend + frontend)
  * Frontend is framework-free (Vite + vanilla TS, no runtime deps); TS renders JSON from the backend
  * No secrets: store access is anonymous (no login required)
* **Dependencies (added to root `requirements.txt`):** `fastapi`, `uvicorn`, `aiosqlite`, `httpx` (test client). Frontend dev deps: `typescript`, `vite`.
* **Store platforms (researched):**
  * FoodMaxx + Lucky share a Swiftly/Remix platform — search URL `{domain}/search/products?q={query}`, search results use the same `data-testid="product-card"` DOM as category pages; the data API is Firebase-gated, so a real browser is required
  * Grocery Outlet is a different platform (Instacart) — search URL `shop.groceryoutlet.com/store/grocery-outlet/s?k={query}`, store selection by full street address, store-local inventory, and ships anti-bot (DataDome-style) that may challenge headless Chromium

## 3. User Stories & Functional Requirements

* **Story 1:** As a user, I want to enter a location and a product name and get a side-by-side price comparison, so I can see which store has the cheapest price for that product.
  * *Acceptance Criteria:*
    * A search form accepts a free-text location ("ZIP or address") and a product query (e.g. "ground beef 80/20", "eggs")
    * The site searches each configured store for the product and returns a table: one row per matched product, one column per store
    * The lowest per-unit price per product is highlighted green with a checkmark; other stores show a "+$X.XX" delta and strikethrough original price where available
    * A winner badge per row ("Tie" for ties, "~" for low-confidence matches, store name otherwise) and a scoreboard counting wins/ties per store
    * Products found at a single store are tagged "{store} only"; low-confidence matches are tagged "~ likely match" and are not scored
    * Per-store scrape status is shown while the search runs ("FoodMaxx: scraping… 34 products"); a failed store is reported without failing the whole search
    * Empty results show a "No products found" state
  * *Technical Sub-tasks (implemented):*
    * `groceries/meat_compare/search.py` — `STORE_CONFIGS`, `scrape_store()`, `run_search()` store adapters
    * `groceries/meat_compare/inference.py` — `infer_category()` query→meat-category keyword inference
    * `groceries/meat_compare/matcher.py` — generic mode (falsy category skips meat-specific guards)
    * `groceries/webapp/api/{main,routes,jobs,cache,schemas}.py` — FastAPI app, job runner, SQLite cache
    * `groceries/webapp/ui/` — Vite + vanilla TS single page (form, polling, results table, scoreboard, Refresh)

* **Story 2:** As a user, I want to re-run a search without waiting for cache, so I can see fresh prices.
  * *Acceptance Criteria:*
    * Results include a "Refresh" button that re-scrapes every store (bypassing the cache) and re-renders on completion
    * Cached results are labeled ("Loaded from cache — Refresh to re-scrape")

* **Story 3:** As a user, I want the CLI to still work for quick headless checks, so I can debug scraping without the web stack.
  * *Acceptance Criteria:*
    * `groceries/meat_compare/meat_compare.py --zip <zip> --query "<product>"` runs the same search pipeline and prints `store | name | sale_price` per deal
    * The existing `--category` flow is unchanged

## 4. Edge Cases & Error Handling

* **Store site down / timeout / anti-bot challenge:** A per-store failure is captured (non-fatal); the job completes and the UI shows which store failed and why. The job fails entirely only if every store fails.
* **Empty location or query:** 422 validation on the API; the form disables submit until both fields are filled.
* **Unknown job id:** 404.
* **Duplicate in-flight request:** An identical (query, location) search that is already queued/running returns the existing job id (dedupe) instead of scraping twice.
* **No parseable price:** Rows without a parseable price show no winner; unmatched rows show as "only at X".
* **Job timeout / concurrency:** Each job is bounded by a timeout; concurrent scrapes are limited by a semaphore (default 2) to bound Chromium usage.
* **Cache staleness:** Cached per-store results expire after a TTL (default 24h); refresh bypasses the cache.
* **Headless anti-bot risk (Grocery Outlet):** mitigation is non-fatal failure + UI note; can gate GO off until solved.
* **Browser cleanup:** The browser is always closed in a `finally` block per job; the cache connection is closed on app shutdown.

## 5. Non-Goals & Out of Scope

* No authentication / multi-user support — personal single-user for v1 (public deployment is a future consideration; env-config and Docker are structured to anticipate it)
* No historical price tracking or price alerts
* No pagination of store search results — first page only for v1
* No scheduling/cron — searches are on-demand with caching
* No WebSocket/SSE progress streaming — polling for v1
* No new stores beyond FoodMaxx, Lucky, Grocery Outlet
* No browser e2e tests for the webapp — unit tests mock the scraper; existing Playwright scraper e2e tests remain unchanged
* No geocoding — the location string is passed through to each store's autocomplete as-is

## 6. Implementation Steps / Plan

### Phase 1: Search core
#### Task: Store search adapters (`meat_compare/search.py`)
- **Files:** `groceries/meat_compare/search.py`, `groceries/meat_compare/inference.py`, edit `groceries/meat_compare/matcher.py`, edit `groceries/pages/PlaywrightAddressPage.py`
- **What to do:** Add per-store async search callables (FoodMaxx/Lucky: goto `{domain}/search/products?q=`, set store by location, re-navigate for store-scoped results, scrape first page; Grocery Outlet: goto `shop.groceryoutlet.com/.../s?k=`, select address, scrape with search-box fallback). Add `infer_category()` keyword inference (longest-alias-wins so "ground turkey"→turkey). Add matcher generic mode (falsy category → normalize + `token_set_ratio` thresholds only). Make `searchAddress` fall back to the first autocomplete suggestion for free-text input.
- **Acceptance criteria:** `infer_category("ground turkey")=="turkey"`, `infer_category("eggs") is None`; generic mode pairs "12 count large eggs" vs "Large Eggs 12 ct"; meat mode still pairs "B/S Chicken Breast" vs "Boneless Chicken Breast"
- **Depends on:** none

### Phase 2: Backend API
#### Task: FastAPI app, job runner, cache
- **Files:** `groceries/webapp/api/{main,routes,jobs,cache,schemas}.py`, edit `requirements.txt`, `.gitignore`
- **What to do:** `POST /api/search` creates a job (dedupes identical in-flight requests); job runs in-process under an asyncio semaphore, checks the SQLite per-store cache (TTL), scrapes missing stores with one shared headless Chromium, then builds the products JSON + scoreboard mirroring the v1 `compare.py` decision logic. `GET /api/search/{id}` returns job status/JSON; `POST /api/search/{id}/refresh` forces a re-scrape. Mount `ui/dist` when present.
- **Acceptance criteria:** Job lifecycle queued→running→done; per-store failure non-fatal; cache hit marks stores "cached"; contract JSON shape matches the frontend
- **Depends on:** Phase 1 (search core)

### Phase 3: Frontend UI
#### Task: Vite + vanilla TS single page
- **Files:** `groceries/webapp/ui/` (package.json, tsconfig, vite.config.ts, index.html, `src/{main,api,render}.ts`, style.css)
- **What to do:** Location + product form; `POST /api/search` then poll every 2s until done/failed; render per-store status while running, then scoreboard + side-by-side table with best/delta/was/tags/brand/winner visuals adapted from the v1 renderer; Refresh button; cached note; empty/error states. Vite dev proxy `/api` → `:8000`; `tsc && vite build` for production assets.
- **Acceptance criteria:** `npm install && npm run build` clean under strict TS; all user data rendered via `textContent` (no untrusted `innerHTML`)
- **Depends on:** Phase 2 API contract

### Phase 4: Tests & Verification
#### Task: Unit tests + integration check
- **Files:** `groceries/webapp/tests/{conftest,test_inference,test_matcher_generic,test_cache,test_api}.py`
- **What to do:** Mock the Playwright browser and `scrape_store` so no browser/network is touched. Cover inference mapping, matcher generic mode, cache TTL/keys, and the API job lifecycle (202/dedupe/422/404/refresh/cache-hit/winner/tie). Verify server boot: `uvicorn --app-dir groceries/webapp api.main:app`, `/api/health`, and static UI serving.
- **Acceptance criteria:** `pytest groceries/webapp/tests -q` green (browser mocked, no live sites)
- **Depends on:** Phase 2, Phase 3

### Follow-up (not v1)
- Multi-stage Dockerfile (node build → Playwright base, `CMD uvicorn`) for the future public deployment
- Optional WebSocket/SSE progress streaming; search-result pagination; more stores
