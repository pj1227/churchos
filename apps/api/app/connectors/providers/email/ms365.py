"""
connectors/providers/email/ms365.py — Microsoft 365 Graph API email connector.

What it does:
  Implements EmailConnector using the MS Graph API sendMail endpoint.
  Authenticates with client credentials flow (OAuth2) — no user sign-in needed.
  Configured via site_config: ms365_tenant_id, ms365_client_id,
  ms365_client_secret, ms365_sender.

Why it exists at this layer:
  Churches on Microsoft 365 can send prayer notifications and future emails
  through their existing M365 tenant — no separate SMTP credentials needed.

How it connects:
  - app/connectors/base/email.py  — implements EmailConnector ABC
  - app/connectors/registry.py    — returned when email_provider = 'ms365'
  - Microsoft identity platform:  https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
  - Microsoft Graph API:          https://graph.microsoft.com/v1.0/users/{sender}/sendMail

Auth flow (client credentials — no user interaction):
  POST /oauth2/v2.0/token with client_id + client_secret + scope=https://graph.microsoft.com/.default
  → access_token used as Bearer on Graph API calls
  Token is NOT cached here — fetched per call. Phase 11 can add a token cache.
"""

import logging

import httpx

from app.connectors.base.email import EmailConnector

logger = logging.getLogger(__name__)

GRAPH_TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
GRAPH_SEND_URL  = "https://graph.microsoft.com/v1.0/users/{sender}/sendMail"


class Ms365EmailConnector(EmailConnector):
    """Email connector backed by Microsoft 365 Graph API."""

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        sender: str,
    ) -> None:
        self.tenant_id     = tenant_id
        self.client_id     = client_id
        self.client_secret = client_secret
        self.sender        = sender

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_access_token(self) -> str:
        """
        Acquire an OAuth2 client-credentials access token from Microsoft.
        Raises on failure — callers catch and return False.
        """
        url  = GRAPH_TOKEN_URL.format(tenant_id=self.tenant_id)
        data = {
            "grant_type":    "client_credentials",
            "client_id":     self.client_id,
            "client_secret": self.client_secret,
            "scope":         "https://graph.microsoft.com/.default",
        }
        resp = httpx.post(url, data=data)
        resp.raise_for_status()
        return resp.json()["access_token"]

    # ------------------------------------------------------------------
    # EmailConnector interface
    # ------------------------------------------------------------------

    def send_email(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: str | None = None,
    ) -> bool:
        """
        Send an email via MS Graph API /sendMail.

        Prefers HTML body when provided; falls back to plain text.
        Returns True on success, False on any failure (never raises).
        """
        try:
            token = self._get_access_token()
            url   = GRAPH_SEND_URL.format(sender=self.sender)

            content_type = "HTML" if body_html else "Text"
            content      = body_html if body_html else body_text

            payload = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": content_type,
                        "content":     content,
                    },
                    "toRecipients": [
                        {"emailAddress": {"address": to}},
                    ],
                },
                "saveToSentItems": False,
            }

            resp = httpx.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            logger.info("MS365 email sent to %s: %s", to, subject)
            return True

        except Exception as exc:
            logger.error("MS365 failed to send email to %s: %s", to, exc)
            return False

    def send_prayer_notification(
        self,
        to: str,
        prayer_body: str,
        submitter_name: str | None,
        is_anonymous: bool,
    ) -> bool:
        """
        Send a prayer chain notification when a request is approved.
        Composes subject/body and delegates to send_email.
        """
        name = "Anonymous" if is_anonymous or not submitter_name else submitter_name

        subject   = "New Prayer Request — ChurchOS"
        body_text = (
            f"A new prayer request has been submitted and approved.\n\n"
            f"From: {name}\n\n"
            f"{prayer_body}\n\n"
            f"—\nChurchOS Prayer Board"
        )
        body_html = f"""
        <p>A new prayer request has been submitted and approved.</p>
        <p><strong>From:</strong> {name}</p>
        <blockquote style="border-left: 3px solid #2d6a4f; padding-left: 1em; color: #333;">
          {prayer_body}
        </blockquote>
        <p style="color: #888; font-size: 0.85em;">— ChurchOS Prayer Board</p>
        """

        return self.send_email(
            to=to,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
        )
