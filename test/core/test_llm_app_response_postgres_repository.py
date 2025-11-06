"""Unit tests for LlmAppResponsePostgresRepository."""

import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.llm_app_response.postgres.repository import LlmAppResponsePostgresRepository
from identity_auth_server.core.llm_app_response.types import LlmAppResponseInput


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
    """Provide a mock PostgresDB and associated session."""
    return _mock_database_with_session()


def test_create_llm_app_response_persists_record(monkeypatch, database_with_session):
    """It should persist an LLM response linked to the latest LLM app call."""
    expected_id = uuid4()
    expected_created_at = datetime.datetime(2025, 1, 2, tzinfo=datetime.timezone.utc)

    database, session, context_manager = database_with_session

    source_token = "source-token"
    proxy_call_id = "proxy-123"
    source_app_call = SimpleNamespace(id=uuid4(), token=source_token)
    llm_app_call = SimpleNamespace(id=uuid4(), source_app_call_id=source_app_call.id, proxy_call_id=proxy_call_id)

    source_query = MagicMock()
    llm_query = MagicMock()

    session.query.side_effect = [source_query, llm_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source_app_call

    llm_filtered = MagicMock()
    llm_query.filter.return_value = llm_filtered
    llm_filtered.one_or_none.return_value = llm_app_call

    monkeypatch.setattr(
        "identity_auth_server.core.llm_app_response.postgres.repository.uuid4",
        lambda: expected_id,
    )

    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return expected_created_at

    monkeypatch.setattr(
        "identity_auth_server.core.llm_app_response.postgres.repository.datetime.datetime",
        FixedDateTime,
    )

    repository = LlmAppResponsePostgresRepository(database)

    input_model = LlmAppResponseInput(
        token="llm-response-token",
        source_app_call_token=source_token,
        proxy_call_id=proxy_call_id,
        message="{}",
        tool_calls="[]",
    )

    result = repository.create(input_model)

    database.session_scope.assert_called_once()
    context_manager.__enter__.assert_called_once()
    session.add.assert_called_once()
    session.flush.assert_called_once()
    session.refresh.assert_called_once()

    assert result.id == expected_id
    assert isinstance(result.id, UUID)
    assert result.llm_app_call_id == llm_app_call.id
    assert result.token == "llm-response-token"
    assert result.proxy_call_id == proxy_call_id
    assert result.message == "{}"
    assert result.tool_calls == "[]"
    assert result.created_at == expected_created_at


def test_create_llm_app_response_raises_when_source_missing(database_with_session):
    """It should raise when the source token cannot be resolved."""
    database, session, context_manager = database_with_session

    source_query = MagicMock()
    session.query.side_effect = [source_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = None

    repository = LlmAppResponsePostgresRepository(database)

    input_model = LlmAppResponseInput(
        token="llm-response-token",
        source_app_call_token="missing-token",
        proxy_call_id="proxy-123",
        message="{}",
        tool_calls="[]",
    )

    with pytest.raises(ResourceNotFoundError, match="Source app call not found"):
        repository.create(input_model)

    database.session_scope.assert_called_once()
    context_manager.__enter__.assert_called_once()
    session.add.assert_not_called()
    session.flush.assert_not_called()
    session.refresh.assert_not_called()


def test_create_llm_app_response_raises_when_llm_call_missing(database_with_session):
    """It should raise when the LLM app call is absent for the source token."""
    source_app_call = SimpleNamespace(id=uuid4(), token="source-token")

    database, session, context_manager = database_with_session

    source_query = MagicMock()
    llm_query = MagicMock()

    session.query.side_effect = [source_query, llm_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source_app_call

    llm_filtered = MagicMock()
    llm_query.filter.return_value = llm_filtered
    llm_filtered.one_or_none.return_value = None

    repository = LlmAppResponsePostgresRepository(database)

    input_model = LlmAppResponseInput(
        token="llm-response-token",
        source_app_call_token=source_app_call.token,
        proxy_call_id="proxy-123",
        message="{}",
        tool_calls="[]",
    )

    with pytest.raises(ResourceNotFoundError, match="LLM app call not found"):
        repository.create(input_model)

    database.session_scope.assert_called_once()
    context_manager.__enter__.assert_called_once()
    session.add.assert_not_called()
    session.flush.assert_not_called()
    session.refresh.assert_not_called()


def test_create_llm_app_response_raises_when_proxy_does_not_match_source(database_with_session):
    """It should raise when the proxy call id belongs to a different source call."""
    source_app_call = SimpleNamespace(id=uuid4(), token="source-token")
    other_source_app_call = SimpleNamespace(id=uuid4(), token="other-source")

    database, session, context_manager = database_with_session

    source_query = MagicMock()
    llm_query = MagicMock()

    session.query.side_effect = [source_query, llm_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source_app_call

    llm_filtered = MagicMock()
    llm_query.filter.return_value = llm_filtered
    llm_filtered.one_or_none.return_value = SimpleNamespace(
        id=uuid4(), source_app_call_id=other_source_app_call.id, proxy_call_id="proxy-123"
    )

    repository = LlmAppResponsePostgresRepository(database)

    input_model = LlmAppResponseInput(
        token="llm-response-token",
        source_app_call_token=source_app_call.token,
        proxy_call_id="proxy-123",
        message="{}",
        tool_calls="[]",
    )

    with pytest.raises(ValueError, match="Proxy call id does not belong"):
        repository.create(input_model)

    database.session_scope.assert_called_once()
    context_manager.__enter__.assert_called_once()
    session.add.assert_not_called()
    session.flush.assert_not_called()
    session.refresh.assert_not_called()
