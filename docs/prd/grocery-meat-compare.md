# Product Requirements Document (PRD): Grocery Meat Price Compare

**Last Updated:** 2026-07-13
**Version:** v1.0

## 1. Executive Summary & Objective

* **Goal:** Selenium-based scraper that fetches meat deals from FoodMaxx and Lucky, compares prices grouped by meat category, and generates an HTML page with the lowest price highlighted per category.
* **Core Value:** Eliminates manually checking multiple grocery websites to find the cheapest meat — saves time and money.

## 2. Technical Context & Constraints

* **Tech Stack:** Python 3.11, Selenium 4, HTML/CSS output (no new dependencies)
* **Architecture Rules:**
  * Follow existing Page Object Model pattern — page objects inherit `shared.BasePage`
  * Reuse existing `LuckyMeat.py`, `FoodMaxxSearch.py`, `FoodMaxxAddress.py` page objects (minimal modifications)
  * Reuse existing `Product.py` data model (wrap with new `MeatDeal` model)
  * New code lives in `groceries/meat_compare/` subpackage with its own entrypoint
* **Dependencies:** Existing `selenium` + `beautifulsoup4` only — no new pip installs

## 3. User Stories & Functional Requirements

* **Story 1:** As a user, I want to compare meat prices across FoodMaxx and Lucky grouped by category, so I can see which store has the best deal on each type of meat.
  * *Acceptance Criteria:*
    * Script fetches meat deals from both FoodMaxx and Lucky for a given ZIP code
    * Results are grouped by meat category (beef, pork, chicken, turkey, seafood)
    * Within each category, products from both stores are displayed with store name, product name, brand, sale price, and original price
    * The lowest price per product across both stores is highlighted (green row + star)
    * Output is an HTML file viewable in any browser
    * Script accepts ZIP code and optional meat category via CLI args
  * *Technical Sub-tasks:*
    * Create `groceries/meat_compare/__init__.py` (empty)
    * Create `groceries/meat_compare/models/__init__.py` (empty)
    * Create `groceries/meat_compare/pages/__init__.py` (empty)
    * Create `groceries/meat_compare/models/MeatDeal.py` (dataclass wrapping Product)
    * Create `groceries/meat_compare/category_urls.py` (URL mapping dict)
    * Create `groceries/meat_compare/compare.py` (HTML renderer)
    * Create `groceries/meat_compare/meat_compare.py` (entrypoint with argparse)
    * Modify `groceries/pages/LuckyMeat.py:58` (parameterize ZIP code)
    * Clean up `groceries/pages/LuckyMeat.py:31-33` (remove debug file write)

* **Story 2:** As a user, I want to filter results to a specific meat category (beef, pork, chicken, turkey, or seafood), so I can focus on what I'm buying today.
  * *Acceptance Criteria:*
    * CLI accepts `--category` / `-c` flag with valid choices: `beef`, `pork`, `chicken`, `turkey`, `seafood`
    * When specified, only that category is fetched and displayed
    * When omitted, all categories are fetched (default behavior)

## 4. Edge Cases & Error Handling

* **Network/timeout errors:** If a store site is down or times out, print a warning for that store and continue with the other. Use `try/except` around each store's scrape block.
* **Empty results:** If no deals are found for a category at a store, display "No deals found" row in that category's table. Skip entirely-empty categories.
* **Store not found for ZIP:** If the ZIP doesn't resolve to a store location, print a clear error and exit with non-zero status.
* **Price parsing failures:** Skip the malformed product with a warning (matching existing `try/except Exception: continue` pattern in `FoodMaxxSearch.scrapeDeals()`).
* **Both stores fail:** Print descriptive error message, exit non-zero.
* **Driver cleanup:** Always call `driver.quit()` in a `finally` block.

## 5. Non-Goals & Out of Scope

* No historical price tracking or database
* No web UI or API — HTML file output only
* No mobile support — CLI tool
* No Safeway or other stores — FoodMaxx and Lucky only for v1
* No automated tests — manual testing only (matches existing codebase)
* No price alerts or notifications

## 6. Implementation Steps / Plan

### Phase 1: Setup

#### Task: Create package structure
- **Files:** `groceries/meat_compare/__init__.py`, `groceries/meat_compare/models/__init__.py`, `groceries/meat_compare/pages/__init__.py`
- **What to do:** Create directories and empty `__init__.py` files
- **Acceptance criteria:** `groceries/meat_compare/` exists with proper package structure
- **Depends on:** none

#### Task: Create MeatDeal data model
- **Files:** `groceries/meat_compare/models/MeatDeal.py`
- **What to do:** Create `@dataclass` with fields from `Product` (`brand`, `name`, `sale_price`, `original_price`, `image_url`) plus `store_name: str` and `category: str`. Add `@classmethod from_product(cls, product, store_name, category)`.
- **Acceptance criteria:** `MeatDeal.from_product(product, "FoodMaxx", "beef")` returns a populated `MeatDeal` instance
- **Depends on:** none

#### Task: Create category URL mapping
- **Files:** `groceries/meat_compare/category_urls.py`
- **What to do:** Define dict mapping category names to URL path segments. Both stores use the same URL pattern: `https://{domain}/categories/Product%2Fmeat_seafood/Product%2F{category}`. Domains: `foodmaxx.com`, `luckysupermarkets.com`. Categories: beef, pork, chicken, turkey, seafood.
- **Acceptance criteria:** `CATEGORY_URLS["foodmaxx.com"]["beef"]` returns the correct URL
- **Depends on:** none

### Phase 2: Core Logic

#### Task: Parameterize LuckyMeat.selectAStore()
- **Files:** `groceries/pages/LuckyMeat.py`
- **What to do:** Change `selectAStore(self)` to `selectAStore(self, zip_code)`. Replace hardcoded `"94506"` on line 58 with `zip_code` parameter. Update `addressInput.send_keys("94506")` → `addressInput.send_keys(zip_code)`.
- **Acceptance criteria:** `luckyMeat.selectAStore("94105")` sets the store for ZIP 94105
- **Depends on:** none

#### Task: Clean up LuckyMeat.scrapeDeals() debug write
- **Files:** `groceries/pages/LuckyMeat.py`
- **What to do:** Remove or comment out lines 31-33 (the `deals.html` file write block) from `scrapeDeals()`
- **Acceptance criteria:** `scrapeDeals()` no longer writes `deals.html`
- **Depends on:** none

#### Task: Build HTML comparison renderer
- **Files:** `groceries/meat_compare/compare.py`
- **What to do:** Create function `generate_html(meat_deals: list[MeatDeal], zip_code: str) -> str` that:
  1. Groups deals by `category`
  2. For each category group, finds the lowest `sale_price` per product
  3. Renders an HTML string with inline CSS matching the example at `docs/example-meat-deals.html`
  4. Highlights lowest-price rows with `class="best"` (green bg + star)
  5. Shows "No deals found" for empty categories
  6. Includes ZIP code and generation date in subtitle
- **Acceptance criteria:** Returns a valid HTML string that looks like the example file when opened in a browser
- **Depends on:** MeatDeal model

### Phase 3: Integration

#### Task: Create CLI entrypoint
- **Files:** `groceries/meat_compare/meat_compare.py`
- **What to do:**
  1. Add `sys.path.insert` for parent directory (matching `groceries/compare-groceries-deals.py` pattern)
  2. `argparse` with `--zip` (required) and `--category` / `-c` (optional, choices: beef, pork, chicken, turkey, seafood)
  3. For each store (FoodMaxx, Lucky): init Chrome driver → navigate to URL from category mapping → accept cookies → set store via ZIP → scrape deals → wrap each `Product` in `MeatDeal` with store name + category
  4. Collect all `MeatDeal` objects, call `generate_html()`, write output to `groceries/meat_compare/meat-deals.html`
  5. Open the HTML file in the default browser
  6. Wrap in `try/finally` for `driver.quit()`
  7. Handle errors per §4 (per-store try/except, clear error messages)
- **Acceptance criteria:** `python groceries/meat_compare/meat_compare.py --zip 94506 --category beef` generates and opens `meat-deals.html` with FoodMaxx and Lucky beef deals
- **Depends on:** all previous tasks

#### Task: Manual end-to-end verification
- **Files:** none
- **What to do:** Run the script with: (1) `--zip 94506` for all categories, (2) `--zip 94506 --category pork` for single category, (3) `--zip 00000` for invalid ZIP. Verify HTML output is correct and error handling works.
- **Acceptance criteria:** All three scenarios produce expected output with no crashes
- **Depends on:** all previous tasks
