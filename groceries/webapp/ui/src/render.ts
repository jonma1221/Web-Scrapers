import type { Job, ProductRow, StoreStatus } from "./api.ts";

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

  const title = document.createElement("h2");
  title.textContent = `Results for “${job.query}” near ${job.location}`;
  card.appendChild(title);

  if (job.generated_at) {
    const meta = document.createElement("p");
    meta.className = "results-meta";
    meta.textContent = `Generated ${new Date(job.generated_at).toLocaleString()}`;
    card.appendChild(meta);
  }

  if (job.cached) {
    const cached = document.createElement("p");
    cached.className = "cached-note";
    cached.textContent = "Loaded from cache — Refresh to re-scrape";
    card.appendChild(cached);
  }

  const actions = document.createElement("div");
  actions.className = "results-actions";
  const refreshBtn = document.createElement("button");
  refreshBtn.type = "button";
  refreshBtn.className = "refresh-btn";
  refreshBtn.textContent = "Refresh";
  refreshBtn.addEventListener("click", onRefresh);
  actions.appendChild(refreshBtn);
  card.appendChild(actions);

  if (job.products.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "No products found";
    card.appendChild(empty);
    root.appendChild(card);
    return;
  }

  card.appendChild(scoreboard(job));
  card.appendChild(productList(job));

  const legend = document.createElement("p");
  legend.className = "legend";
  legend.textContent =
    '✓ best = lowest price for that product · +$X = how much more the other store charges · ' +
    '"only" = product found at just one store · "~ likely match" = names differ but appear to be the same product (not scored)';
  card.appendChild(legend);

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

function scoreboard(job: Job): HTMLElement {
  const board = document.createElement("div");
  board.className = "scoreboard";

  job.stores.forEach((store, index) => {
    const chip = document.createElement("div");
    chip.className = "score-chip";
    const label = document.createElement("span");
    label.textContent = `${store.name} wins `;
    const strong = document.createElement("strong");
    strong.textContent = String(job.scoreboard.wins[store.name] ?? 0);
    chip.append(makeDot(index), label, strong);
    board.appendChild(chip);
  });

  const tieChip = document.createElement("div");
  tieChip.className = "score-chip";
  tieChip.append(document.createTextNode("Ties "));
  const strong = document.createElement("strong");
  strong.textContent = String(job.scoreboard.ties);
  tieChip.appendChild(strong);
  board.appendChild(tieChip);

  return board;
}

function productList(job: Job): HTMLElement {
  const list = document.createElement("div");
  list.className = "product-list";

  const legend = document.createElement("div");
  legend.className = "store-legend";
  job.stores.forEach((store, index) => {
    const chip = document.createElement("span");
    chip.className = "legend-chip";
    const head = document.createElement("span");
    head.className = "legend-chip-head";
    head.append(makeDot(index), document.createTextNode(store.name));
    chip.appendChild(head);
    if (store.address) {
      chip.appendChild(makeSub("chip-loc", store.address));
    }
    legend.appendChild(chip);
  });
  list.appendChild(legend);

  const stores = job.stores.map((s) => s.name);
  for (const product of job.products) {
    list.appendChild(productCard(product, stores));
  }

  return list;
}

function productCard(product: ProductRow, stores: string[]): HTMLElement {
  const card = document.createElement("article");
  card.className = "product-card";
  if (product.confidence === "fuzzy_low") card.classList.add("fuzzy");
  if (product.only_store) card.classList.add("only");

  const head = document.createElement("div");
  head.className = "product-head";

  const title = document.createElement("div");
  title.className = "product-title";
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

  head.appendChild(title);
  head.appendChild(winnerBadge(product.winner, stores));

  card.appendChild(head);
  card.appendChild(storeLines(product, stores));
  return card;
}

function storeLines(product: ProductRow, stores: string[]): HTMLElement {
  const lines = document.createElement("div");
  lines.className = "store-lines";

  for (const store of stores) {
    const cell = product.prices.find((p) => p.store === store);
    const line = document.createElement("div");
    line.className = "store-line";

    const idx = stores.indexOf(store);
    line.append(makeDot(idx));

    const name = document.createElement("span");
    name.className = "store-line-name";
    name.textContent = store;
    line.appendChild(name);

    if (!cell || cell.parsed_price === null) {
      line.classList.add("missing");
      const na = document.createElement("span");
      na.className = "store-line-na";
      na.textContent = "not available";
      line.appendChild(na);
      lines.appendChild(line);
      continue;
    }

    if (cell.is_best) line.classList.add("best");

    const price = document.createElement("span");
    price.className = "store-line-price";
    price.textContent = cell.sale_price;
    line.appendChild(price);

    if (cell.original_price) {
      line.appendChild(makeSub("was", `was ${cell.original_price}`));
    }
    if (cell.delta !== null && cell.delta > 0) {
      line.appendChild(makeSub("delta", `+$${cell.delta.toFixed(2)}`));
    }
    if (cell.is_best) {
      line.appendChild(makeSub("best-note", "✓ best"));
    }

    lines.appendChild(line);
  }

  return lines;
}

function productTag(product: ProductRow): HTMLSpanElement | null {
  if (product.confidence === "fuzzy_low" || product.tag === "~ likely match") {
    return makeTag("~ likely match", "fuzzy");
  }
  if (product.only_store) {
    return makeTag(`${product.only_store} only`, "");
  }
  if (product.tag) {
    return makeTag(product.tag, "");
  }
  return null;
}

function winnerBadge(winner: string | null, stores: string[]): HTMLElement {
  if (!winner) {
    const span = document.createElement("span");
    span.className = "no-winner";
    span.textContent = "—";
    return span;
  }

  const badge = document.createElement("span");
  badge.className = "badge";

  if (winner === "Tie") {
    badge.classList.add("tie");
    badge.textContent = "Tie";
  } else if (winner === "~") {
    badge.classList.add("fuzzy");
    badge.textContent = "~";
  } else {
    const index = stores.indexOf(winner);
    badge.style.background = storeColor(index === -1 ? 0 : index);
    badge.textContent = winner;
  }

  return badge;
}
