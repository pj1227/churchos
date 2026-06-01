"""
connectors/registry.py — Connector factory functions.

What it does:
  Returns the active connector instance for each category by reading
  site_config at call time. Callers never import a provider directly.

Why it exists at this layer:
  Centralises the "which provider is active?" decision in one place.
  Swapping providers requires only a site_config update — no code changes.

How it connects:
  - app/crud/site_config.py          — reads email_provider and credentials
  - app/connectors/base/email.py     — return type for get_email_connector()
  - app/connectors/providers/email/  — concrete implementations
  - app/routers/prayer_requests.py   — calls get_email_connector()

Fallback policy:
  Unknown provider strings and missing config both fall back to SMTP.
  This ensures a misconfigured site_config never breaks email delivery —
  it just falls back to the known-working default.
"""

import logging

from app.connectors.base.email import EmailConnector
from app.connectors.providers.email.smtp import SmtpEmailConnector
from app.connectors.providers.email.ms365 import Ms365EmailConnector
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
