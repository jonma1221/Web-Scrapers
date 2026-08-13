export type JobStatus = "queued" | "running" | "done" | "failed";
export type StoreStatusValue = "pending" | "scraping" | "cached" | "done" | "failed";
export type Confidence = "exact" | "fuzzy_high" | "fuzzy_low" | "no_match";
export type Category = "beef" | null;

export interface StoreStatus {
  name: string;
  status: StoreStatusValue;
  product_count: number;
  error: string | null;
  cached: boolean;
  address: string | null;
}

export interface Scoreboard {
  wins: Record<string, number>;
  ties: number;
}

export interface PriceCell {
  store: string;
  sale_price: string;
  parsed_price: number | null;
  original_price: string | null;
  image_url: string;
  is_best: boolean;
  delta: number | null;
}

export interface ProductRow {
  display_name: string;
  brand: string;
  confidence: Confidence;
  tag: string;
  winner: string | null;
  only_store: string | null;
  prices: PriceCell[];
}

export interface Job {
  id: string;
  status: JobStatus;
  query: string;
  location: string;
  inferred_category: Category;
  generated_at: string | null;
  cached: boolean;
  error: string | null;
  stores: StoreStatus[];
  scoreboard: Scoreboard;
  products: ProductRow[];
}

interface JobIdResponse {
  job_id: string;
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(url, init);
  } catch {
    throw new Error("Network error — could not reach the server.");
  }

  if (!res.ok) {
    if (res.status === 404) {
      throw new Error(`Not found (404): ${url}`);
    }
    const body = await res.text().catch(() => "");
    throw new Error(
      `Request failed (${res.status})${body ? `: ${body}` : ""}`,
    );
  }

  return (await res.json()) as T;
}

export async function startSearch(query: string, location: string): Promise<string> {
  const data = await request<JobIdResponse>("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, location }),
  });
  return data.job_id;
}

export async function getJob(id: string): Promise<Job> {
  return request<Job>(`/api/search/${encodeURIComponent(id)}`);
}

export async function refreshSearch(id: string): Promise<string> {
  const data = await request<JobIdResponse>(
    `/api/search/${encodeURIComponent(id)}/refresh`,
    { method: "POST" },
  );
  return data.job_id;
}
