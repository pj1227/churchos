"""
connectors/providers/email/smtp.py — SMTP email connector.

What it does:
  Implements EmailConnector using the existing services/email.py SMTP helpers.
  This is the default provider — works with any SMTP server (MS365, Gmail,
  Zoho, self-hosted relay) via env vars SMTP_HOST / SMTP_USER / etc.

Why it exists at this layer:
  Wraps the Phase 5b SMTP service in the connector interface so it can be
  swapped for MS365 Graph API or any future provider without changing callers.

How it connects:
  - app/connectors/base/email.py    — implements EmailConnector ABC
  - app/services/email.py           — delegates to send_email() and
                                      send_prayer_notification() helpers
  - app/connectors/registry.py      — returned when email_provider = 'smtp'
                                      or when no provider is configured
"""

from app.connectors.base.email import EmailConnector
from app.services.email import (
    send_email,
    send_prayer_notification,
)


class SmtpEmailConnector(EmailConnector):
    """Email connector backed by the configured SMTP server."""

    def send_email(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: str | None = None,
    ) -> bool:
        return send_email(
            to=to,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
        )

    def send_prayer_notification(
        self,
        to: str,
        prayer_body: str,
        submitter_name: str | None,
        is_anonymous: bool,
    ) -> bool:
        return send_prayer_notification(
            to=to,
            prayer_body=prayer_body,
            submitter_name=submitter_name,
            is_anonymous=is_anonymous,
        )
