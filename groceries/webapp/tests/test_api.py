"""API tests against the FastAPI app with a fully mocked scrape pipeline."""

import threading
import time

import pytest

# Keys the API contract guarantees on every product row and price cell.
ROW_KEYS = {
    "display_name",
    "brand",
    "confidence",
    "tag",
    "winner",
    "only_store",
    "prices",
}
PRICE_KEYS = {
    "store",
    "sale_price",
    "parsed_price",
    "original_price",
    "image_url",
    "url",
    "is_best",
    "delta",
}

POLL_INTERVAL = 0.05
POLL_TIMEOUT = 10.0


def _wait_for_job(client, job_id, expected_status="done"):
    """Poll GET /api/search/{id} until the job leaves the 'running' state."""
    deadline = time.time() + POLL_TIMEOUT
    data = None
    while time.time() < deadline:
        resp = client.get(f"/api/search/{job_id}")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        if data["status"] != "running":
            break
        time.sleep(POLL_INTERVAL)
    assert data is not None, "poll timed out with no job response"
    assert data["status"] == expected_status, data
    return data


def test_create_search_returns_202_and_dedupes(client, mock_pipeline):
    mock_pipeline.gate = threading.Event()
    body = {"query": "large eggs", "location": "94110"}

    resp = client.post("/api/search", json=body)
    assert resp.status_code == 202, resp.text
    assert resp.json()["job_id"], "202 response should include a job_id"
    job_id = resp.json()["job_id"]

    state = client.get(f"/api/search/{job_id}").json()
    assert state["status"] in ("queued", "running")

    resp2 = client.post("/api/search", json=body)
    assert resp2.status_code == 202, resp2.text
    assert (
        resp2.json()["job_id"] == job_id
    ), "an identical queued/running search should dedupe to the same job"

    mock_pipeline.gate.set()
    _wait_for_job(client, job_id)


def test_completed_job_matches_api_contract(client, mock_pipeline):
    resp = client.post(
        "/api/search", json={"query": "ground beef", "location": "94110"}
    )
    assert resp.status_code == 202, resp.text
    job_id = resp.json()["job_id"]
    data = _wait_for_job(client, job_id)

    assert data["id"] == job_id
    assert data["status"] == "done"
    assert data["query"] == "ground beef"
    assert data["location"] == "94110"
    assert data["inferred_category"] == "beef"
    assert data["generated_at"], "generated_at should be an ISO timestamp"
    assert data["error"] is None
    assert data["cached"] is False

    stores = {store["name"]: store for store in data["stores"]}
    assert set(stores) == {"FoodMaxx", "Lucky", "Grocery Outlet"}
    assert stores["FoodMaxx"]["status"] == "done"
    assert stores["FoodMaxx"]["product_count"] == 1
    assert stores["FoodMaxx"]["cached"] is False
    assert stores["Lucky"]["status"] == "done"
    assert stores["Lucky"]["product_count"] == 1
    assert stores["Grocery Outlet"]["status"] == "failed"
    assert "Grocery Outlet" in (stores["Grocery Outlet"]["error"] or "")

    assert data["scoreboard"]["wins"]["FoodMaxx"] == 1
    assert data["scoreboard"]["ties"] == 0

    assert data["products"], "a completed job should have product rows"
    row = data["products"][0]
    assert set(row) == ROW_KEYS
    assert row["confidence"] in ("exact", "fuzzy_high", "fuzzy_low", "no_match")
    assert row["prices"], "each row should have at least one price cell"
    price = row["prices"][0]
    assert set(price) == PRICE_KEYS
    assert isinstance(price["parsed_price"], float)
    assert isinstance(price["is_best"], bool)


@pytest.mark.parametrize(
    "body",
    [
        {"query": "", "location": "94110"},
        {"query": "   ", "location": "94110"},
        {"query": "eggs", "location": ""},
        {"query": "eggs", "location": "    "},
    ],
)
def test_search_rejects_blank_query_or_location(client, body):
    resp = client.post("/api/search", json=body)
    assert resp.status_code == 422, resp.text


def test_get_unknown_job_returns_404(client):
    resp = client.get("/api/search/00000000000000000000000000000000")
    assert resp.status_code == 404


def test_refresh_completed_job_returns_new_job(client, mock_pipeline):
    first = client.post(
        "/api/search", json={"query": "ground beef", "location": "94110"}
    )
    assert first.status_code == 202
    first_id = first.json()["job_id"]
    _wait_for_job(client, first_id)

    resp = client.post(f"/api/search/{first_id}/refresh")
    assert resp.status_code == 202, resp.text
    new_id = resp.json()["job_id"]
    assert new_id != first_id, "refresh should start a brand new job"

    data = _wait_for_job(client, new_id)
    assert data["status"] == "done"
    assert data["query"] == "ground beef"


def test_slow_store_times_out_but_comparison_continues(client, mock_pipeline, monkeypatch):
    monkeypatch.setattr("api.jobs._STORE_TIMEOUT_SECONDS", 0.2)
    mock_pipeline.failures = set()
    mock_pipeline.delays = {"Grocery Outlet": 5.0}

    job_id = client.post(
        "/api/search", json={"query": "large eggs", "location": "94110"}
    ).json()["job_id"]
    data = _wait_for_job(client, job_id)

    assert data["status"] == "done", "a hung store must not fail the whole job"
    stores = {store["name"]: store for store in data["stores"]}
    assert stores["FoodMaxx"]["status"] == "done"
    assert stores["Lucky"]["status"] == "done"
    assert stores["FoodMaxx"]["product_count"] == 1
    assert stores["Lucky"]["product_count"] == 1
    assert stores["Grocery Outlet"]["status"] == "failed"
    assert "timed out" in stores["Grocery Outlet"]["error"]
    assert data["products"], "the two good stores should still produce results"


def test_second_search_hits_cache(client, mock_pipeline):
    body = {"query": "large eggs", "location": "94110"}

    first_id = client.post("/api/search", json=body).json()["job_id"]
    first = _wait_for_job(client, first_id)
    assert first["status"] == "done"

    second_id = client.post("/api/search", json=body).json()["job_id"]
    assert second_id != first_id, "a completed job should not be deduped"
    second = _wait_for_job(client, second_id)

    stores = {store["name"]: store for store in second["stores"]}
    assert stores["FoodMaxx"]["status"] == "cached"
    assert stores["FoodMaxx"]["cached"] is True
    assert stores["FoodMaxx"]["product_count"] == 1
    assert stores["Lucky"]["status"] == "cached"
    assert stores["Lucky"]["cached"] is True
    assert stores["Lucky"]["product_count"] == 1
    # Grocery Outlet never cached (it always fails), so it is re-scraped
    # and fails again on the second run.
    assert stores["Grocery Outlet"]["status"] == "failed"

    assert second["products"], "cached products should still be present"
    assert second["products"][0]["winner"] == "FoodMaxx"


def test_cheapest_store_wins(client, mock_pipeline, make_product):
    mock_pipeline.products_by_store = {
        "FoodMaxx": [make_product("FoodMaxx", "Large Eggs 12 ct", "$2.49")],
        "Lucky": [make_product("Lucky", "12 count large eggs", "$2.99")],
    }
    job_id = client.post(
        "/api/search", json={"query": "large eggs", "location": "94110"}
    ).json()["job_id"]
    data = _wait_for_job(client, job_id)

    assert len(data["products"]) == 1
    row = data["products"][0]
    assert row["winner"] == "FoodMaxx"
    assert data["scoreboard"]["wins"]["FoodMaxx"] == 1
    assert data["scoreboard"]["ties"] == 0

    prices = {price["store"]: price for price in row["prices"]}
    assert prices["FoodMaxx"]["is_best"] is True
    assert prices["FoodMaxx"]["delta"] is None
    assert prices["Lucky"]["is_best"] is False
    assert prices["Lucky"]["delta"] == pytest.approx(0.5)


def test_equal_prices_produce_tie(client, mock_pipeline, make_product):
    mock_pipeline.products_by_store = {
        "FoodMaxx": [make_product("FoodMaxx", "Large Eggs 12 ct", "$2.49")],
        "Lucky": [make_product("Lucky", "12 count large eggs", "$2.49")],
    }
    job_id = client.post(
        "/api/search", json={"query": "eggs", "location": "94110"}
    ).json()["job_id"]
    data = _wait_for_job(client, job_id)

    assert len(data["products"]) == 1
    row = data["products"][0]
    assert row["winner"] == "Tie"
    assert data["scoreboard"]["ties"] == 1

    prices = {price["store"]: price for price in row["prices"]}
    assert prices["FoodMaxx"]["is_best"] is True
    assert prices["Lucky"]["is_best"] is True
    assert prices["FoodMaxx"]["delta"] is None
    assert prices["Lucky"]["delta"] is None
