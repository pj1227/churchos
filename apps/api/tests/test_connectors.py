"""
test_connectors.py — TDD tests for the Phase 6 connector framework.

What it covers:
  - EmailConnector ABC enforces the interface contract
  - SmtpEmailConnector delegates to services/email.py
  - Ms365EmailConnector calls the Graph API send-mail endpoint
  - get_email_connector() registry reads site_config and returns
    the right provider (smtp by default, ms365 when configured)

How it connects:
  - app/connectors/base/email.py      — EmailConnector ABC
  - app/connectors/providers/email/smtp.py  — SmtpEmailConnector
  - app/connectors/providers/email/ms365.py — Ms365EmailConnector
  - app/connectors/registry.py        — get_email_connector()
  - app/crud/site_config.py           — registry reads email_provider key
"""

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# EmailConnector ABC
# ---------------------------------------------------------------------------
class TestEmailConnectorABC:
    def test_cannot_instantiate_abc_directly(self):
        """EmailConnector is abstract — cannot be instantiated."""
        from app.connectors.base.email import EmailConnector
        with pytest.raises(TypeError):
            EmailConnector()  # type: ignore

    def test_concrete_subclass_must_implement_send_email(self):
        """A subclass that omits send_email raises TypeError on instantiation."""
        from app.connectors.base.email import EmailConnector

        class Incomplete(EmailConnector):
            pass  # missing send_email and send_prayer_notification

        with pytest.raises(TypeError):
            Incomplete()  # type: ignore

    def test_concrete_subclass_with_all_methods_is_valid(self):
        """A fully implemented subclass can be instantiated."""
        from app.connectors.base.email import EmailConnector

        class Complete(EmailConnector):
            def send_email(self, to, subject, body_text, body_html=None):
                return True
            def send_prayer_notification(self, to, prayer_body, submitter_name, is_anonymous):
                return True

        instance = Complete()
        assert instance is not None


# ---------------------------------------------------------------------------
# SmtpEmailConnector
# ---------------------------------------------------------------------------
class TestSmtpEmailConnector:
    def test_send_email_delegates_to_smtp_service(self):
        """SmtpEmailConnector.send_email calls services.email.send_email."""
        from app.connectors.providers.email.smtp import SmtpEmailConnector
        connector = SmtpEmailConnector()
        with patch("app.connectors.providers.email.smtp.send_email",
                   return_value=True) as mock_send:
            result = connector.send_email(
                to="test@example.com",
                subject="Test",
                body_text="Hello",
            )
        mock_send.assert_called_once_with(
            to="test@example.com",
            subject="Test",
            body_text="Hello",
            body_html=None,
        )
        assert result is True

    def test_send_prayer_notification_delegates(self):
        """SmtpEmailConnector.send_prayer_notification calls the service helper."""
        from app.connectors.providers.email.smtp import SmtpEmailConnector
        connector = SmtpEmailConnector()
        with patch("app.connectors.providers.email.smtp.send_prayer_notification",
                   return_value=True) as mock_notify:
            result = connector.send_prayer_notification(
                to="chain@church.org",
                prayer_body="Please pray.",
                submitter_name="Jane",
                is_anonymous=False,
            )
        mock_notify.assert_called_once()
        assert result is True

    def test_send_email_returns_false_on_failure(self):
        """Returns False when the underlying service fails."""
        from app.connectors.providers.email.smtp import SmtpEmailConnector
        connector = SmtpEmailConnector()
        with patch("app.connectors.providers.email.smtp.send_email",
                   return_value=False):
            result = connector.send_email("x@y.com", "s", "b")
        assert result is False


# ---------------------------------------------------------------------------
# Ms365EmailConnector
# ---------------------------------------------------------------------------
class TestMs365EmailConnector:
    def _make_connector(self):
        from app.connectors.providers.email.ms365 import Ms365EmailConnector
        return Ms365EmailConnector(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret="test-secret",
            sender="noreply@church.org",
        )

    def test_send_email_acquires_token_and_posts_to_graph(self):
        """send_email: gets OAuth token then POSTs to Graph /sendMail."""
        connector = self._make_connector()
        mock_token_resp = MagicMock()
        mock_token_resp.json.return_value = {"access_token": "tok123"}
        mock_token_resp.raise_for_status = MagicMock()

        mock_send_resp = MagicMock()
        mock_send_resp.raise_for_status = MagicMock()

        with patch("app.connectors.providers.email.ms365.httpx.post",
                   side_effect=[mock_token_resp, mock_send_resp]) as mock_post:
            result = connector.send_email(
                to="recipient@example.com",
                subject="Hello",
                body_text="Body text",
            )

        assert mock_post.call_count == 2
        assert result is True

    def test_send_email_returns_false_on_token_failure(self):
        """Returns False when the OAuth token request fails."""
        connector = self._make_connector()
        with patch("app.connectors.providers.email.ms365.httpx.post",
                   side_effect=Exception("network error")):
            result = connector.send_email("x@y.com", "s", "b")
        assert result is False

    def test_send_prayer_notification_calls_send_email(self):
        """send_prayer_notification composes and sends via send_email."""
        connector = self._make_connector()
        with patch.object(connector, "send_email", return_value=True) as mock_send:
            result = connector.send_prayer_notification(
                to="chain@church.org",
                prayer_body="Pray for healing.",
                submitter_name="Jane",
                is_anonymous=False,
            )
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args
        assert "chain@church.org" in call_kwargs[1].values() or "chain@church.org" in call_kwargs[0]
        assert result is True

    def test_anonymous_prayer_notification_hides_name(self):
        """Anonymous submissions show 'Anonymous', not the submitter name."""
        connector = self._make_connector()
        with patch.object(connector, "send_email", return_value=True) as mock_send:
            connector.send_prayer_notification(
                to="chain@church.org",
                prayer_body="Pray for me.",
                submitter_name="Jane",
                is_anonymous=True,
            )
        # body_text should contain "Anonymous", not "Jane"
        call_kwargs = mock_send.call_args
        body_text = call_kwargs[1].get("body_text") or call_kwargs[0][2]
        assert "Anonymous" in body_text
        assert "Jane" not in body_text


# ---------------------------------------------------------------------------
# Registry — get_email_connector()
# ---------------------------------------------------------------------------
class TestEmailConnectorRegistry:
    def test_returns_smtp_connector_by_default(self):
        """When email_provider is not set, returns SmtpEmailConnector."""
        from app.connectors.registry import get_email_connector
        from app.connectors.providers.email.smtp import SmtpEmailConnector
        with patch("app.connectors.registry.get_raw_value", return_value=None):
            connector = get_email_connector()
        assert isinstance(connector, SmtpEmailConnector)

    def test_returns_smtp_connector_when_configured(self):
        """When email_provider = 'smtp', returns SmtpEmailConnector."""
        from app.connectors.registry import get_email_connector
        from app.connectors.providers.email.smtp import SmtpEmailConnector
        with patch("app.connectors.registry.get_raw_value", return_value="smtp"):
            connector = get_email_connector()
        assert isinstance(connector, SmtpEmailConnector)

    def test_returns_ms365_connector_when_configured(self):
        """When email_provider = 'ms365', returns Ms365EmailConnector."""
        from app.connectors.registry import get_email_connector
        from app.connectors.providers.email.ms365 import Ms365EmailConnector

        def mock_config(key):
            return {
                "email_provider":      "ms365",
                "ms365_tenant_id":     "tenant-123",
                "ms365_client_id":     "client-123",
                "ms365_client_secret": "secret-123",
                "ms365_sender":        "noreply@church.org",
            }.get(key)

        with patch("app.connectors.registry.get_raw_value", side_effect=mock_config):
            connector = get_email_connector()
        assert isinstance(connector, Ms365EmailConnector)

    def test_unknown_provider_falls_back_to_smtp(self):
        """Unknown provider string falls back to SMTP rather than raising."""
        from app.connectors.registry import get_email_connector
        from app.connectors.providers.email.smtp import SmtpEmailConnector
        with patch("app.connectors.registry.get_raw_value", return_value="carrier_pigeon"):
            connector = get_email_connector()
        assert isinstance(connector, SmtpEmailConnector)
