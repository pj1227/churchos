"""
dependencies/ai_moderation.py — AI content moderation for prayer submissions.

What it does:
  `moderate_prayer_request(body)` sends the prayer request text to the
  xAI Grok API and returns a moderation result:
    {"approved": True,  "reason": None}
    {"approved": False, "reason": "...explanation..."}

  xAI's API is OpenAI-compatible, so the request format is standard chat
  completions. Free tier available at console.x.ai.

  The function is intentionally NOT a FastAPI Depends — it's a plain sync
  function so it's easy to patch in tests:
    patch("app.dependencies.ai_moderation.moderate_prayer_request", ...)

Why it exists at this layer:
  Isolating AI calls here keeps router logic clean and makes this layer
  independently testable and swappable.

How it connects:
  - app/routers/prayer_requests.py calls moderate_prayer_request() on every POST.
  - app/config.py supplies grok_api_key.
  - tests/test_prayer_requests.py patches this function.

Graceful degradation:
  If GROK_API_KEY is not set or the API is unavailable, the request is
  approved (fail-open). A Redis or AI outage should never silently block
  someone from submitting a prayer request.

Phase 6 note:
  When Gloo AI integration lands, this becomes the fallback in a provider
  chain: Gloo → Grok → fail-open. The interface (`moderate_prayer_request`)
  stays the same — only the internals change.

Phase 9 note:
  Provider selection and API keys will be configurable per-deployment via
  the admin settings UI, stored encrypted in site_config.
"""

import json
import logging

import httpx

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
    Check prayer request body with Grok (xAI).

    Returns:
        {"approved": True,  "reason": None}   — content is appropriate
        {"approved": False, "reason": "..."}   — content flagged
        {"approved": True,  "reason": None}    — on missing key or API error (fail-open)

    Patchable in tests:
        patch("app.dependencies.ai_moderation.moderate_prayer_request",
              return_value={"approved": True, "reason": None})
    """
    api_key = settings.grok_api_key
    if not api_key:
        logger.warning("GROK_API_KEY not set — skipping AI moderation (approving)")
        return {"approved": True, "reason": None}

    try:
        resp = httpx.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            json={
                "model":       "grok-3-mini",
                "max_tokens":  100,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user",   "content": body},
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
        # Fail-open: API unavailable → approve request.
        logger.warning("AI moderation failed (approving): %s", exc)
        return {"approved": True, "reason": None}
