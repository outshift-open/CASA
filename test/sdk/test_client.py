"""Tests for the Identity Auth Server SDK client."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

import httpx
import pytest

from identity_auth_server.sdk import IdentityAuthClient, IdentityAuthSDKError
from identity_auth_server.sdk.types import SourceAppCallInput


def test_create_source_app_call_roundtrip() -> None:
    """The client should serialize payloads and parse models end-to-end."""
    source_app_call_id = uuid4()
    expected_response = {
        "id": str(source_app_call_id),
        "token": "source-token",
        "input": "hello",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/source-app-call"
        assert json.loads(request.content.decode()) == {
            "token": "source-token",
            "input": "hello",
        }
        return httpx.Response(200, json=expected_response)

    transport = httpx.MockTransport(handler)
    payload = SourceAppCallInput(token="source-token", input="hello")

    with IdentityAuthClient("https://example.test", transport=transport) as client:
        result = client.create_source_app_call(payload)

    assert result.id == source_app_call_id
    assert result.token == "source-token"
    assert result.input == "hello"


def test_http_errors_are_wrapped() -> None:
    """HTTP status errors should raise ``IdentityAuthSDKError`` with context."""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "trace not found"})

    transport = httpx.MockTransport(handler)
    trace_id = uuid4()

    with IdentityAuthClient("https://example.test", transport=transport) as client:
        with pytest.raises(IdentityAuthSDKError) as exc_info:
            client.get_trace(trace_id)

    error = exc_info.value
    assert error.status_code == 404
    assert isinstance(error.response, httpx.Response)
    assert "trace not found" in str(error)
    assert error.response.json()["detail"] == "trace not found"
    assert error.response.request is not None
    assert error.response.request.url == httpx.URL(f"https://example.test/trace/{trace_id}")
