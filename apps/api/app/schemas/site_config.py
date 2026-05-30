"""
schemas/site_config.py — Pydantic models for site configuration.

What it does:
  SiteConfigRead  — outbound shape for GET responses; secrets are masked
  SiteConfigWrite — inbound payload for PUT /site-config/{key}

How it connects:
  - app/routers/site_config.py uses these as request/response_model types.
  - app/crud/site_config.py receives SiteConfigWrite after validation.
"""

from pydantic import BaseModel


class SiteConfigRead(BaseModel):
    id:         int
    church_id:  str
    key:        str
    value:      str | None   # "***" when is_secret=True
    is_secret:  bool
    is_json:    bool
    updated_at: str | None

    model_config = {"from_attributes": True}


class SiteConfigWrite(BaseModel):
    value:     str
    is_secret: bool = False
    is_json:   bool = False
