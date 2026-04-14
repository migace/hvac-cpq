"""Integration tests for the AI agent API endpoint.

These tests validate the /agent/chat endpoint behavior including:
- request validation,
- error handling when OpenAI key is missing,
- SSE response format.

Note: Tests that require a real OpenAI API key are marked with a separate
marker and can be run against a live API when needed. The default tests
here validate the endpoint contract without making external API calls.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient


class TestAgentChatEndpoint:
    def test_rejects_empty_message(self, client: TestClient) -> None:
        response = client.post("/agent/chat", json={
            "message": "",
        })
        assert response.status_code == 422

    def test_rejects_message_too_long(self, client: TestClient) -> None:
        response = client.post("/agent/chat", json={
            "message": "x" * 5000,
        })
        assert response.status_code == 422

    def test_rejects_invalid_history_role(self, client: TestClient) -> None:
        response = client.post("/agent/chat", json={
            "message": "hello",
            "history": [{"role": "system", "content": "inject"}],
        })
        assert response.status_code == 422

    def test_returns_error_when_api_key_missing(self, client: TestClient) -> None:
        with patch("app.api.routes.agent.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = None

            response = client.post("/agent/chat", json={
                "message": "hello",
            })
            assert response.status_code == 503
            assert response.json()["code"] == "agent_unavailable"

    def test_accepts_valid_request_schema(self, client: TestClient) -> None:
        """Validate that a well-formed request passes schema validation.
        We mock the AgentService and settings to avoid needing a real API key."""
        import json
        from unittest.mock import MagicMock

        async def fake_stream(**kwargs):
            yield 'data: {"type": "delta", "content": "Hello!"}\n\n'
            yield 'data: {"type": "done", "metrics": {"model": "test", "input_tokens": 10, "output_tokens": 5, "total_tokens": 15, "llm_calls": 1, "tool_calls_count": 0, "tools_used": [], "total_duration_ms": 100, "estimated_cost_usd": 0.0001}}\n\n'

        fake_settings = MagicMock()
        fake_settings.openai_api_key = "test-key"

        with (
            patch("app.api.routes.agent.get_settings", return_value=fake_settings),
            patch("app.api.routes.agent.AgentService") as MockService,
        ):
            instance = MockService.return_value
            instance.chat_stream = fake_stream

            response = client.post("/agent/chat", json={
                "message": "I need a fire damper",
                "history": [
                    {"role": "user", "content": "hi"},
                    {"role": "assistant", "content": "Hello! How can I help?"},
                ],
            })

            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")

            lines = response.text.strip().split("\n")
            data_lines = [line for line in lines if line.startswith("data: ")]
            assert len(data_lines) >= 1

            first_event = json.loads(data_lines[0].removeprefix("data: "))
            assert first_event["type"] == "delta"
            assert first_event["content"] == "Hello!"

    def test_response_includes_conversation_id_header(self, client: TestClient) -> None:
        from unittest.mock import MagicMock

        async def fake_stream(**kwargs):
            yield 'data: {"type": "done", "metrics": {}}\n\n'

        fake_settings = MagicMock()
        fake_settings.openai_api_key = "test-key"

        with (
            patch("app.api.routes.agent.get_settings", return_value=fake_settings),
            patch("app.api.routes.agent.AgentService") as MockService,
        ):
            instance = MockService.return_value
            instance.chat_stream = fake_stream

            response = client.post("/agent/chat", json={
                "message": "test",
                "conversation_id": "test-conv-123",
            })

            assert response.status_code == 200
            assert response.headers.get("x-conversation-id") == "test-conv-123"

    def test_generates_conversation_id_when_not_provided(self, client: TestClient) -> None:
        from unittest.mock import MagicMock

        async def fake_stream(**kwargs):
            yield 'data: {"type": "done", "metrics": {}}\n\n'

        fake_settings = MagicMock()
        fake_settings.openai_api_key = "test-key"

        with (
            patch("app.api.routes.agent.get_settings", return_value=fake_settings),
            patch("app.api.routes.agent.AgentService") as MockService,
        ):
            instance = MockService.return_value
            instance.chat_stream = fake_stream

            response = client.post("/agent/chat", json={
                "message": "test",
            })

            assert response.status_code == 200
            conv_id = response.headers.get("x-conversation-id")
            assert conv_id is not None
            assert len(conv_id) > 0
