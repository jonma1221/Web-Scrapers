# Web Scrapers

Python 3.11 Selenium + BeautifulSoup scrapers.

## Venv

- `.venv/` — activate with `source .venv/bin/activate`
- No requirements.txt or pyproject.toml. Install new deps with `.venv/bin/pip install <pkg>`.

## Entrypoints

| Script | What it scrapes |
|---|---|
| `slickdeals/deal-scraper.py` | Slickdeals.net video game deals |
| `groceries/compare-groceries-deals.py` | Safeway weekly ad |

Run from repo root: `python3 slickdeals/deal-scraper.py`

## Known quirks

- **`groceries/compare-groceries-deals.py`** adds repo root to `sys.path` at import time. **`slickdeals/deal-scraper.py` does not** — it must be run from repo root (`.venv/bin/python` or `python3` from `/Users/jon/Projects/web-scrapers`) so that `from shared.BasePage import BasePage` resolves.
- Selenium 4 uses its built-in Selenium Manager — no manual ChromeDriver install.
- Error dumps write `error_dump.html` to CWD (gitignored).
- Page Object Model: pages inherit `shared.BasePage` which provides `self.driver` and `self.wait` (10s default).
- No linter, formatter, or typecheck config.
- `pytest` is installed but no tests exist yet.
- Git repo has no commits.
