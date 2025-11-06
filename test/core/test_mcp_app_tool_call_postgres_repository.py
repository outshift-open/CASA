"""Unit tests for McpAppToolCallPostgresRepository."""

import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.mcp_app_tool_call.postgres.repository import McpAppToolCallPostgresRepository
from identity_auth_server.core.mcp_app_tool_call.types import McpAppToolCallInput


def _mock_database_with_session():
    session = MagicMock()
    session.refresh.side_effect = lambda _: None

    context_manager = MagicMock()
    context_manager.__enter__.return_value = session
    context_manager.__exit__.return_value = None

    database = MagicMock()
    database.session_scope.return_value = context_manager

    return database, session, context_manager


@pytest.fixture
def database_with_session():
    """Return a mock PostgresDB and its session."""
    return _mock_database_with_session()


def _build_simple_namespace(**kwargs):
    """Create a SimpleNamespace with an id when missing."""
    if "id" not in kwargs:
        kwargs["id"] = uuid4()
    return SimpleNamespace(**kwargs)


def test_create_mcp_app_tool_call_persists_record(monkeypatch, database_with_session):
    """It should persist a tool call resolving all foreign keys via tokens."""
    expected_id = uuid4()
    expected_created_at = datetime.datetime(2025, 1, 3, tzinfo=datetime.timezone.utc)

    database, session, context_manager = database_with_session

    source_token = "source-token"
    llm_call_token = "llm-call-token"

    source_app_call = _build_simple_namespace(token=source_token)
    llm_app_call = _build_simple_namespace(token=llm_call_token)
    llm_app_response = _build_simple_namespace(llm_app_call_id=llm_app_call.id)

    source_query = MagicMock()
    llm_call_query = MagicMock()
    llm_response_query = MagicMock()

    session.query.side_effect = [source_query, llm_call_query, llm_response_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source_app_call

    llm_call_filtered = MagicMock()
    llm_call_query.filter.return_value = llm_call_filtered
    llm_call_filtered.one_or_none.return_value = llm_app_call

    llm_response_filtered = MagicMock()
    llm_response_query.filter.return_value = llm_response_filtered
    llm_response_ordered = MagicMock()
    llm_response_filtered.order_by.return_value = llm_response_ordered
    llm_response_ordered.first.return_value = llm_app_response

    monkeypatch.setattr(
        "identity_auth_server.core.mcp_app_tool_call.postgres.repository.uuid4",
        lambda: expected_id,
    )

    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return expected_created_at

    monkeypatch.setattr(
        "identity_auth_server.core.mcp_app_tool_call.postgres.repository.datetime.datetime",
        FixedDateTime,
    )

    repository = McpAppToolCallPostgresRepository(database)

    input_model = McpAppToolCallInput(
        token="tool-call-token",
        source_app_call_token=source_token,
        llm_app_call_token=llm_call_token,
        tool="{}",
        mcp_server={"name": "test-server", "tools": [], "resources": []},
    )

    result = repository.create(input_model)

    database.session_scope.assert_called_once()
    context_manager.__enter__.assert_called_once()
    session.add.assert_called_once()
    session.flush.assert_called_once()
    session.refresh.assert_called_once()

    assert result.id == expected_id
    assert isinstance(result.id, UUID)
    assert result.source_app_call_id == source_app_call.id
    # Repository no longer queries for LLM calls/responses - that logic is in the service layer
    assert result.llm_app_call_id is None
    assert result.llm_app_response_id is None
    assert result.token == "tool-call-token"
    assert result.tool == "{}"
    assert result.blocked is False
    assert result.blocked_by_type_id is None
    assert result.created_at == expected_created_at


def test_create_tool_call_raises_when_source_missing(database_with_session):
    """It should raise ValueError when the source token cannot be resolved."""
    database, session, context_manager = database_with_session

    source_query = MagicMock()
    session.query.side_effect = [source_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = None

    repository = McpAppToolCallPostgresRepository(database)

    input_model = McpAppToolCallInput(
        token="tool-call-token",
        source_app_call_token="missing-source",
        llm_app_call_token="llm-token",
        tool="{}",
        mcp_server={"name": "test-server", "tools": [], "resources": []},
    )

    with pytest.raises(ResourceNotFoundError, match="Source app call not found"):
        repository.create(input_model)

    database.session_scope.assert_called_once()
    context_manager.__enter__.assert_called_once()
    session.add.assert_not_called()
    session.flush.assert_not_called()
    session.refresh.assert_not_called()


def test_create_tool_call_raises_when_llm_call_missing(database_with_session):
    """It should succeed even when LLM call token is provided but not validated (validation is in service layer)."""
    source_app_call = _build_simple_namespace(token="source-token")

    database, session, context_manager = database_with_session

    source_query = MagicMock()

    session.query.side_effect = [source_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source_app_call

    repository = McpAppToolCallPostgresRepository(database)

    input_model = McpAppToolCallInput(
        token="tool-call-token",
        source_app_call_token=source_app_call.token,
        llm_app_call_token="missing-llm",
        tool="{}",
        mcp_server={"name": "test-server", "tools": [], "resources": []},
    )

    # Repository no longer validates LLM calls - service layer handles that
    result = repository.create(input_model)

    database.session_scope.assert_called_once()
    context_manager.__enter__.assert_called_once()
    session.add.assert_called_once()
    session.flush.assert_called_once()
    session.refresh.assert_called_once()

    assert result.source_app_call_id == source_app_call.id
    assert result.llm_app_call_id is None
    assert result.token == "tool-call-token"


def test_create_tool_call_succeeds_when_llm_response_missing(monkeypatch, database_with_session):
    """It should persist even when the linked LLM call has no response yet."""
    expected_id = uuid4()
    expected_created_at = datetime.datetime(2025, 1, 4, tzinfo=datetime.timezone.utc)

    database, session, context_manager = database_with_session

    source_app_call = _build_simple_namespace(token="source-token")
    llm_app_call = _build_simple_namespace(token="llm-token")

    source_query = MagicMock()
    llm_call_query = MagicMock()
    llm_response_query = MagicMock()

    session.query.side_effect = [source_query, llm_call_query, llm_response_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source_app_call

    llm_call_filtered = MagicMock()
    llm_call_query.filter.return_value = llm_call_filtered
    llm_call_filtered.one_or_none.return_value = llm_app_call

    llm_response_filtered = MagicMock()
    llm_response_query.filter.return_value = llm_response_filtered
    llm_response_ordered = MagicMock()
    llm_response_filtered.order_by.return_value = llm_response_ordered
    llm_response_ordered.first.return_value = None

    monkeypatch.setattr(
        "identity_auth_server.core.mcp_app_tool_call.postgres.repository.uuid4",
        lambda: expected_id,
    )

    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return expected_created_at

    monkeypatch.setattr(
        "identity_auth_server.core.mcp_app_tool_call.postgres.repository.datetime.datetime",
        FixedDateTime,
    )

    repository = McpAppToolCallPostgresRepository(database)

    input_model = McpAppToolCallInput(
        token="tool-call-token",
        source_app_call_token=source_app_call.token,
        llm_app_call_token=llm_app_call.token,
        tool="{}",
        mcp_server={"name": "test-server", "tools": [], "resources": []},
    )

    result = repository.create(input_model)

    database.session_scope.assert_called_once()
    context_manager.__enter__.assert_called_once()
    session.add.assert_called_once()
    session.flush.assert_called_once()
    session.refresh.assert_called_once()

    # Repository no longer queries for LLM calls/responses
    assert result.llm_app_call_id is None
    assert result.llm_app_response_id is None
    assert result.created_at == expected_created_at


def test_create_tool_call_without_llm_call_token(monkeypatch, database_with_session):
    """It should allow creating a tool call without an LLM call reference."""
    expected_id = uuid4()
    expected_created_at = datetime.datetime(2025, 1, 5, tzinfo=datetime.timezone.utc)

    database, session, context_manager = database_with_session

    source_app_call = _build_simple_namespace(token="source-token")

    source_query = MagicMock()
    session.query.side_effect = [source_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source_app_call

    monkeypatch.setattr(
        "identity_auth_server.core.mcp_app_tool_call.postgres.repository.uuid4",
        lambda: expected_id,
    )

    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return expected_created_at

    monkeypatch.setattr(
        "identity_auth_server.core.mcp_app_tool_call.postgres.repository.datetime.datetime",
        FixedDateTime,
    )

    repository = McpAppToolCallPostgresRepository(database)

    input_model = McpAppToolCallInput(
        token="tool-call-token",
        source_app_call_token=source_app_call.token,
        llm_app_call_token=None,
        tool="{}",
        mcp_server={"name": "test-server", "tools": [], "resources": []},
    )

    result = repository.create(input_model)

    database.session_scope.assert_called_once()
    context_manager.__enter__.assert_called_once()
    session.add.assert_called_once()
    session.flush.assert_called_once()
    session.refresh.assert_called_once()

    assert result.llm_app_call_id is None
    assert result.llm_app_response_id is None
    assert result.source_app_call_id == source_app_call.id
    assert result.created_at == expected_created_at
