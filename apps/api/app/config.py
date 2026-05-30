"""
config.py — Application settings via pydantic-settings.

What it does:
  Reads environment variables (and an optional .env file) into a typed
  Settings object. Every part of the app imports `settings` from here
  rather than calling os.environ directly, keeping env access in one place.

Why it exists at this layer:
  pydantic-settings validates types at startup, so a missing required var
  raises an error immediately rather than failing silently at the call site.

How it connects:
  - app/dependencies/auth.py reads `settings.supabase_jwt_secret` to
    verify incoming JWTs.
  - Future routers will read `settings.supabase_url` / `settings.supabase_service_key`
    to query Supabase directly via the service role.
  - tests/conftest.py sets SUPABASE_JWT_SECRET in os.environ *before*
    this module is imported, so tests never need a real .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Allow extra vars in .env without raising a validation error.
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Supabase
    # ------------------------------------------------------------------
    # JWT secret from Supabase dashboard → Project Settings → API → JWT Secret.
    # Used server-side to verify access tokens (HS256).
    supabase_jwt_secret: str = ""

    # REST API base URL — e.g. https://<project>.supabase.co
    supabase_url: str = ""

    # Service role key — bypasses RLS, used only in server-side code.
    # NEVER exposed to the browser.
    supabase_service_key: str = ""

    # ------------------------------------------------------------------
    # Redis (Upstash) — rate limiting
    # ------------------------------------------------------------------
    # Full Redis URL including scheme, e.g. rediss://...upstash.io:6380
    upstash_redis_url:   str = ""
    # Upstash REST token used as the Redis AUTH password.
    upstash_redis_token: str = ""

    # ------------------------------------------------------------------
    # AI — prayer board moderation
    # ------------------------------------------------------------------
    # xAI (Grok) — primary moderator. Free tier at console.x.ai.
    # Phase 6 adds Gloo AI as primary with Grok as fallback.
    # Phase 9 exposes provider selection via the admin settings UI.
    grok_api_key:      str = ""   # xAI / Grok — active moderator
    anthropic_api_key: str = ""   # reserved for future fallback chain

    # ------------------------------------------------------------------
    # Email (SMTP) — Phase 5b built-in connector
    # ------------------------------------------------------------------
    # Phase 6 will route these through the connector framework.
    # MS365: smtp_host=smtp.office365.com, smtp_port=587
    # Gmail:  smtp_host=smtp.gmail.com,    smtp_port=587
    smtp_host:      str = ""
    smtp_port:      int = 587
    smtp_user:      str = ""   # sender address / login
    smtp_password:  str = ""   # sensitive — never log
    smtp_from_name: str = "ChurchOS"

    # ------------------------------------------------------------------
    # App
    # ------------------------------------------------------------------
    church_slug: str = "libby-naz"
    church_id:   str = ""   # UUID of the default church row in public.churches


settings = Settings()
