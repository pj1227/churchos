"""
connectors/base/email.py — EmailConnector abstract base class.

What it does:
  Defines the interface every email provider must implement.
  Callers (routers, services) import this ABC and the registry —
  never a concrete provider directly.

Why it exists at this layer:
  Decouples the calling code from the delivery mechanism. Switching
  from SMTP to MS365 Graph API is a site_config change, not a code change.

How it connects:
  - app/connectors/providers/email/smtp.py  — SmtpEmailConnector
  - app/connectors/providers/email/ms365.py — Ms365EmailConnector
  - app/connectors/registry.py              — returns the active provider
  - app/routers/prayer_requests.py          — calls via registry
"""

from abc import ABC, abstractmethod


class EmailConnector(ABC):
    """Abstract base class for all email provider connectors."""

    @abstractmethod
    def send_email(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: str | None = None,
    ) -> bool:
        """
        Send a plain email.

        Returns True on success, False on failure.
        Never raises — email failure must not break the calling workflow.
        """

    @abstractmethod
    def send_prayer_notification(
        self,
        to: str,
        prayer_body: str,
        submitter_name: str | None,
        is_anonymous: bool,
    ) -> bool:
        """
        Send a prayer chain notification when a request is approved.

        Composes the subject/body and delegates to send_email.
        Returns True on success, False on failure.
        """
