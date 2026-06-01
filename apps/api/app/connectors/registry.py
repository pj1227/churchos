"""
connectors/registry.py — Connector factory functions.

What it does:
  Returns the active connector instance for each category by reading
  site_config at call time. Callers never import a provider directly.

Why it exists at this layer:
  Centralises the "which provider is active?" decision in one place.
  Swapping providers requires only a site_config update — no code changes.

How it connects:
  - app/crud/site_config.py           — reads provider keys and credentials
  - app/connectors/base/email.py      — return type for get_email_connector()
  - app/connectors/base/ai.py         — return type for get_ai_connector()
  - app/connectors/providers/email/   — concrete email implementations
  - app/connectors/providers/ai/      — concrete AI implementations
  - app/routers/prayer_requests.py    — calls get_email_connector()
  - app/dependencies/ai_moderation.py — calls get_ai_connector()

Fallback policy (email):
  Unknown provider strings and missing config both fall back to SMTP.
  This ensures a misconfigured site_config never breaks email delivery —
  it just falls back to the known-working default.

Fallback policy (AI moderation):
  Provider chain: Gloo → Grok → fail-open.
  - ai_provider = 'gloo' but incomplete credentials → GrokAiConnector
  - ai_provider unknown or not set → GrokAiConnector
  - GrokAiConnector with no api_key → fail-open within the connector
"""

import logging

from app.connectors.base.email import EmailConnector
from app.connectors.base.ai import AiModerationConnector
from app.connectors.providers.email.smtp import SmtpEmailConnector
from app.connectors.providers.email.ms365 import Ms365EmailConnector
from app.connectors.providers.ai.grok import GrokAiConnector
from app.connectors.providers.ai.gloo import GlooAiConnector
from app.crud.site_config import get_raw_value

logger = logging.getLogger(__name__)


def get_email_connector() -> EmailConnector:
    """
    Return the active email connector based on site_config.

    Reads `email_provider` from site_config:
      - 'smtp'  (or not set) → SmtpEmailConnector
      - 'ms365'              → Ms365EmailConnector (requires ms365_* keys)
      - anything else        → SmtpEmailConnector (fallback with warning)
    """
    provider = get_raw_value("email_provider") or "smtp"

    if provider == "ms365":
        tenant_id     = get_raw_value("ms365_tenant_id")     or ""
        client_id     = get_raw_value("ms365_client_id")     or ""
        client_secret = get_raw_value("ms365_client_secret") or ""
        sender        = get_raw_value("ms365_sender")        or ""

        if not all([tenant_id, client_id, client_secret, sender]):
            logger.warning(
                "email_provider=ms365 but MS365 credentials are incomplete "
                "— falling back to SMTP"
            )
            return SmtpEmailConnector()

        return Ms365EmailConnector(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            sender=sender,
        )

    if provider != "smtp":
        logger.warning(
            "Unknown email_provider '%s' — falling back to SMTP", provider
        )

    return SmtpEmailConnector()


def get_ai_connector() -> AiModerationConnector:
    """
    Return the active AI moderation connector based on site_config.

    Provider chain:
      1. ai_provider = 'gloo' with complete credentials → GlooAiConnector
      2. ai_provider = 'gloo' but missing credentials  → GrokAiConnector (warn)
      3. ai_provider = 'grok' or not set               → GrokAiConnector
      4. unknown provider string                        → GrokAiConnector (warn)

    GrokAiConnector itself fails-open if grok_api_key is not set, so the
    chain always resolves to approve-if-uncertain.
    """
    provider = get_raw_value("ai_provider") or "grok"

    if provider == "gloo":
        client_id     = get_raw_value("gloo_client_id")     or ""
        client_secret = get_raw_value("gloo_client_secret") or ""
        tradition     = get_raw_value("gloo_tradition")     or "evangelical"

        if not client_id or not client_secret:
            logger.warning(
                "ai_provider=gloo but Gloo credentials are incomplete "
                "— falling back to Grok"
            )
            from app.config import settings
            return GrokAiConnector(api_key=settings.grok_api_key or "")

        return GlooAiConnector(
            client_id=client_id,
            client_secret=client_secret,
            tradition=tradition,
        )

    if provider != "grok":
        logger.warning(
            "Unknown ai_provider '%s' — falling back to Grok", provider
        )

    from app.config import settings
    return GrokAiConnector(api_key=settings.grok_api_key or "")
