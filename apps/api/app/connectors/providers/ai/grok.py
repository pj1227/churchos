"""
connectors/providers/ai/grok.py — Grok (xAI) AI moderation connector.

What it does:
  Implements AiModerationConnector using xAI's Grok API (OpenAI-compatible).
  This is the default/fallback AI provider — free tier available at console.x.ai.

Why it exists at this layer:
  Wraps the xAI API call in the connector interface so it can be swapped for
  Gloo or any future provider without changing callers.

How it connects:
  - app/connectors/base/ai.py     — implements AiModerationConnector ABC
  - app/connectors/registry.py    — returned when ai_provider = 'grok'
                                    or when no provider is configured
  - app/config.py                 — grok_api_key read by the registry

Fail-open policy:
  Any exception (network error, malformed JSON, etc.) returns
  {"approved": True, "reason": None} — a prayer submission must never be
  silently blocked by an AI outage.
"""

import json
import logging

import httpx

from app.connectors.base.ai import AiModerationConnector

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a content moderator for a church community prayer board.
Your job is to determine whether a submitted prayer request is appropriate
for a Christian church community. Appropriate requests include:
- Personal prayer needs (health, family, relationships, spiritual growth)
- Prayers for others (friends, community, world events)
- Expressions of gratitude or praise

Reject submissions that contain:
- Profanity or sexually explicit content
- Hate speech or harassment targeting individuals or groups
- Spam or clearly non-prayer content (advertisements, gibberish, etc.)
- Threats or calls to violence

Respond with ONLY a JSON object in this exact format:
{"approved": true, "reason": null}
OR
{"approved": false, "reason": "Brief explanation of why rejected"}

Do not include any other text. Only the JSON object.
"""


class GrokAiConnector(AiModerationConnector):
    """AI moderation connector backed by xAI Grok (OpenAI-compatible API)."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def moderate(self, text: str) -> dict:
        """
        Send text to xAI Grok for moderation.

        Returns:
            {"approved": True,  "reason": None}   — content is appropriate
            {"approved": False, "reason": "..."}   — content flagged
            {"approved": True,  "reason": None}    — on any error (fail-open)
        """
        if not self._api_key:
            logger.warning("GrokAiConnector: no API key — skipping moderation (approving)")
            return {"approved": True, "reason": None}

        try:
            resp = httpx.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":       "grok-3-mini",
                    "max_tokens":  100,
                    "temperature": 0,
                    "messages": [
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user",   "content": text},
                    ],
                },
                timeout=10.0,
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"].strip()
            result = json.loads(raw)
            return {
                "approved": bool(result.get("approved", True)),
                "reason":   result.get("reason"),
            }

        except Exception as exc:
            logger.warning("GrokAiConnector: moderation failed (approving): %s", exc)
            return {"approved": True, "reason": None}
