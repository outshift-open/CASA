"""End-to-end integration tests for the session routes."""

from __future__ import annotations

from typing import Dict
from uuid import uuid4

import pytest

from identity_auth_server.api.app import database as app_database
from identity_auth_server.core.session.postgres.models import (
    LlmAppCallSessionModel,
    McpAppCallSessionModel,
    SourceAppCallSessionModel,
)

pytestmark = pytest.mark.integration


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid4()}"


def _create_source_session(client, *, input_text: str | None = None) -> Dict[str, str]:
    payload = {"input": input_text or _unique("source-input")}
    response = client.post("/session/get_source_app_call_token", json=payload)
    assert response.status_code == 200, response.text
    token = response.json()
    assert isinstance(token, str)
    return {"token": token, "input": payload["input"]}


def _create_llm_session(client, *, source_token: str) -> Dict[str, str]:
    payload = {"source_app_call_token": source_token}
    response = client.post("/session/get_llm_app_call_token", json=payload)
    assert response.status_code == 200, response.text
    token = response.json()
    assert isinstance(token, str)
    return {"token": token, "source_token": source_token}


def _create_mcp_session(client, *, source_token: str, llm_token: str) -> Dict[str, str]:
    payload = {"source_app_call_token": source_token, "llm_app_call_token": llm_token}
    response = client.post("/session/get_mcp_app_call_token", json=payload)
    assert response.status_code == 200, response.text
    token = response.json()
    assert isinstance(token, str)
    return {"token": token, "source_token": source_token, "llm_token": llm_token}


def test_create_source_app_session_persists_record(client):
    """Creating a source session should store the payload and return a token."""
    created = _create_source_session(client)

    with app_database.session_scope() as session:
        record = (
            session.query(SourceAppCallSessionModel).filter(SourceAppCallSessionModel.token == created["token"]).one()
        )

        assert record.input == created["input"]
        assert len(created["token"]) == 32


def test_create_llm_app_session_links_to_source(client):
    """Creating an LLM session should reference an existing source session."""
    source = _create_source_session(client)
    llm = _create_llm_session(client, source_token=source["token"])

    with app_database.session_scope() as session:
        llm_record = session.query(LlmAppCallSessionModel).filter(LlmAppCallSessionModel.token == llm["token"]).one()
        source_record = (
            session.query(SourceAppCallSessionModel).filter(SourceAppCallSessionModel.token == source["token"]).one()
        )

        assert llm_record.source_app_call_session_id == source_record.id


def test_create_mcp_app_session_links_to_source_and_llm(client):
    """Creating an MCP session should reference both the source and LLM sessions."""
    source = _create_source_session(client)
    llm = _create_llm_session(client, source_token=source["token"])
    mcp = _create_mcp_session(client, source_token=source["token"], llm_token=llm["token"])

    with app_database.session_scope() as session:
        mcp_record = session.query(McpAppCallSessionModel).filter(McpAppCallSessionModel.token == mcp["token"]).one()
        llm_record = session.query(LlmAppCallSessionModel).filter(LlmAppCallSessionModel.token == llm["token"]).one()
        source_record = (
            session.query(SourceAppCallSessionModel).filter(SourceAppCallSessionModel.token == source["token"]).one()
        )

        assert mcp_record.llm_app_call_session_id == llm_record.id
        assert mcp_record.source_app_call_session_id == source_record.id


def test_validate_source_app_call_token_returns_valid(client):
    """Validating an existing source token should return a positive response."""
    source = _create_source_session(client)

    response = client.post(
        "/session/validate_source_app_call_token",
        json={"source_app_call_token": source["token"]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload == {"valid": True}


def test_validate_llm_app_call_token_returns_associations(client):
    """Validating an LLM token should include the parent source token."""
    source = _create_source_session(client)
    llm = _create_llm_session(client, source_token=source["token"])

    response = client.post(
        "/session/validate_llm_app_call_token",
        json={"llm_app_call_token": llm["token"]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["valid"] is True
    assert payload["source_app_call_token"] == source["token"]


def test_validate_mcp_app_call_token_returns_associations(client):
    """Validating an MCP token should include both source and LLM associations."""
    source = _create_source_session(client)
    llm = _create_llm_session(client, source_token=source["token"])
    mcp = _create_mcp_session(client, source_token=source["token"], llm_token=llm["token"])

    response = client.post(
        "/session/validate_mcp_app_call_token",
        json={"mcp_app_call_token": mcp["token"]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["valid"] is True
    assert payload["source_app_call_token"] == source["token"]
    assert payload["llm_app_call_token"] == llm["token"]


def test_create_llm_app_session_requires_existing_source(client):
    """Creating an LLM session with an unknown source token should fail."""
    response = client.post(
        "/session/get_llm_app_call_token",
        json={"source_app_call_token": _unique("missing-source")},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_mcp_app_session_requires_existing_source(client):
    """Creating an MCP session with an unknown source token should fail."""
    response = client.post(
        "/session/get_mcp_app_call_token",
        json={
            "source_app_call_token": _unique("missing-source"),
            "llm_app_call_token": _unique("missing-llm"),
        },
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_mcp_app_session_requires_existing_llm(client):
    """Creating an MCP session with an unknown LLM token should fail."""
    source = _create_source_session(client)

    response = client.post(
        "/session/get_mcp_app_call_token",
        json={
            "source_app_call_token": source["token"],
            "llm_app_call_token": _unique("missing-llm"),
        },
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_mcp_app_session_validates_llm_matches_source(client):
    """Creating an MCP session should ensure the LLM session belongs to the source session."""
    first_source = _create_source_session(client)
    second_source = _create_source_session(client)

    _create_llm_session(client, source_token=first_source["token"])
    llm_second = _create_llm_session(client, source_token=second_source["token"])

    response = client.post(
        "/session/get_mcp_app_call_token",
        json={
            "source_app_call_token": first_source["token"],
            "llm_app_call_token": llm_second["token"],
        },
    )

    assert response.status_code == 400
    assert "does not belong" in response.json()["detail"].lower()


def test_validate_source_app_call_token_missing_returns_404(client):
    """Validating an unknown source token should raise a 404."""
    response = client.post(
        "/session/validate_source_app_call_token",
        json={"source_app_call_token": _unique("missing-source")},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_validate_llm_app_call_token_missing_returns_404(client):
    """Validating an unknown LLM token should raise a 404."""
    response = client.post(
        "/session/validate_llm_app_call_token",
        json={"llm_app_call_token": _unique("missing-llm")},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_validate_mcp_app_call_token_missing_returns_404(client):
    """Validating an unknown MCP token should raise a 404."""
    response = client.post(
        "/session/validate_mcp_app_call_token",
        json={"mcp_app_call_token": _unique("missing-mcp")},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_multiple_llm_sessions_can_share_source(client):
    """A single source session may spawn multiple independent LLM sessions."""
    source = _create_source_session(client)
    llm_one = _create_llm_session(client, source_token=source["token"])
    llm_two = _create_llm_session(client, source_token=source["token"])

    assert llm_one["token"] != llm_two["token"]

    with app_database.session_scope() as session:
        source_record = (
            session.query(SourceAppCallSessionModel).filter(SourceAppCallSessionModel.token == source["token"]).one()
        )
        llm_records = (
            session.query(LlmAppCallSessionModel)
            .filter(LlmAppCallSessionModel.source_app_call_session_id == source_record.id)
            .all()
        )

        tokens = {record.token for record in llm_records}
        assert tokens >= {llm_one["token"], llm_two["token"]}


def test_multiple_mcp_sessions_can_share_source_and_llm(client):
    """An LLM session may produce multiple MCP sessions tied to the same relationships."""
    source = _create_source_session(client)
    llm = _create_llm_session(client, source_token=source["token"])
    mcp_one = _create_mcp_session(client, source_token=source["token"], llm_token=llm["token"])
    mcp_two = _create_mcp_session(client, source_token=source["token"], llm_token=llm["token"])

    assert mcp_one["token"] != mcp_two["token"]

    with app_database.session_scope() as session:
        llm_record = session.query(LlmAppCallSessionModel).filter(LlmAppCallSessionModel.token == llm["token"]).one()
        mcp_records = (
            session.query(McpAppCallSessionModel)
            .filter(McpAppCallSessionModel.llm_app_call_session_id == llm_record.id)
            .all()
        )

        tokens = {record.token for record in mcp_records}
        assert tokens >= {mcp_one["token"], mcp_two["token"]}
