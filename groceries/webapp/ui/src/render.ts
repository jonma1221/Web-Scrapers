import type { Job, PriceCell, ProductRow, StoreStatus } from "./api.ts";

export const STORE_COLORS = ["#e67e22", "#2d6da3", "#2d8a2d", "#8e44ad", "#c0392b"];

export function storeColor(index: number): string {
  return STORE_COLORS[index % STORE_COLORS.length];
}

const STORE_STATUS_LABEL: Record<StoreStatus["status"], string> = {
  pending: "queued…",
  scraping: "scraping…",
  cached: "cached ✓",
  done: "done",
  failed: "failed",
};

function storeStatusText(store: StoreStatus): string {
  if (store.status === "failed") {
    return store.error ? `${store.name}: failed — ${store.error}` : `${store.name}: failed`;
  }
  if (store.status === "scraping" && store.product_count > 0) {
    return `${store.name}: scraping… ${store.product_count} products`;
  }
  if (store.status === "done" && store.product_count > 0) {
    return `${store.name}: done — ${store.product_count} products`;
  }
  return `${store.name}: ${STORE_STATUS_LABEL[store.status]}`;
}

function makeDot(index: number): HTMLSpanElement {
  const dot = document.createElement("span");
  dot.className = "dot";
  dot.style.background = storeColor(index);
  return dot;
}

function makeSub(className: string, text: string): HTMLSpanElement {
  const span = document.createElement("span");
  span.className = className;
  span.textContent = text;
  return span;
}

const PRODUCT_PLACEHOLDER =
  "data:image/svg+xml," +
  encodeURIComponent(
    "<svg xmlns='http://www.w3.org/2000/svg' width='56' height='56'>" +
      "<rect width='56' height='56' fill='#f0f0f0'/>" +
      "<g fill='#c4c4c4' stroke='#c4c4c4' stroke-width='1.5' stroke-linejoin='round'>" +
      "<path d='M22 21v-1a6 6 0 0 1 12 0v1' fill='none'/>" +
      "<path d='M19 21h18l-2 16a3 3 0 0 1-3 3H24a3 3 0 0 1-3-3z'/>" +
      "<path d='M28 27v8M24 29v6M32 29v6' stroke-linecap='round'/>" +
      "</g></svg>",
  );

function pickImage(product: ProductRow): string {
  const cells = product.prices;
  const winner = cells.find((c) => c.is_best && c.image_url);
  const first = cells.find((c) => c.image_url);
  return (winner ?? first)?.image_url ?? "";
}

function pickTitleUrl(product: ProductRow): string {
  const cells = product.prices;
  const winner = cells.find((c) => c.is_best && c.url);
  const first = cells.find((c) => c.url);
  return (winner ?? first)?.url ?? "";
}

function makeThumb(src: string): HTMLImageElement {
  const img = document.createElement("img");
  img.className = "product-thumb";
  img.alt = "";
  img.loading = "lazy";
  img.referrerPolicy = "no-referrer";
  const resolved =
    src && src.startsWith("//") ? `https:${src}` : src || PRODUCT_PLACEHOLDER;
  img.src = resolved;
  if (src) {
    img.addEventListener("error", () => {
      img.src = PRODUCT_PLACEHOLDER;
    });
  }
  return img;
}

function makeTag(text: string, extraClass: string): HTMLSpanElement {
  const tag = document.createElement("span");
  tag.className = extraClass ? `tag ${extraClass}` : "tag";
  tag.textContent = text;
  return tag;
}

function makeExtLink(): HTMLSpanElement {
  const icon = document.createElement("span");
  icon.className = "ext-link";
  icon.setAttribute("aria-hidden", "true");
  icon.textContent = "↗";
  return icon;
}

export function renderLoading(root: HTMLElement, job: Job): void {
  root.replaceChildren();

  const panel = document.createElement("section");
  panel.className = "status-panel";

  const heading = document.createElement("h2");
  heading.textContent = `Searching for “${job.query}” near ${job.location}…`;
  panel.appendChild(heading);

  const list = document.createElement("ul");
  list.className = "store-status-list";
  job.stores.forEach((store, index) => {
    const item = document.createElement("li");
    item.append(makeDot(index), document.createTextNode(storeStatusText(store)));
    list.appendChild(item);
  });
  panel.appendChild(list);

  root.appendChild(panel);
}

export function renderResults(
  root: HTMLElement,
  job: Job,
  onRefresh: () => void,
): void {
  root.replaceChildren();

  const card = document.createElement("section");
  card.className = "results-card";

  const head = document.createElement("div");
  head.className = "results-head";

  const title = document.createElement("h2");
  title.className = "results-title";
  title.textContent = job.query;
  head.appendChild(title);

  const meta = document.createElement("p");
  meta.className = "results-meta";
  const storeCount = job.stores.length;
  meta.textContent = `${job.products.length} products compared across ${storeCount} stores near ${job.location}`;
  head.appendChild(meta);

  if (job.cached) {
    const cached = document.createElement("p");
    cached.className = "cached-note";
    cached.textContent = "Loaded from cache — Refresh to re-scrape";
    head.appendChild(cached);
  }

  const actions = document.createElement("div");
  actions.className = "results-actions";
  const refreshBtn = document.createElement("button");
  refreshBtn.type = "button";
  refreshBtn.className = "refresh-btn";
  refreshBtn.textContent = "Refresh";
  refreshBtn.addEventListener("click", onRefresh);
  actions.appendChild(refreshBtn);
  head.appendChild(actions);

  card.appendChild(head);

  const failedStores = job.stores.filter((s) => s.status === "failed");
  if (failedStores.length > 0) {
    const note = document.createElement("p");
    note.className = "partial-note";
    note.textContent = `${failedStores.map((s) => s.name).join(", ")} failed — showing comparison from the other stores.`;
    card.appendChild(note);
  }

  if (job.products.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "No products found";
    card.appendChild(empty);
    root.appendChild(card);
    return;
  }

  const legend = document.createElement("div");
  legend.className = "store-legend";
  job.stores.forEach((store, index) => {
    const chip = document.createElement("span");
    chip.className = "legend-chip";
    const headChip = document.createElement("span");
    headChip.className = "legend-chip-head";
    headChip.append(makeDot(index), document.createTextNode(store.name));
    chip.appendChild(headChip);
    if (store.address) {
      chip.appendChild(makeSub("chip-loc", store.address));
    }
    if (store.status === "failed" && store.error) {
      chip.appendChild(makeSub("chip-err", store.error));
    }
    legend.appendChild(chip);
  });
  card.appendChild(legend);

  const list = document.createElement("div");
  list.className = "product-list";
  const stores = job.stores.map((s) => s.name);
  for (const product of job.products) {
    list.appendChild(productCard(product, stores));
  }
  card.appendChild(list);

  const notes = document.createElement("p");
  notes.className = "legend";
  notes.textContent =
    '✓ cheapest = lowest price for that product · +$X = how much more the other store charges · ' +
    '"only store" = product found at just one store · "~ likely match" = names differ but appear to be the same product (not scored)';
  card.appendChild(notes);

  root.appendChild(card);
}

export function renderError(root: HTMLElement, job: Job): void {
  root.replaceChildren();

  const panel = document.createElement("section");
  panel.className = "error-panel";

  const heading = document.createElement("h2");
  heading.textContent = "Search failed";
  panel.appendChild(heading);

  const message = document.createElement("p");
  message.textContent = job.error || "Something went wrong while fetching prices.";
  panel.appendChild(message);

  root.appendChild(panel);
}

function productCard(product: ProductRow, stores: string[]): HTMLElement {
  const card = document.createElement("article");
  card.className = "product-card";
  if (product.confidence === "fuzzy_low") card.classList.add("fuzzy");
  if (product.only_store) card.classList.add("only");

  const titleUrl = pickTitleUrl(product);
  const title = document.createElement(titleUrl ? "a" : "div");
  title.className = "product-title";
  if (titleUrl) {
    title.setAttribute("href", titleUrl);
    title.setAttribute("target", "_blank");
    title.setAttribute("rel", "noopener");
  }

  title.appendChild(makeThumb(pickImage(product)));

  const identity = document.createElement("div");
  identity.className = "product-identity";

  const name = document.createElement("span");
  name.className = "product-name";
  name.textContent = product.display_name;
  identity.appendChild(name);

  if (product.brand) {
    identity.appendChild(makeSub("brand", product.brand));
  }

  const tag = productTag(product);
  if (tag) identity.appendChild(tag);

  title.appendChild(identity);
  card.appendChild(title);
  card.appendChild(storeCells(product, stores));
  return card;
}

function productTag(product: ProductRow): HTMLSpanElement | null {
  if (product.confidence === "fuzzy_low" || product.tag === "~ likely match") {
    return makeTag("~ likely match", "fuzzy");
  }
  return null;
}

function storeCells(product: ProductRow, stores: string[]): HTMLElement {
  const grid = document.createElement("div");
  grid.className = "store-cells";

  const bestCells = product.prices.filter((c) => c.is_best);
  const firstBestStore = bestCells[0]?.store ?? null;

  for (const store of stores) {
    const cell = product.prices.find((p) => p.store === store);
    if (!cell || cell.parsed_price === null) {
      grid.appendChild(missingCell(store));
      continue;
    }
    grid.appendChild(priceCell(cell, store, product, firstBestStore, stores));
  }

  return grid;
}

function missingCell(store: string): HTMLElement {
  const cell = document.createElement("div");
  cell.className = "store-cell missing";
  const name = document.createElement("p");
  name.className = "store-cell-name";
  name.textContent = store;
  const dash = document.createElement("p");
  dash.className = "store-cell-dash";
  dash.textContent = "—";
  cell.append(name, dash);
  return cell;
}

function priceCell(
  cell: PriceCell,
  store: string,
  product: ProductRow,
  firstBestStore: string | null,
  stores: string[],
): HTMLElement {
  const index = stores.indexOf(store);
  const el = document.createElement(cell.url ? "a" : "div");
  el.className = cell.is_best ? "store-cell best" : "store-cell";
  if (cell.url) {
    el.setAttribute("href", cell.url);
    el.setAttribute("target", "_blank");
    el.setAttribute("rel", "noopener");
  }

  const name = document.createElement("p");
  name.className = "store-cell-name";
  name.append(makeDot(index), document.createTextNode(store));
  if (cell.url) name.appendChild(makeExtLink());
  el.appendChild(name);

  if (cell.original_price) {
    el.appendChild(makeSub("was", cell.original_price));
  }

  const price = document.createElement("p");
  price.className = "store-cell-price";
  price.textContent = cell.sale_price;
  el.appendChild(price);

  if (cell.delta !== null && cell.delta > 0) {
    el.appendChild(makeSub("delta", `+$${cell.delta.toFixed(2)}`));
  }

  const note = bestNote(cell, product, firstBestStore);
  if (note) {
    el.appendChild(makeSub("best-note", note));
  }

  return el;
}

function bestNote(
  cell: PriceCell,
  product: ProductRow,
  firstBestStore: string | null,
): string {
  if (!cell.is_best) return "";
  if (product.only_store) return "only store";
  if (firstBestStore === null || cell.store === firstBestStore) return "✓ cheapest";
  return "tie";
}
