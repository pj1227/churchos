"""
connectors/base/ai.py — AiModerationConnector abstract base class.

What it does:
  Defines the interface every AI moderation provider must implement.
  Callers import this ABC and the registry — never a concrete provider directly.

Why it exists at this layer:
  Decouples prayer-request moderation from any specific AI provider.
  Switching from Grok to Gloo (or any future provider) is a site_config
  change, not a code change.

How it connects:
  - app/connectors/providers/ai/grok.py  — GrokAiConnector
  - app/connectors/providers/ai/gloo.py  — GlooAiConnector
  - app/connectors/registry.py           — returns the active provider
  - app/dependencies/ai_moderation.py    — calls via registry

Contract:
  moderate(text) must NEVER raise — any error should return fail-open
  {"approved": True, "reason": None} so a provider outage never silently
  blocks someone from submitting a prayer request.
"""

from abc import ABC, abstractmethod


class AiModerationConnector(ABC):
    """Abstract base class for all AI moderation provider connectors."""

    @abstractmethod
    def moderate(self, text: str) -> dict:
        """
        Evaluate text for appropriateness in a church community context.

        Returns:
            {"approved": True,  "reason": None}   — content is appropriate
            {"approved": False, "reason": "..."}   — content flagged

        Must never raise. On any error, implementations must fail-open:
            {"approved": True, "reason": None}
        """
