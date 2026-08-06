"""HTML comparison renderer for meat deals across stores.

Generates a side-by-side table per meat category: each product is a row,
each store is a column, and the lowest price per product is highlighted.
"""

import re
from collections import defaultdict
from datetime import date
from html import escape

from meat_compare.models.MeatDeal import MeatDeal

# Fixed display order for categories
CATEGORY_ORDER = ["beef", "pork", "chicken", "turkey", "seafood"]

# Category display names (title case for headings)
CATEGORY_DISPLAY = {
    "beef": "Beef",
    "pork": "Pork",
    "chicken": "Chicken",
    "turkey": "Turkey",
    "seafood": "Seafood",
}

# Store badge/dot colors, cycled in store order
STORE_COLORS = ["#e67e22", "#2d6da3", "#2d8a2d", "#8e44ad", "#c0392b"]


def _parse_price(price_str: str) -> float | None:
    """Extract the per-unit numeric price from a price string.

    Handles formats like:
      - "$4.99"         -> 4.99
      - "2 for $5.00"   -> 2.50  (per unit)
      - "$10/ea"        -> 10.00
      - "BOGO"          -> None  (unparseable)
    """
    price_str = price_str.strip()

    match = re.search(r"(\d+)\s+for\s+\$(\d+(?:\.\d{1,2})?)", price_str, re.IGNORECASE)
    if match:
        qty = int(match.group(1))
        total = float(match.group(2))
        return total / qty if qty > 0 else None

    match = re.search(r"\$(\d+(?:\.\d{1,2})?)", price_str)
    if match:
        return float(match.group(1))

    return None


def _store_css(stores: list[str]) -> str:
    """Generate CSS rules for store-specific badges and dots."""
    rules = []
    for i, store in enumerate(stores):
        slug = store.lower().replace(" ", "-")
        color = STORE_COLORS[i % len(STORE_COLORS)]
        rules.append(f"""
    .badge.{slug} {{ background: {color}; }}
    .dot.{slug} {{ background: {color}; }}""")
    return "\n".join(rules)


def generate_html(meat_deals: list[MeatDeal], zip_code: str) -> str:
    """Generate an HTML comparison page for meat deals.

    Groups deals by category, then by product name (case-insensitive).
    Each product becomes a row with one price column per store. The
    lowest price per product is highlighted and a winner badge is shown.

    Args:
        meat_deals: List of MeatDeal objects to display.
        zip_code: The ZIP code used for the store search (shown in subtitle).

    Returns:
        A complete HTML string with inline CSS and side-by-side tables.
    """
    today = date.today().strftime("%B %d, %Y")
    esc_zip = escape(zip_code)

    # Distinct stores in order of first appearance
    stores: list[str] = []
    for deal in meat_deals:
        if deal.store_name not in stores:
            stores.append(deal.store_name)

    # Group deals by category
    deals_by_category: dict[str, list[MeatDeal]] = defaultdict(list)
    for deal in meat_deals:
        deals_by_category[deal.category.lower()].append(deal)

    global_wins = {store: 0 for store in stores}
    global_ties = 0

    # Build HTML sections for each category
    category_sections: list[str] = []
    for cat in CATEGORY_ORDER:
        display_name = CATEGORY_DISPLAY.get(cat, cat.title())
        deals = deals_by_category.get(cat, [])

        if not deals:
            category_sections.append(
                f"""
        <div class="category">
          <h2>{escape(display_name)}</h2>
          <table>
            <thead>
              <tr>
                <th>Product</th>
                {' '.join(f'<th class="store-col">{escape(s)}</th>' for s in stores)}
                <th>Winner</th>
              </tr>
            </thead>
            <tbody>
              <tr class="empty"><td colspan="{len(stores) + 2}">No deals found</td></tr>
            </tbody>
          </table>
        </div>"""
            )
            continue

        # Group products by normalized name
        products: dict[str, list[MeatDeal]] = defaultdict(list)
        for deal in deals:
            products[deal.name.strip().lower()].append(deal)

        rows: list[str] = []
        for key in sorted(products.keys()):
            product_deals = products[key]

            # Store name -> deal for this product
            by_store = {deal.store_name: deal for deal in product_deals}

            # Best (lowest per-unit) price among parseable deals
            parsed_prices = {
                deal.store_name: price
                for deal in product_deals
                if (price := _parse_price(deal.sale_price)) is not None
            }
            best_price = min(parsed_prices.values()) if parsed_prices else None

            # Winner determination
            if best_price is None:
                winner: str | None = None
            else:
                winning_stores = {
                    store
                    for store, price in parsed_prices.items()
                    if abs(price - best_price) < 0.005
                }
                if len(winning_stores) == 1:
                    winner = winning_stores.pop()
                    global_wins[winner] += 1
                else:
                    winner = "tie"
                    global_ties += 1

            # Brand line (distinct, non-empty brands joined)
            brands = [deal.brand for deal in product_deals if deal.brand]
            brand_html = escape(" / ".join(dict.fromkeys(brands)))

            # Only-at-one-store tag
            present_stores = [s for s in stores if s in by_store]
            only_store = present_stores[0] if len(present_stores) == 1 and len(stores) > 1 else None
            tag_html = (
                f"<span class='tag'>{escape(only_store)} only</span>"
                if only_store
                else ""
            )

            # Store price cells
            cells: list[str] = []
            for store in stores:
                deal = by_store.get(store)
                if deal is None:
                    cells.append(f"<td class='price missing'>&mdash;</td>")
                    continue

                price = parsed_prices.get(store)
                is_best = (
                    price is not None
                    and best_price is not None
                    and abs(price - best_price) < 0.005
                )

                sublabels = []
                if deal.original_price:
                    sublabels.append(
                        f"<span class='was'>was {escape(deal.original_price)}</span>"
                    )
                if price is not None and best_price is not None and not is_best:
                    sublabels.append(f"<span class='delta'>+${price - best_price:.2f}</span>")
                if is_best:
                    sublabels.append("<span class='best-note'>&#10003; best</span>")

                sub_html = "".join(sublabels)
                cell_class = "price best" if is_best else "price"
                cells.append(
                    f"<td class='{cell_class}'>"
                    f"{escape(deal.sale_price)}{sub_html}</td>"
                )

            # Winner badge
            if winner == "tie":
                badge_html = "<span class='badge tie'>Tie</span>"
            elif winner:
                slug = winner.lower().replace(" ", "-")
                badge_html = f"<span class='badge {slug}'>{escape(winner)}</span>"
            else:
                badge_html = "&mdash;"

            row_class = "only" if only_store else ""
            product_name_html = escape(product_deals[0].name)
            if brand_html:
                product_name_html += f"<span class='brand'>{brand_html}</span>"
            product_name_html += tag_html
            rows.append(
                f'            <tr class="{row_class}">'
                f"<td class='product'>{product_name_html}</td>"
                f"{''.join(cells)}"
                f"<td class='winner'>{badge_html}</td>"
                f"</tr>"
            )

        rows_html = "\n".join(rows)

        category_sections.append(
            f"""
        <div class="category">
          <h2>{escape(display_name)}</h2>
          <table>
            <thead>
              <tr>
                <th>Product</th>
                {' '.join(f'<th class="store-col">{escape(s)}</th>' for s in stores)}
                <th>Winner</th>
              </tr>
            </thead>
            <tbody>
{rows_html}
            </tbody>
          </table>
        </div>"""
        )

    sections_html = "\n".join(category_sections)

    # Scoreboard chips
    scoreboard_html = "".join(
        f"""
      <div class="score-chip"><span class="dot {store.lower().replace(' ', '-')}"></span> {escape(store)} wins <strong>{global_wins[store]}</strong></div>"""
        for store in stores
    )
    scoreboard_html += f"""
      <div class="score-chip">Ties <strong>{global_ties}</strong></div>"""

    store_css = _store_css(stores)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Meat Price Comparison</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      max-width: 900px;
      margin: 0 auto;
      padding: 20px;
      background: #f5f5f5;
      color: #333;
    }}
    h1 {{
      text-align: center;
      margin-bottom: 4px;
    }}
    .subtitle {{
      text-align: center;
      color: #666;
      margin-top: 0;
      margin-bottom: 24px;
      font-size: 0.95em;
    }}
    .scoreboard {{
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      flex-wrap: wrap;
      justify-content: center;
    }}
    .score-chip {{
      background: #fff;
      border-radius: 8px;
      padding: 10px 16px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      font-size: 0.9em;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .score-chip .dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      display: inline-block;
    }}
    .category {{
      background: #fff;
      border-radius: 8px;
      padding: 20px 24px;
      margin-bottom: 20px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }}
    .category h2 {{
      margin-top: 0;
      border-bottom: 2px solid #e0e0e0;
      padding-bottom: 8px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      padding: 10px 12px;
      text-align: left;
      border-bottom: 1px solid #eee;
      vertical-align: top;
    }}
    th {{
      background: #f1f3f5;
      font-weight: 600;
      font-size: 0.9em;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    th.store-col {{
      text-align: center;
      white-space: nowrap;
    }}
    .product .brand {{
      display: block;
      color: #888;
      font-size: 0.75em;
      margin-top: 2px;
    }}
    .tag {{
      background: #eee;
      color: #666;
      font-size: 0.7em;
      border-radius: 3px;
      padding: 1px 5px;
      margin-left: 4px;
    }}
    td.price {{
      text-align: center;
      font-weight: 600;
      position: relative;
      white-space: nowrap;
    }}
    td.price.best {{
      background: #e6f9e6;
    }}
    td.price.missing {{
      color: #ccc;
      font-weight: 400;
    }}
    .best-note {{
      display: block;
      color: #2d8a2d;
      font-size: 0.7em;
      font-weight: 600;
      margin-top: 2px;
    }}
    .delta {{
      display: block;
      color: #c0392b;
      font-size: 0.75em;
      font-weight: 400;
      margin-top: 2px;
    }}
    .was {{
      display: block;
      color: #999;
      text-decoration: line-through;
      font-size: 0.75em;
      font-weight: 400;
      margin-top: 2px;
    }}
    .winner {{
      text-align: center;
    }}
    .badge {{
      display: inline-block;
      color: #fff;
      font-size: 0.7em;
      font-weight: 600;
      border-radius: 4px;
      padding: 3px 8px;
      white-space: nowrap;
    }}
    .badge.tie {{
      background: #888;
    }}
    tr.only td.product {{
      opacity: 0.9;
    }}
    .empty {{
      color: #999;
      font-style: italic;
    }}
    .legend {{
      font-size: 0.8em;
      color: #666;
      margin-top: 16px;
    }}
    .legend .swatch {{
      display: inline-block;
      background: #e6f9e6;
      padding: 0 4px;
    }}{store_css}
  </style>
</head>
<body>
  <h1>&#129385; Meat Price Comparison</h1>
  <p class="subtitle">ZIP: {esc_zip} &middot; Generated on {escape(today)}</p>

  <div class="scoreboard">{scoreboard_html}
  </div>

{sections_html}

  <p class="legend"><span class="swatch">&#10003; best</span> = lowest price for that product &middot; +$X = how much more the other store charges &middot; "only" = product found at just one store</p>
</body>
</html>"""
