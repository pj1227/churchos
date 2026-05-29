"""
dependencies/ai_moderation.py — AI content moderation for prayer submissions.

What it does:
  `moderate_prayer_request(body)` sends the prayer request text to the
  Anthropic Claude API and returns a moderation result:
    {"approved": True,  "reason": None}
    {"approved": False, "reason": "...explanation..."}

  The function is intentionally NOT a FastAPI Depends — it's a plain sync
  function so it's easy to patch in tests:
    patch("app.dependencies.ai_moderation.moderate_prayer_request", ...)

Why it exists at this layer:
  Isolating AI calls here keeps router logic clean and makes this layer
  independently testable. The router calls this, inspects the result,
  and passes ai_approved + ai_reason to the CRUD layer.

How it connects:
  - app/routers/prayer_requests.py calls moderate_prayer_request() on every POST.
  - app/config.py supplies anthropic_api_key.
  - tests/test_prayer_requests.py patches this function.

Graceful degradation:
  If the Anthropic API is unavailable (network error, rate limit, etc.),
  the request is approved with ai_score=None (fail-open).
  This ensures a service disruption doesn't silently block all prayers.

Phase 6 note:
  When Gloo AI integration lands (Phase 6), this will be updated to call
  Gloo first and fall back to Anthropic. The interface stays the same.
"""

import logging

from app.config import settings

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


def moderate_prayer_request(body: str) -> dict:
    """
    Check prayer request body with Claude.

    Returns:
        {"approved": True,  "reason": None}       — content is appropriate
        {"approved": False, "reason": "..."}       — content flagged, include reason
        {"approved": True,  "reason": None}        — on API error (fail-open)

    This function is patchable in tests:
        patch("app.dependencies.ai_moderation.moderate_prayer_request",
              return_value={"approved": True, "reason": None})
    """
    import json

    api_key = settings.anthropic_api_key
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set — skipping AI moderation (approving)")
        return {"approved": True, "reason": None}

    try:
        import httpx

        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-haiku-4-5-20251001",
                "max_tokens": 100,
                "system":     _SYSTEM_PROMPT,
                "messages": [
                    {"role": "user", "content": body},
                ],
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        raw = resp.json()["content"][0]["text"].strip()
        result = json.loads(raw)
        return {
            "approved": bool(result.get("approved", True)),
            "reason":   result.get("reason"),
        }

    except Exception as exc:
        # Fail-open: API unavailable → approve request.
        logger.warning("AI moderation failed (approving): %s", exc)
        return {"approved": True, "reason": None}
