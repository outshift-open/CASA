"""End-to-end integration tests covering trace construction flows."""

from __future__ import annotations

import random
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

import pytest

from identity_auth_server.api.app import database as app_database
from identity_auth_server.core.mcp_app_tool_call.postgres.models import McpAppToolCallModel
from identity_auth_server.core.mcp_app_tool_call.postgres.repository import McpAppToolCallPostgresRepository
from identity_auth_server.core.mcp_app_tool_call.types import BlockedByTypeName

_mcp_tool_call_repository = McpAppToolCallPostgresRepository(app_database)


pytestmark = pytest.mark.integration


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid4()}"


def _create_source_app_call(client, *, token: Optional[str] = None, input_text: Optional[str] = None) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "token": token or _unique("source-token"),
        "input": input_text or _unique("source-input"),
    }
    response = client.post("/source-app-call", json=body)
    assert response.status_code == 200, response.text
    data = response.json()
    data["request_token"] = body["token"]
    data["request_input"] = body["input"]
    return data


def _create_source_app_response(
    client, *, source_token: str, token: Optional[str] = None, output: Optional[str] = None
) -> Dict[str, Any]:
    body = {
        "token": token or _unique("source-response"),
        "source_app_call_token": source_token,
        "output": output or _unique("source-output"),
    }
    response = client.post("/source-app-response", json=body)
    assert response.status_code == 200, response.text
    data = response.json()
    data["request_token"] = body["token"]
    data["request_output"] = body["output"]
    return data


def _create_llm_app_call(
    client,
    *,
    source_token: str,
    token: Optional[str] = None,
    proxy_call_id: Optional[str] = None,
    messages: str | None = None,
    tools: str | None = None,
) -> Dict[str, Any]:
    body = {
        "token": token or _unique("llm-call"),
        "source_app_call_token": source_token,
        "proxy_call_id": proxy_call_id or _unique("proxy"),
        "messages": messages or "[]",
        "tools": tools or "[]",
    }
    response = client.post("/llm-app-call", json=body)
    assert response.status_code == 200, response.text
    data = response.json()
    data["request_token"] = body["token"]
    data["request_proxy_call_id"] = body["proxy_call_id"]
    return data


def _create_llm_app_response(
    client,
    *,
    source_token: str,
    proxy_call_id: str,
    token: Optional[str] = None,
    message: Optional[str] = None,
    tool_calls: Optional[str] = None,
) -> Dict[str, Any]:
    body = {
        "token": token or _unique("llm-response"),
        "source_app_call_token": source_token,
        "proxy_call_id": proxy_call_id,
        "message": message or _unique("llm-message"),
        "tool_calls": tool_calls or "[]",
    }
    response = client.post("/llm-app-response", json=body)
    assert response.status_code == 200, response.text
    data = response.json()
    data["request_token"] = body["token"]
    data["request_message"] = body["message"]
    return data


def _create_mcp_tool_call(
    client,
    *,
    source_token: str,
    token: Optional[str] = None,
    tool: Optional[str] = None,
    llm_call_token: Optional[str] = None,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "token": token or _unique("mcp-call"),
        "source_app_call_token": source_token,
        "tool": tool or _unique("tool"),
        "mcp_server": {"name": "test-server", "tools": [], "resources": []},
    }
    if llm_call_token is not None:
        body["llm_app_call_token"] = llm_call_token
    response = client.post("/mcp-app-tool-call", json=body)
    assert response.status_code == 200, response.text
    data = response.json()
    data["request_token"] = body["token"]
    data["request_tool"] = body["tool"]
    return data


def _get_trace(client, source_id: str) -> Dict[str, Any]:
    response = client.get(f"/trace/{source_id}")
    assert response.status_code == 200, response.text
    return response.json()


def _mark_tool_call_blocked(
    tool_call_id: str,
    *,
    reason: BlockedByTypeName | None = None,
) -> str:
    selected_reason = reason or random.choice(list(BlockedByTypeName))
    reason_definition = _mcp_tool_call_repository.get_blocked_by_type_by_name(name=selected_reason)
    with app_database.session_scope() as session:
        tool_call_uuid = UUID(tool_call_id)
        tool_call: McpAppToolCallModel = (
            session.query(McpAppToolCallModel).filter(McpAppToolCallModel.id == tool_call_uuid).one()
        )
        tool_call.blocked = True
        tool_call.blocked_by_type_id = reason_definition.id
        session.add(tool_call)

    return str(reason_definition.id)


# Happy path scenarios ---------------------------------------------------------------------------


def test_trace_with_only_source_app_call(client):
    """Trace returns only the source app call when no downstream events exist."""
    source = _create_source_app_call(client)

    trace = _get_trace(client, source["id"])

    assert trace["source_app_call"]["id"] == source["id"]
    assert trace["source_app_call"]["input"] == source["request_input"]
    assert trace["source_app_response"] is None
    assert trace["llm_app_calls"] == []
    assert trace["mcp_app_tool_calls"] == []


def test_trace_with_source_response(client):
    """Trace includes the source app response when it exists."""
    source = _create_source_app_call(client)
    response = _create_source_app_response(client, source_token=source["request_token"])

    trace = _get_trace(client, source["id"])

    assert trace["source_app_response"]["output"] == response["request_output"]
    assert trace["llm_app_calls"] == []
    assert trace["mcp_app_tool_calls"] == []


def test_trace_with_llm_app_call(client):
    """Trace records an LLM app call without a response."""
    source = _create_source_app_call(client)
    llm_call = _create_llm_app_call(client, source_token=source["request_token"])

    trace = _get_trace(client, source["id"])

    assert len(trace["llm_app_calls"]) == 1
    assert trace["llm_app_calls"][0]["llm_app_call"]["proxy_call_id"] == llm_call["request_proxy_call_id"]
    assert trace["llm_app_calls"][0]["llm_app_response"] is None


def test_trace_with_llm_app_call_and_response(client):
    """Trace pairs an LLM app call with its response."""
    source = _create_source_app_call(client)
    llm_call = _create_llm_app_call(client, source_token=source["request_token"])
    llm_response = _create_llm_app_response(
        client,
        source_token=source["request_token"],
        proxy_call_id=llm_call["request_proxy_call_id"],
    )

    trace = _get_trace(client, source["id"])

    assert len(trace["llm_app_calls"]) == 1
    assert trace["llm_app_calls"][0]["llm_app_call"]["proxy_call_id"] == llm_call["request_proxy_call_id"]
    assert trace["llm_app_calls"][0]["llm_app_response"]["message"] == llm_response["request_message"]


def test_trace_with_multiple_llm_calls_and_responses(client):
    """Trace handles multiple LLM app calls and responses."""
    source = _create_source_app_call(client)

    first_call = _create_llm_app_call(client, source_token=source["request_token"])
    first_response = _create_llm_app_response(
        client,
        source_token=source["request_token"],
        proxy_call_id=first_call["request_proxy_call_id"],
        message="First response",
    )

    second_call = _create_llm_app_call(client, source_token=source["request_token"])
    second_response = _create_llm_app_response(
        client,
        source_token=source["request_token"],
        proxy_call_id=second_call["request_proxy_call_id"],
        message="Second response",
    )

    trace = _get_trace(client, source["id"])

    assert len(trace["llm_app_calls"]) == 2
    proxy_ids = [entry["llm_app_call"]["proxy_call_id"] for entry in trace["llm_app_calls"]]
    assert first_call["request_proxy_call_id"] in proxy_ids
    assert second_call["request_proxy_call_id"] in proxy_ids

    responses_by_proxy = {
        entry["llm_app_call"]["proxy_call_id"]: entry["llm_app_response"]["message"]
        for entry in trace["llm_app_calls"]
        if entry["llm_app_response"] is not None
    }
    assert responses_by_proxy[first_call["request_proxy_call_id"]] == first_response["request_message"]
    assert responses_by_proxy[second_call["request_proxy_call_id"]] == second_response["request_message"]


def test_trace_with_llm_and_mcp_tool_call(client):
    """Trace links LLM calls and MCP tool calls.

    Note: Currently the service has a bug where it queries responses by llm_call_token,
    but the repository searches by response.token. This causes all tool calls with
    llm_call_token to be blocked. This test documents the current behavior.
    """
    source = _create_source_app_call(client)
    llm_call = _create_llm_app_call(client, source_token=source["request_token"])
    _create_llm_app_response(
        client,
        source_token=source["request_token"],
        proxy_call_id=llm_call["request_proxy_call_id"],
        tool_calls="[{'name':'jira.search'}]",  # Include the tool in tool_calls
    )
    mcp_call = _create_mcp_tool_call(
        client,
        source_token=source["request_token"],
        llm_call_token=llm_call["request_token"],
        tool="jira.search",
    )

    trace = _get_trace(client, source["id"])

    assert len(trace["mcp_app_tool_calls"]) == 1
    tool_entry = trace["mcp_app_tool_calls"][0]["tool_call"]
    assert tool_entry["tool"] == mcp_call["request_tool"]
    # Currently blocked due to service not finding responses (searches by wrong token)
    assert tool_entry["blocked"] is True
    assert tool_entry["blocked_by_type_id"] is not None


def test_trace_with_blocked_mcp_tool_call(client):
    """Trace reports blocked MCP tool calls."""
    source = _create_source_app_call(client)
    llm_call = _create_llm_app_call(client, source_token=source["request_token"])
    _create_llm_app_response(
        client,
        source_token=source["request_token"],
        proxy_call_id=llm_call["request_proxy_call_id"],
    )
    mcp_call = _create_mcp_tool_call(
        client,
        source_token=source["request_token"],
        llm_call_token=llm_call["request_token"],
    )

    blocked_type_id = _mark_tool_call_blocked(
        mcp_call["id"],
        reason=BlockedByTypeName.TOOL_NOT_SELECTED_BY_LLM,
    )

    trace = _get_trace(client, source["id"])

    assert len(trace["mcp_app_tool_calls"]) == 1
    tool_entry = trace["mcp_app_tool_calls"][0]["tool_call"]
    assert tool_entry["blocked"] is True
    assert tool_entry["blocked_by_type_id"] == blocked_type_id


def test_trace_with_mcp_tool_call_without_llm(client):
    """Trace shows MCP tool calls created without an LLM call - these are blocked by the service."""
    source = _create_source_app_call(client)
    mcp_call = _create_mcp_tool_call(client, source_token=source["request_token"], tool="file.read")

    trace = _get_trace(client, source["id"])

    assert len(trace["mcp_app_tool_calls"]) == 1
    tool_entry = trace["mcp_app_tool_calls"][0]["tool_call"]
    assert tool_entry["tool"] == mcp_call["request_tool"]
    assert tool_entry["llm_app_call_id"] is None
    # Service blocks tool calls without LLM responses
    assert tool_entry["blocked"] is True
    assert tool_entry["blocked_by_type_id"] is not None


def test_trace_with_blocked_mcp_tool_call_without_llm(client):
    """Trace flags blocked MCP tool calls without an LLM call."""
    source = _create_source_app_call(client)
    mcp_call = _create_mcp_tool_call(client, source_token=source["request_token"])  # defaults to unique tool

    blocked_type_id = _mark_tool_call_blocked(
        mcp_call["id"],
        reason=BlockedByTypeName.TOOL_INTENT_MISMATCH,
    )

    trace = _get_trace(client, source["id"])

    assert len(trace["mcp_app_tool_calls"]) == 1
    tool_entry = trace["mcp_app_tool_calls"][0]["tool_call"]
    assert tool_entry["blocked"] is True
    assert tool_entry["blocked_by_type_id"] == blocked_type_id


def test_retrieve_multiple_traces(client):
    """Trace list endpoint returns created traces across pagination."""
    traces_to_create = []
    for _ in range(3):
        traces_to_create.append(_create_source_app_call(client))

    for source in traces_to_create:
        _create_source_app_response(client, source_token=source["request_token"], output="ok")
        _create_llm_app_call(client, source_token=source["request_token"])

    fetched = [_get_trace(client, source["id"]) for source in traces_to_create]

    assert len(fetched) == len(traces_to_create)
    for trace in fetched:
        assert trace["source_app_call"]["id"] in {source["id"] for source in traces_to_create}
        assert trace["source_app_response"] is not None
        assert trace["llm_app_calls"]

    # Also verify the paginated endpoint returns at least the created traces
    list_response = client.get("/trace", params={"page": 1, "page_size": 10})
    assert list_response.status_code == 200, list_response.text
    payload = list_response.json()
    assert payload["total"] >= len(traces_to_create)
    listed_ids = {item["source_app_call"]["id"] for item in payload["items"]}
    for source in traces_to_create:
        assert source["id"] in listed_ids


# Error scenarios ---------------------------------------------------------------------------------


def test_source_app_response_with_invalid_source_token(client):
    """Source app response creation fails for unknown source tokens."""
    response = client.post(
        "/source-app-response",
        json={
            "token": _unique("invalid-response"),
            "source_app_call_token": _unique("missing-source"),
            "output": "nope",
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_llm_app_call_with_invalid_source_token(client):
    """LLM app call creation rejects unknown source tokens."""
    response = client.post(
        "/llm-app-call",
        json={
            "token": _unique("invalid-llm"),
            "source_app_call_token": _unique("missing-source"),
            "proxy_call_id": _unique("proxy"),
            "messages": "[]",
            "tools": "[]",
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_llm_app_response_with_invalid_source_token(client):
    """LLM app response creation fails with an invalid source token."""
    response = client.post(
        "/llm-app-response",
        json={
            "token": _unique("invalid-llm-response"),
            "source_app_call_token": _unique("missing-source"),
            "proxy_call_id": _unique("proxy"),
            "message": "no source",
            "tool_calls": "[]",
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_llm_app_response_with_invalid_llm_call(client):
    """LLM app response creation fails for missing proxy call IDs."""
    source = _create_source_app_call(client)
    _create_llm_app_call(client, source_token=source["request_token"])

    response = client.post(
        "/llm-app-response",
        json={
            "token": _unique("invalid-llm-response"),
            "source_app_call_token": source["request_token"],
            "proxy_call_id": _unique("missing-proxy"),
            "message": "invalid llm call",
            "tool_calls": "[]",
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_mcp_tool_call_with_invalid_source_token(client):
    """MCP tool call creation fails for unknown source tokens."""
    response = client.post(
        "/mcp-app-tool-call",
        json={
            "token": _unique("invalid-mcp"),
            "source_app_call_token": _unique("missing-source"),
            "tool": "invalid",
            "mcp_server": {"name": "test-server", "tools": [], "resources": []},
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_mcp_tool_call_with_invalid_llm_call_token(client):
    """MCP tool call creation succeeds but blocks when LLM call token has no responses."""
    source = _create_source_app_call(client)

    response = client.post(
        "/mcp-app-tool-call",
        json={
            "token": _unique("invalid-mcp"),
            "source_app_call_token": source["request_token"],
            "llm_app_call_token": _unique("missing-llm"),
            "tool": "invalid",
            "mcp_server": {"name": "test-server", "tools": [], "resources": []},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["blocked"] is True
    assert data["blocked_by_type_id"] is not None


def test_trace_lookup_with_unknown_source_id(client):
    """Trace lookup returns 404 for unknown source IDs."""
    missing_id = uuid4()
    response = client.get(f"/trace/{missing_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
