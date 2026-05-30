"""
services/email.py — SMTP email delivery service.

What it does:
  `send_email(to, subject, body_text, body_html)` sends an email via the
  configured SMTP server. Works with any SMTP provider — MS365, Gmail,
  Zoho, or a self-hosted relay.

Why it exists at this layer:
  Keeping email delivery in a service (not a router or dependency) makes it
  reusable across routers (prayer approvals, event notifications, etc.) and
  independently replaceable when the Phase 6 connector framework lands.

How it connects:
  - app/config.py supplies smtp_host, smtp_port, smtp_user, smtp_password,
    smtp_from_name.
  - app/routers/prayer_requests.py calls send_prayer_notification() when a
    request is approved.
  - Phase 6 will wrap this in a connector interface so MS365 Graph API or
    Gmail API can be substituted without changing calling code.

Graceful degradation:
  If SMTP is not configured (smtp_host is empty), email is skipped silently
  with a log warning. This ensures a missing config never breaks the approval
  workflow.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


def send_email(
    to: str,
    subject: str,
    body_text: str,
    body_html: str | None = None,
) -> bool:
    """
    Send an email via the configured SMTP server.

    Returns True on success, False if SMTP is not configured or sending fails.
    Never raises — email failure should not break the calling workflow.
    """
    if not settings.smtp_host or not settings.smtp_user:
        logger.warning("SMTP not configured — skipping email to %s", to)
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{settings.smtp_from_name} <{settings.smtp_user}>"
        msg["To"]      = to

        msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_user, to, msg.as_string())

        logger.info("Email sent to %s: %s", to, subject)
        return True

    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to, exc)
        return False


def send_prayer_notification(
    to: str,
    prayer_body: str,
    submitter_name: str | None,
    is_anonymous: bool,
) -> bool:
    """
    Send a prayer chain notification email when a request is approved.

    Called by app/routers/prayer_requests.py after a PATCH approves a request.
    """
    name = "Anonymous" if is_anonymous or not submitter_name else submitter_name

    subject = "New Prayer Request — ChurchOS"

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

    return send_email(to, subject, body_text, body_html)
