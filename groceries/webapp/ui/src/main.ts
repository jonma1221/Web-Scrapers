import { getJob, refreshSearch, startSearch } from "./api.ts";
import type { Job } from "./api.ts";
import { renderError, renderLoading, renderResults } from "./render.ts";

const form = document.getElementById("search-form") as HTMLFormElement;
const locationInput = document.getElementById("location") as HTMLInputElement;
const productInput = document.getElementById("product") as HTMLInputElement;
const searchBtn = document.getElementById("search-btn") as HTMLButtonElement;
const errorEl = document.getElementById("error") as HTMLDivElement;
const resultsEl = document.getElementById("results") as HTMLDivElement;

let busy = false;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function setError(message: string | null): void {
  if (message === null) {
    errorEl.hidden = true;
    errorEl.textContent = "";
  } else {
    errorEl.textContent = message;
    errorEl.hidden = false;
  }
}

function setFormEnabled(enabled: boolean): void {
  locationInput.disabled = !enabled;
  productInput.disabled = !enabled;
  searchBtn.disabled = !enabled;
  form.classList.toggle("loading", !enabled);
}

async function poll(jobId: string): Promise<void> {
  let job: Job = await getJob(jobId);
  renderLoading(resultsEl, job);

  while (job.status === "queued" || job.status === "running") {
    await sleep(2000);
    job = await getJob(jobId);
    renderLoading(resultsEl, job);
  }

  if (job.status === "failed") {
    renderError(resultsEl, job);
  } else {
    renderResults(resultsEl, job, () => {
      void refresh(job);
    });
  }
}

async function refresh(job: Job): Promise<void> {
  if (busy) return;
  busy = true;
  setFormEnabled(false);
  setError(null);
  try {
    const newJobId = await refreshSearch(job.id);
    await poll(newJobId);
  } catch (err) {
    setError(err instanceof Error ? err.message : "Unexpected error");
  } finally {
    busy = false;
    setFormEnabled(true);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  if (busy) return;

  const query = productInput.value.trim();
  const location = locationInput.value.trim();
  if (!query || !location) {
    setError("Please enter both a location and a product.");
    return;
  }

  busy = true;
  setFormEnabled(false);
  setError(null);
  void (async () => {
    try {
      const jobId = await startSearch(query, location);
      await poll(jobId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      busy = false;
      setFormEnabled(true);
    }
  })();
});
