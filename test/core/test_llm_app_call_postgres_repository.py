"""Unit tests for LlmAppCallPostgresRepository."""

import datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.llm_app_call.postgres.repository import LlmAppCallPostgresRepository
from identity_auth_server.core.llm_app_call.types import LlmAppCallInput
from identity_auth_server.core.source_app_call.postgres.models import SourceAppCallModel


@pytest.fixture
def database_with_session():
    """Provide a mock database and backing session."""
    session = MagicMock()
    session.refresh.side_effect = lambda _: None

    context_manager = MagicMock()
    context_manager.__enter__.return_value = session
    context_manager.__exit__.return_value = None

    database = MagicMock()
    database.session_scope.return_value = context_manager

    return database, session


def build_source_app_call(token: str) -> SourceAppCallModel:
    """Create a SourceAppCallModel instance for testing."""
    return SourceAppCallModel(
        id=uuid4(),
        token=token,
        input="{}",
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )


def test_create_llm_app_call_persists_record(monkeypatch, database_with_session):
    """It should persist a new LLM app call referencing the existing source record."""
    expected_id = uuid4()
    expected_created_at = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)

    source_token = "source-token"
    proxy_call_id = "proxy-123"
    source_app_call = build_source_app_call(source_token)

    database, session = database_with_session

    # Configure session query chain
    source_query = MagicMock()
    proxy_query = MagicMock()
    session.query.side_effect = [source_query, proxy_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source_app_call

    proxy_filtered = MagicMock()
    proxy_query.filter.return_value = proxy_filtered
    proxy_filtered.one_or_none.return_value = None

    monkeypatch.setattr(
        "identity_auth_server.core.llm_app_call.postgres.repository.uuid4",
        lambda: expected_id,
    )

    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return expected_created_at

    monkeypatch.setattr(
        "identity_auth_server.core.llm_app_call.postgres.repository.datetime.datetime",
        FixedDateTime,
    )

    repository = LlmAppCallPostgresRepository(database)

    input_model = LlmAppCallInput(
        token="llm-token",
        source_app_call_token=source_token,
        proxy_call_id=proxy_call_id,
        messages="[]",
        tools="[]",
    )

    result = repository.create(input_model)

    database.session_scope.assert_called_once()
    session.add.assert_called_once()
    session.flush.assert_called_once()
    session.refresh.assert_called_once()

    assert result.id == expected_id
    assert isinstance(result.id, UUID)
    assert result.source_app_call_id == source_app_call.id
    assert result.created_at == expected_created_at
    assert result.token == "llm-token"
    assert result.proxy_call_id == proxy_call_id
    assert result.messages == "[]"
    assert result.tools == "[]"


def test_create_llm_app_call_raises_when_source_missing(database_with_session):
    """It should raise ValueError when the source app call token cannot be resolved."""
    database, session = database_with_session

    source_query = MagicMock()
    session.query.side_effect = [source_query]
    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = None

    repository = LlmAppCallPostgresRepository(database)

    input_model = LlmAppCallInput(
        token="llm-token",
        source_app_call_token="missing-token",
        proxy_call_id="proxy-123",
        messages="[]",
        tools="[]",
    )

    with pytest.raises(ResourceNotFoundError, match="Source app call not found"):
        repository.create(input_model)

    database.session_scope.assert_called_once()
    session.add.assert_not_called()
    session.flush.assert_not_called()
    session.refresh.assert_not_called()


def test_create_llm_app_call_raises_when_proxy_conflicts(database_with_session):
    """It should raise ValueError when a proxy_call_id already exists."""
    source_token = "source-token"
    proxy_call_id = "proxy-123"
    source_app_call = build_source_app_call(source_token)

    database, session = database_with_session

    existing_llm_call = MagicMock()

    source_query = MagicMock()
    proxy_query = MagicMock()
    session.query.side_effect = [source_query, proxy_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source_app_call

    proxy_filtered = MagicMock()
    proxy_query.filter.return_value = proxy_filtered
    proxy_filtered.one_or_none.return_value = existing_llm_call

    repository = LlmAppCallPostgresRepository(database)

    input_model = LlmAppCallInput(
        token="llm-token",
        source_app_call_token=source_token,
        proxy_call_id=proxy_call_id,
        messages="[]",
        tools="[]",
    )

    with pytest.raises(ValueError, match="LLM app call already exists"):
        repository.create(input_model)

    database.session_scope.assert_called_once()
    session.add.assert_not_called()
    session.flush.assert_not_called()
    session.refresh.assert_not_called()
