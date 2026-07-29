"""
crud/storage.py — Supabase Storage REST calls for public file uploads.

What it does:
  upload_public_file — uploads bytes to a public Supabase Storage bucket,
                        returns the resulting public URL.

Why it exists at this layer:
  Same rationale as crud/site_config.py — isolates the Supabase REST call
  so routers stay thin and the call is independently patchable in tests.
  Uses the same httpx-against-Supabase-REST style as the rest of app/crud/
  rather than the supabase-py SDK, so there's only one HTTP client pattern
  in the codebase.

How it connects:
  - app/routers/site_config.py POST /site-config/logo calls this to store
    the uploaded church logo, then writes the returned URL into site_config.

Manual prerequisite:
  The target bucket must exist and allow public read. Create it once via
  Supabase dashboard → Storage → New bucket → name it to match LOGO_BUCKET
  below → toggle "Public bucket" on. No new env vars needed — this reuses
  settings.supabase_url / settings.supabase_service_key.
"""

import httpx

from app.config import settings

LOGO_BUCKET = "public-assets"


def upload_public_file(bucket: str, path: str, content: bytes, content_type: str) -> str:
    """
    Upload `content` to `bucket/path` in Supabase Storage (upsert: true so a
    re-upload of the same path overwrites rather than erroring), and return
    the public URL.
    """
    upload_url = f"{settings.supabase_url}/storage/v1/object/{bucket}/{path}"
    headers = {
        "apikey":        settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type":  content_type,
        "x-upsert":      "true",
    }
    resp = httpx.post(upload_url, headers=headers, content=content)
    resp.raise_for_status()
    return f"{settings.supabase_url}/storage/v1/object/public/{bucket}/{path}"
