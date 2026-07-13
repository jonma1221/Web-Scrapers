"""HTML comparison renderer for meat deals across stores."""

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


def _parse_price(price_str: str) -> float | None:
    """Extract the per-unit numeric price from a price string.

    Handles formats like:
      - "$4.99"         -> 4.99
      - "2 for $5.00"   -> 2.50  (per unit)
      - "$10/ea"        -> 10.00
      - "BOGO"          -> None  (unparseable)
    """
    price_str = price_str.strip()

    # Try "N for $X.XX" pattern — divide total by quantity
    match = re.search(r"(\d+)\s+for\s+\$(\d+(?:\.\d{1,2})?)", price_str, re.IGNORECASE)
    if match:
        qty = int(match.group(1))
        total = float(match.group(2))
        return total / qty if qty > 0 else None

    # Try plain "$X.XX" pattern
    match = re.search(r"\$(\d+(?:\.\d{1,2})?)", price_str)
    if match:
        return float(match.group(1))

    return None


def _format_price_with_unit(price_str: str) -> str:
    """Format a price string for display.

    If it's a multi-unit deal, append the per-unit price in parentheses.
    """
    parsed = _parse_price(price_str)
    if parsed is None:
        return escape(price_str)

    # Check if this was a multi-unit deal
    match = re.search(r"(\d+)\s+for\s+\$(\d+(?:\.\d{1,2})?)", price_str, re.IGNORECASE)
    if match:
        qty = int(match.group(1))
        total = float(match.group(2))
        return f"{escape(price_str)} (${parsed:.2f}/ea)"
    else:
        return escape(price_str)


def generate_html(meat_deals: list[MeatDeal], zip_code: str) -> str:
    """Generate an HTML comparison page for meat deals.

    Groups deals by category, matches products across stores by name
    (case-insensitive), and highlights the lowest per-unit price per product.

    Args:
        meat_deals: List of MeatDeal objects to display.
        zip_code: The ZIP code used for the store search (shown in subtitle).

    Returns:
        A complete HTML string with inline CSS and comparison tables.
    """
    today = date.today().strftime("%B %d, %Y")
    esc_zip = escape(zip_code)

    # Group deals by category
    deals_by_category: dict[str, list[MeatDeal]] = defaultdict(list)
    for deal in meat_deals:
        deals_by_category[deal.category.lower()].append(deal)

    # Build HTML sections for each category
    category_sections: list[str] = []
    for cat in CATEGORY_ORDER:
        display_name = CATEGORY_DISPLAY.get(cat, cat.title())
        deals = deals_by_category.get(cat, [])

        if not deals:
            category_sections.append(
                f"""
        <div class="category-section">
          <h2>{escape(display_name)}</h2>
          <p class="no-deals">No deals found</p>
        </div>"""
            )
            continue

        # Build product rows — match products across stores by name
        # Key: normalized product name -> list of MeatDeal across stores
        products: dict[str, list[MeatDeal]] = defaultdict(list)
        for deal in deals:
            key = deal.name.strip().lower()
            products[key].append(deal)

        # Determine the best (lowest per-unit) price for each product
        best_prices: dict[str, float] = {}
        for key, product_deals in products.items():
            prices = []
            for d in product_deals:
                parsed = _parse_price(d.sale_price)
                if parsed is not None:
                    prices.append(parsed)
            if prices:
                best_prices[key] = min(prices)

        # Build table rows — one row per store per product
        rows: list[str] = []
        for key in sorted(products.keys()):
            product_deals = products[key]
            for deal in sorted(product_deals, key=lambda d: d.store_name):
                parsed = _parse_price(deal.sale_price)
                is_best = (
                    parsed is not None
                    and best_prices.get(key) is not None
                    and abs(parsed - best_prices[key]) < 0.005
                )
                row_class = "best" if is_best else ""
                star = "⭐ " if is_best else ""

                original_html = (
                    f"<span class='original-price'>{escape(deal.original_price)}</span>"
                    if deal.original_price
                    else ""
                )

                rows.append(
                    f'            <tr class="{row_class}">'
                    f"<td>{escape(deal.store_name)}</td>"
                    f"<td>{star}{escape(deal.name)}</td>"
                    f"<td>{escape(deal.brand)}</td>"
                    f"<td class='sale-price'>{_format_price_with_unit(deal.sale_price)}</td>"
                    f"<td>{original_html}</td>"
                    f"</tr>"
                )

        rows_html = "\n".join(rows)

        category_sections.append(
            f"""
        <div class="category-section">
          <h2>{escape(display_name)}</h2>
          <table>
            <thead>
              <tr>
                <th>Store</th>
                <th>Product Name</th>
                <th>Brand</th>
                <th>Sale Price</th>
                <th>Original Price</th>
              </tr>
            </thead>
            <tbody>
{rows_html}
            </tbody>
          </table>
        </div>"""
        )

    sections_html = "\n".join(category_sections)

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
      background: #f8f9fa;
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
    .category-section {{
      background: #fff;
      border-radius: 8px;
      padding: 20px 24px;
      margin-bottom: 20px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }}
    .category-section h2 {{
      margin-top: 0;
      border-bottom: 2px solid #e0e0e0;
      padding-bottom: 8px;
    }}
    .no-deals {{
      color: #999;
      font-style: italic;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      padding: 10px 12px;
      text-align: left;
      border-bottom: 1px solid #eee;
    }}
    th {{
      background: #f1f3f5;
      font-weight: 600;
      font-size: 0.9em;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    tr:hover {{
      background: #f5f5f5;
    }}
    tr.best {{
      background: #d4edda !important;
    }}
    .sale-price {{
      font-weight: 600;
      color: #28a745;
    }}
    .original-price {{
      text-decoration: line-through;
      color: #999;
    }}
  </style>
</head>
<body>
  <h1>🥩 Meat Price Comparison</h1>
  <p class="subtitle">ZIP: {esc_zip} &middot; Generated on {escape(today)}</p>

{sections_html}

</body>
</html>"""
