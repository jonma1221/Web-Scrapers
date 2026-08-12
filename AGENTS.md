# Web Scrapers

Python 3.11 Selenium + BeautifulSoup scrapers.

## Venv

- `.venv/` — activate with `source .venv/bin/activate`
- Install new deps with `.venv/bin/pip install <pkg>` and pin them in root `requirements.txt`.

## Entrypoints

| Script | What it scrapes |
|---|---|
| `slickdeals/deal-scraper.py` | Slickdeals.net video game deals |
| `groceries/compare-groceries-deals.py` | Safeway weekly ad |
| `groceries/meat_compare/meat_compare.py` | Meat price compare CLI (FoodMaxx/Lucky/Grocery Outlet) — `--zip` category flow, or `--query "ground beef"` product search |
| `groceries/webapp/` | FastAPI + Vite/TS website: search a product + location, get per-store prices |

Run from repo root: `python3 slickdeals/deal-scraper.py`

## Known quirks

- **`groceries/compare-groceries-deals.py`** adds repo root to `sys.path` at import time. **`slickdeals/deal-scraper.py` does not** — it must be run from repo root (`.venv/bin/python` or `python3` from `/Users/jon/Projects/web-scrapers`) so that `from shared.BasePage import BasePage` resolves.
- Selenium 4 uses its built-in Selenium Manager — no manual ChromeDriver install.
- Error dumps write `error_dump.html` to CWD (gitignored).
- Page Object Model: pages inherit `shared.BasePage` which provides `self.driver` and `self.wait` (10s default).
- No linter, formatter, or typecheck config (frontend `ui/` has `tsc` via `npm run build`).
- `groceries/webapp/` (FastAPI): backend in `webapp/api/` (`main.py`, `routes.py`, `jobs.py`, `cache.py`), frontend in `webapp/ui/` (Vite + vanilla TS, build with `npm run build`).
  - Run the server: `.venv/bin/uvicorn --app-dir groceries/webapp api.main:app` (serve the frontend, run `npm run build` in `ui/` first; dev uses `npm run dev` with `/api` proxied to `:8000`).
  - Env config: `HEADLESS` (default true), `MAX_CONCURRENT_JOBS` (2), `CACHE_TTL_HOURS` (24), `CACHE_DB_PATH` (default `groceries/webapp/cache.db`, gitignored).
  - Search core: `groceries/meat_compare/search.py` (store adapters) + `inference.py` (query→meat-category). Matcher supports a generic mode when category is empty.
  - Grocery Outlet is a different platform (Instacart) from FoodMaxx/Lucky (Swiftly/Remix) and may challenge headless Chromium.
- `pytest` installed; unit tests for the webapp live in `groceries/webapp/tests/` (browser mocked, no live sites). Existing Playwright e2e tests in `groceries/tests/` hit real sites.
