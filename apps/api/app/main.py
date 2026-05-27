"""
main.py — FastAPI application entry point.

What it does:
  Creates and configures the FastAPI app instance. All routers are
  registered here. This is the file uvicorn targets when starting the server.

Why it exists at this layer:
  FastAPI requires a single importable `app` object. Keeping it in app/main.py
  (rather than the package root) makes the import path unambiguous and lets
  alembic, pytest, and uvicorn all find the app consistently.

How it connects:
  - tests/conftest.py imports `app` from here to build the TestClient.
  - version.json (repo root) is the single source of truth for version info,
    read at startup so the /health response is always in sync.
"""

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import me as me_router

# ---------------------------------------------------------------------------
# Version — read from repo root version.json (single source of truth)
# ---------------------------------------------------------------------------
try:
    _VERSION_FILE = Path(__file__).resolve().parents[3] / "version.json"
    _version_data: dict = json.loads(_VERSION_FILE.read_text())
except (FileNotFoundError, IndexError):
    _version_data = {"version": "0.1.0", "codename": "Kootenai"}

VERSION: str = _version_data["version"]
CODENAME: str = _version_data["codename"]

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ChurchOS API",
    version=VERSION,
    description="Open-source church CMS — REST API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tightened per-environment in Phase 3
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(me_router.router)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health", tags=["meta"])
async def health() -> dict:
    """
    Health check endpoint.

    Returns the API status, semantic version, and release codename.
    Visible in the site footer, admin topbar badge, and monitoring dashboards.
    """
    return {
        "status": "ok",
        "version": VERSION,
        "codename": CODENAME,
    }
