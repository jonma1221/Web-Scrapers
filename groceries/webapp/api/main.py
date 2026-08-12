"""FastAPI application for the grocery price-comparison webapp.

Run from repo root: ``.venv/bin/uvicorn api.main:app`` (with
``groceries/webapp`` on PYTHONPATH) or via
``from api.main import app``.
"""

import sys
from pathlib import Path

WEBAPP_DIR = Path(__file__).parent.parent
GROCERIES_DIR = WEBAPP_DIR.parent
sys.path.insert(0, str(WEBAPP_DIR))
sys.path.insert(0, str(GROCERIES_DIR))
sys.path.insert(0, str(GROCERIES_DIR.parent))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api import routes
from api.cache import get_cache

UI_DIST = Path(__file__).parent.parent / "ui" / "dist"

app = FastAPI(title="Grocery Price Compare")
app.include_router(routes.router)


@app.on_event("shutdown")
async def close_cache() -> None:
    """Close the SQLite cache connection on shutdown."""
    cache = await get_cache()
    await cache.close()


@app.get("/api/health")
async def health() -> dict:
    """Simple liveness check."""
    return {"status": "ok"}


if UI_DIST.is_dir():
    app.mount("/", StaticFiles(directory=UI_DIST, html=True))
