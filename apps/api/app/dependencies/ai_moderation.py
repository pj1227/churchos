"""
dependencies/ai_moderation.py — AI content moderation for prayer submissions.

What it does:
  `moderate_prayer_request(body)` calls the active AI moderation connector
  (resolved via the registry at call time) and returns a moderation result:
    {"approved": True,  "reason": None}
    {"approved": False, "reason": "...explanation..."}

  Provider chain (configured via site_config):
    Gloo AI → Grok (xAI) → fail-open

Why it exists at this layer:
  Isolating AI calls here keeps router logic clean and makes this layer
  independently testable and swappable.

How it connects:
  - app/connectors/registry.py          — get_ai_connector() resolves provider
  - app/connectors/base/ai.py           — AiModerationConnector ABC
  - app/connectors/providers/ai/gloo.py — GlooAiConnector (primary)
  - app/connectors/providers/ai/grok.py — GrokAiConnector (fallback)
  - app/routers/prayer_requests.py      — calls moderate_prayer_request()
  - tests/test_prayer_requests.py       — patches this function

Graceful degradation:
  If all providers are unavailable, the connector chain fails-open and
  approves the request. A Redis or AI outage must never silently block
  someone from submitting a prayer request.

Patchable in tests:
    patch("app.dependencies.ai_moderation.moderate_prayer_request",
          return_value={"approved": True, "reason": None})
"""

from app.connectors.registry import get_ai_connector


def moderate_prayer_request(body: str) -> dict:
    """
    Check prayer request body using the configured AI provider.

    Returns:
        {"approved": True,  "reason": None}   — content is appropriate
        {"approved": False, "reason": "..."}   — content flagged
        {"approved": True,  "reason": None}    — on any error (fail-open)
    """
    connector = get_ai_connector()
    return connector.moderate(body)
