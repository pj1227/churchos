"""
connectors/providers/ai/gloo.py — Gloo AI moderation connector.

What it does:
  Implements AiModerationConnector using the Gloo Faith API — a faith-context
  AI provider designed for Christian ministry use cases.

  Auth: OAuth2 client credentials flow (POST to Gloo token endpoint).
  Moderation: POST to Gloo's content moderation endpoint with the prayer text
  and the church's theological tradition (e.g. "evangelical").

Why it exists at this layer:
  Gloo is the primary/preferred AI provider for ChurchOS — it understands
  faith-specific language and community norms better than general-purpose
  models. Grok serves as the fallback when Gloo is not configured.

How it connects:
  - app/connectors/base/ai.py     — implements AiModerationConnector ABC
  - app/connectors/registry.py    — returned when ai_provider = 'gloo'
                                    with complete gloo_* credentials
  - site_config keys consumed:
      gloo_client_id      — Gloo API client ID
      gloo_client_secret  — Gloo API client secret (stored encrypted)
      gloo_tradition      — e.g. "evangelical", "catholic", "mainline"

Fail-open policy:
  Any exception (token failure, API error) returns
  {"approved": True, "reason": None} so a Gloo outage never silently
  blocks a prayer submission.

Token caching:
  Tokens are fetched per-call for simplicity. A future optimization can
  cache the token with expiry, but correctness comes first.
"""

import logging

import httpx

from app.connectors.base.ai import AiModerationConnector

logger = logging.getLogger(__name__)

_GLOO_TOKEN_URL  = "https://api.gloo.chat/oauth/token"
_GLOO_MOD_URL    = "https://api.gloo.chat/v1/moderate"


class GlooAiConnector(AiModerationConnector):
    """AI moderation connector backed by the Gloo Faith API."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tradition: str = "evangelical",
    ) -> None:
        self._client_id     = client_id
        self._client_secret = client_secret
        self._tradition     = tradition

    def _fetch_token(self) -> str:
        """Fetch an OAuth2 access token from Gloo."""
        resp = httpx.post(
            _GLOO_TOKEN_URL,
            json={
                "client_id":     self._client_id,
                "client_secret": self._client_secret,
                "grant_type":    "client_credentials",
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def moderate(self, text: str) -> dict:
        """
        Send text to Gloo's moderation endpoint.

        Returns:
            {"approved": True,  "reason": None}   — content is appropriate
            {"approved": False, "reason": "..."}   — content flagged
            {"approved": True,  "reason": None}    — on any error (fail-open)
        """
        if not self._client_id or not self._client_secret:
            logger.warning("GlooAiConnector: missing credentials — skipping (approving)")
            return {"approved": True, "reason": None}

        try:
            token = self._fetch_token()
            resp = httpx.post(
                _GLOO_MOD_URL,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type":  "application/json",
                },
                json={
                    "text":      text,
                    "tradition": self._tradition,
                    "context":   "prayer_request",
                },
                timeout=10.0,
            )
            resp.raise_for_status()
            result = resp.json()
            return {
                "approved": bool(result.get("approved", True)),
                "reason":   result.get("reason"),
            }

        except Exception as exc:
            logger.warning("GlooAiConnector: moderation failed (approving): %s", exc)
            return {"approved": True, "reason": None}
