"""Unit tests for SessionPostgresRepository."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.session.postgres.models import (
    LlmAppCallSessionModel,
    McpAppCallSessionModel,
    SourceAppCallSessionModel,
)
from identity_auth_server.core.session.postgres.repository import SessionPostgresRepository
from identity_auth_server.core.session.types import (
    SessionLlmAppInput,
    SessionMcpAppInput,
    SessionSourceAppInput,
)


@pytest.fixture
def database_with_session():
    """Provide a mock database/session pair."""
    session = MagicMock()
    session.refresh.side_effect = lambda _: None

    context_manager = MagicMock()
    context_manager.__enter__.return_value = session
    context_manager.__exit__.return_value = None

    database = MagicMock()
    database.session_scope.return_value = context_manager

    return database, session


def _query_mock(result):
    """Create a query MagicMock that returns the supplied result."""
    filter_mock = MagicMock()
    filter_mock.one_or_none.return_value = result

    query_mock = MagicMock()
    query_mock.filter.return_value = filter_mock

    return query_mock


def test_create_source_app_session_persists_and_returns_token(database_with_session):
    """It should persist the session record and return the generated token."""
    database, session = database_with_session

    repository = SessionPostgresRepository(database)
    input_model = SessionSourceAppInput(input="{}")

    token = repository.create_source_app_session(input_model)

    database.session_scope.assert_called_once()
    session.add.assert_called_once()
    session.flush.assert_called_once()
    session.refresh.assert_called_once()

    persisted = session.add.call_args.args[0]
    assert isinstance(persisted, SourceAppCallSessionModel)
    assert persisted.input == "{}"
    assert persisted.token == token
    assert len(token) == 32


def test_create_llm_app_session_requires_existing_source(database_with_session):
    """It should raise if the referenced source session does not exist."""
    database, session = database_with_session
    session.query.side_effect = [_query_mock(None)]

    repository = SessionPostgresRepository(database)

    with pytest.raises(ResourceNotFoundError):
        repository.create_llm_app_session(SessionLlmAppInput(source_app_call_token="missing"))


def test_create_llm_app_session_persists_record(database_with_session):
    """It should persist the LLM session when the source session exists."""
    database, session = database_with_session

    source_session = SourceAppCallSessionModel()
    source_session.id = SimpleNamespace()  # sentinel value

    session.query.side_effect = [_query_mock(source_session)]

    repository = SessionPostgresRepository(database)
    input_model = SessionLlmAppInput(source_app_call_token="source-token")

    token = repository.create_llm_app_session(input_model)

    session.add.assert_called_once()
    persisted = session.add.call_args.args[0]
    assert isinstance(persisted, LlmAppCallSessionModel)
    assert persisted.source_app_call_session_id == source_session.id
    assert persisted.token == token
    assert len(token) == 32


def test_create_mcp_app_session_validates_llm_belongs_to_source(database_with_session):
    """It should raise if the LLM session references a different source session."""
    database, session = database_with_session

    source_session = SourceAppCallSessionModel()
    source_session.id = "source-id"

    other_source_id = "other-source-id"

    llm_session = LlmAppCallSessionModel()
    llm_session.id = "llm-id"
    llm_session.source_app_call_session_id = other_source_id

    session.query.side_effect = [
        _query_mock(source_session),
        _query_mock(llm_session),
    ]

    repository = SessionPostgresRepository(database)

    with pytest.raises(ValueError):
        repository.create_mcp_app_session(
            SessionMcpAppInput(source_app_call_token="source-token", llm_app_call_token="llm-token")
        )


def test_validate_llm_app_call_token_returns_associations(database_with_session):
    """It should return the associated source token when validation succeeds."""
    database, session = database_with_session

    llm_session = LlmAppCallSessionModel()
    llm_session.id = "llm-id"
    llm_session.token = "llm-token"
    llm_session.source_app_call_session_id = "source-id"

    source_session = SourceAppCallSessionModel()
    source_session.id = "source-id"
    source_session.token = "source-token"

    session.query.side_effect = [
        _query_mock(llm_session),
        _query_mock(source_session),
    ]

    repository = SessionPostgresRepository(database)

    result = repository.validate_llm_app_call_token("llm-token")

    assert result.valid is True
    assert result.source_app_call_token == "source-token"


def test_validate_mcp_app_call_token_returns_associations(database_with_session):
    """It should return both associated tokens when validation succeeds."""
    database, session = database_with_session

    mcp_session = McpAppCallSessionModel()
    mcp_session.token = "mcp-token"
    mcp_session.source_app_call_session_id = "source-id"
    mcp_session.llm_app_call_session_id = "llm-id"

    source_session = SourceAppCallSessionModel()
    source_session.id = "source-id"
    source_session.token = "source-token"

    llm_session = LlmAppCallSessionModel()
    llm_session.id = "llm-id"
    llm_session.token = "llm-token"

    session.query.side_effect = [
        _query_mock(mcp_session),
        _query_mock(source_session),
        _query_mock(llm_session),
    ]

    repository = SessionPostgresRepository(database)

    result = repository.validate_mcp_app_call_token("mcp-token")

    assert result.valid is True
    assert result.source_app_call_token == "source-token"
    assert result.llm_app_call_token == "llm-token"
