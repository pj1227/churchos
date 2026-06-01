"""
test_ai_connectors.py — TDD tests for the Phase 7 AI connector framework.

What it covers:
  - AiModerationConnector ABC enforces the interface contract
  - GrokAiConnector wraps the xAI Grok API
  - GlooAiConnector wraps the Gloo API with faith-context
  - get_ai_connector() registry reads site_config and returns the right provider
  - Provider chain: Gloo → Grok → fail-open

How it connects:
  - app/connectors/base/ai.py              — AiModerationConnector ABC
  - app/connectors/providers/ai/grok.py    — GrokAiConnector
  - app/connectors/providers/ai/gloo.py    — GlooAiConnector
  - app/connectors/registry.py             — get_ai_connector()
  - app/crud/site_config.py                — registry reads ai_provider + gloo_* keys
"""

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# AiModerationConnector ABC
# ---------------------------------------------------------------------------
class TestAiModerationConnectorABC:
    def test_cannot_instantiate_abc_directly(self):
        """AiModerationConnector is abstract — cannot be instantiated."""
        from app.connectors.base.ai import AiModerationConnector
        with pytest.raises(TypeError):
            AiModerationConnector()  # type: ignore

    def test_concrete_subclass_must_implement_moderate(self):
        """A subclass that omits moderate() raises TypeError on instantiation."""
        from app.connectors.base.ai import AiModerationConnector

        class Incomplete(AiModerationConnector):
            pass  # missing moderate()

        with pytest.raises(TypeError):
            Incomplete()  # type: ignore

    def test_concrete_subclass_with_moderate_is_valid(self):
        """A fully implemented subclass can be instantiated."""
        from app.connectors.base.ai import AiModerationConnector

        class Complete(AiModerationConnector):
            def moderate(self, text: str) -> dict:
                return {"approved": True, "reason": None}

        instance = Complete()
        assert instance is not None

    def test_moderate_return_shape(self):
        """moderate() must return a dict with 'approved' bool and 'reason'."""
        from app.connectors.base.ai import AiModerationConnector

        class Complete(AiModerationConnector):
            def moderate(self, text: str) -> dict:
                return {"approved": True, "reason": None}

        result = Complete().moderate("Please pray for my family.")
        assert isinstance(result, dict)
        assert "approved" in result
        assert "reason" in result
        assert isinstance(result["approved"], bool)


# ---------------------------------------------------------------------------
# GrokAiConnector
# ---------------------------------------------------------------------------
class TestGrokAiConnector:
    def _make_connector(self):
        from app.connectors.providers.ai.grok import GrokAiConnector
        return GrokAiConnector(api_key="test-grok-key")

    def test_moderate_calls_xai_api(self):
        """moderate() POSTs to xAI chat completions and parses JSON response."""
        connector = self._make_connector()
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '{"approved": true, "reason": null}'}}]
        }
        with patch("app.connectors.providers.ai.grok.httpx.post",
                   return_value=mock_resp) as mock_post:
            result = connector.moderate("Please pray for healing.")

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert "api.x.ai" in call_kwargs[0][0]
        assert result == {"approved": True, "reason": None}

    def test_moderate_returns_rejection(self):
        """moderate() correctly returns approved=False with a reason."""
        connector = self._make_connector()
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '{"approved": false, "reason": "Spam content"}'}}]
        }
        with patch("app.connectors.providers.ai.grok.httpx.post",
                   return_value=mock_resp):
            result = connector.moderate("Buy cheap meds now!")

        assert result["approved"] is False
        assert result["reason"] == "Spam content"

    def test_moderate_fails_open_on_api_error(self):
        """API error → fail-open (approved=True, reason=None)."""
        connector = self._make_connector()
        with patch("app.connectors.providers.ai.grok.httpx.post",
                   side_effect=Exception("network error")):
            result = connector.moderate("Please pray for me.")

        assert result == {"approved": True, "reason": None}

    def test_moderate_fails_open_on_malformed_json(self):
        """Malformed JSON from API → fail-open."""
        connector = self._make_connector()
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "not json at all"}}]
        }
        with patch("app.connectors.providers.ai.grok.httpx.post",
                   return_value=mock_resp):
            result = connector.moderate("Pray for me.")

        assert result == {"approved": True, "reason": None}

    def test_moderate_without_api_key_fails_open(self):
        """No API key → fail-open immediately without hitting the network."""
        from app.connectors.providers.ai.grok import GrokAiConnector
        connector = GrokAiConnector(api_key="")
        with patch("app.connectors.providers.ai.grok.httpx.post") as mock_post:
            result = connector.moderate("Pray for me.")

        mock_post.assert_not_called()
        assert result == {"approved": True, "reason": None}


# ---------------------------------------------------------------------------
# GlooAiConnector
# ---------------------------------------------------------------------------
class TestGlooAiConnector:
    def _make_connector(self):
        from app.connectors.providers.ai.gloo import GlooAiConnector
        return GlooAiConnector(
            client_id="test-client-id",
            client_secret="test-client-secret",
            tradition="evangelical",
        )

    def test_moderate_acquires_token_and_calls_gloo(self):
        """moderate() gets an OAuth token then calls the Gloo moderation endpoint."""
        connector = self._make_connector()
        mock_token_resp = MagicMock()
        mock_token_resp.raise_for_status = MagicMock()
        mock_token_resp.json.return_value = {"access_token": "gloo-tok-123"}

        mock_mod_resp = MagicMock()
        mock_mod_resp.raise_for_status = MagicMock()
        mock_mod_resp.json.return_value = {"approved": True, "reason": None}

        with patch("app.connectors.providers.ai.gloo.httpx.post",
                   side_effect=[mock_token_resp, mock_mod_resp]) as mock_post:
            result = connector.moderate("Please pray for my family.")

        assert mock_post.call_count == 2
        assert result == {"approved": True, "reason": None}

    def test_moderate_returns_rejection_from_gloo(self):
        """moderate() propagates approved=False from Gloo."""
        connector = self._make_connector()
        mock_token_resp = MagicMock()
        mock_token_resp.raise_for_status = MagicMock()
        mock_token_resp.json.return_value = {"access_token": "gloo-tok-123"}

        mock_mod_resp = MagicMock()
        mock_mod_resp.raise_for_status = MagicMock()
        mock_mod_resp.json.return_value = {
            "approved": False,
            "reason": "Content inappropriate for faith community",
        }

        with patch("app.connectors.providers.ai.gloo.httpx.post",
                   side_effect=[mock_token_resp, mock_mod_resp]):
            result = connector.moderate("Hateful content here")

        assert result["approved"] is False
        assert "faith" in result["reason"]

    def test_moderate_fails_open_on_token_error(self):
        """Token fetch failure → fail-open."""
        connector = self._make_connector()
        with patch("app.connectors.providers.ai.gloo.httpx.post",
                   side_effect=Exception("auth error")):
            result = connector.moderate("Pray for me.")

        assert result == {"approved": True, "reason": None}

    def test_moderate_fails_open_on_api_error(self):
        """Moderation API failure after token success → fail-open."""
        connector = self._make_connector()
        mock_token_resp = MagicMock()
        mock_token_resp.raise_for_status = MagicMock()
        mock_token_resp.json.return_value = {"access_token": "tok"}

        with patch("app.connectors.providers.ai.gloo.httpx.post",
                   side_effect=[mock_token_resp, Exception("gloo down")]):
            result = connector.moderate("Pray for me.")

        assert result == {"approved": True, "reason": None}

    def test_moderate_without_credentials_fails_open(self):
        """Missing client_id or client_secret → fail-open without network call."""
        from app.connectors.providers.ai.gloo import GlooAiConnector
        connector = GlooAiConnector(client_id="", client_secret="", tradition="evangelical")
        with patch("app.connectors.providers.ai.gloo.httpx.post") as mock_post:
            result = connector.moderate("Pray for me.")

        mock_post.assert_not_called()
        assert result == {"approved": True, "reason": None}

    def test_tradition_sent_in_request(self):
        """The tradition value is included in the moderation request payload."""
        connector = self._make_connector()
        mock_token_resp = MagicMock()
        mock_token_resp.raise_for_status = MagicMock()
        mock_token_resp.json.return_value = {"access_token": "tok"}

        mock_mod_resp = MagicMock()
        mock_mod_resp.raise_for_status = MagicMock()
        mock_mod_resp.json.return_value = {"approved": True, "reason": None}

        with patch("app.connectors.providers.ai.gloo.httpx.post",
                   side_effect=[mock_token_resp, mock_mod_resp]) as mock_post:
            connector.moderate("Pray for me.")

        # Second call is the moderation request — check tradition in payload
        mod_call = mock_post.call_args_list[1]
        payload = mod_call[1].get("json") or (mod_call[0][1] if len(mod_call[0]) > 1 else {})
        assert payload.get("tradition") == "evangelical"


# ---------------------------------------------------------------------------
# Registry — get_ai_connector()
# ---------------------------------------------------------------------------
class TestAiConnectorRegistry:
    def test_returns_grok_connector_by_default(self):
        """When ai_provider is not set, returns GrokAiConnector."""
        from app.connectors.registry import get_ai_connector
        from app.connectors.providers.ai.grok import GrokAiConnector
        with patch("app.connectors.registry.get_raw_value", return_value=None):
            connector = get_ai_connector()
        assert isinstance(connector, GrokAiConnector)

    def test_returns_grok_connector_when_configured(self):
        """When ai_provider = 'grok', returns GrokAiConnector."""
        from app.connectors.registry import get_ai_connector
        from app.connectors.providers.ai.grok import GrokAiConnector

        def mock_config(key):
            return {"ai_provider": "grok"}.get(key)

        with patch("app.connectors.registry.get_raw_value", side_effect=mock_config):
            connector = get_ai_connector()
        assert isinstance(connector, GrokAiConnector)

    def test_returns_gloo_connector_when_configured(self):
        """When ai_provider = 'gloo' with credentials, returns GlooAiConnector."""
        from app.connectors.registry import get_ai_connector
        from app.connectors.providers.ai.gloo import GlooAiConnector

        def mock_config(key):
            return {
                "ai_provider":       "gloo",
                "gloo_client_id":    "client-123",
                "gloo_client_secret":"secret-123",
                "gloo_tradition":    "evangelical",
            }.get(key)

        with patch("app.connectors.registry.get_raw_value", side_effect=mock_config):
            connector = get_ai_connector()
        assert isinstance(connector, GlooAiConnector)

    def test_gloo_falls_back_to_grok_when_credentials_missing(self):
        """ai_provider=gloo but missing credentials → falls back to GrokAiConnector."""
        from app.connectors.registry import get_ai_connector
        from app.connectors.providers.ai.grok import GrokAiConnector

        def mock_config(key):
            return {"ai_provider": "gloo"}.get(key)  # no gloo_* credentials

        with patch("app.connectors.registry.get_raw_value", side_effect=mock_config):
            connector = get_ai_connector()
        assert isinstance(connector, GrokAiConnector)

    def test_unknown_provider_falls_back_to_grok(self):
        """Unknown provider string → falls back to GrokAiConnector."""
        from app.connectors.registry import get_ai_connector
        from app.connectors.providers.ai.grok import GrokAiConnector
        with patch("app.connectors.registry.get_raw_value", return_value="skynet"):
            connector = get_ai_connector()
        assert isinstance(connector, GrokAiConnector)
