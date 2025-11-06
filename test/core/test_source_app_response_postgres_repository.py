"""Unit tests for SourceAppResponsePostgresRepository."""

import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.source_app_response.postgres.repository import SourceAppResponsePostgresRepository
from identity_auth_server.core.source_app_response.types import SourceAppResponseInput


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

    return database, session, context_manager


def test_create_source_app_response_persists_record(monkeypatch, database_with_session):
    """It should persist a new source app response linked to a source app call."""
    expected_id = uuid4()
    expected_created_at = datetime.datetime(2025, 1, 3, tzinfo=datetime.timezone.utc)

    database, session, context_manager = database_with_session

    source_token = "source-token"
    source_app_call = SimpleNamespace(id=uuid4(), token=source_token)

    source_query = MagicMock()
    session.query.side_effect = [source_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = source_app_call

    monkeypatch.setattr(
        "identity_auth_server.core.source_app_response.postgres.repository.uuid4",
        lambda: expected_id,
    )

    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return expected_created_at

    monkeypatch.setattr(
        "identity_auth_server.core.source_app_response.postgres.repository.datetime.datetime",
        FixedDateTime,
    )

    repository = SourceAppResponsePostgresRepository(database)

    input_model = SourceAppResponseInput(
        token="source-response-token",
        source_app_call_token=source_token,
        output="{}",
    )

    result = repository.create(input_model)

    database.session_scope.assert_called_once()
    context_manager.__enter__.assert_called_once()
    session.add.assert_called_once()
    session.flush.assert_called_once()
    session.refresh.assert_called_once()

    assert isinstance(result.id, UUID)
    assert result.id == expected_id
    assert result.source_app_call_id == source_app_call.id
    assert result.token == "source-response-token"
    assert result.output == "{}"
    assert result.created_at == expected_created_at


def test_create_source_app_response_raises_when_source_missing(database_with_session):
    """It should raise when the source token cannot be resolved."""
    database, session, context_manager = database_with_session

    source_query = MagicMock()
    session.query.side_effect = [source_query]

    source_filtered = MagicMock()
    source_query.filter.return_value = source_filtered
    source_filtered.one_or_none.return_value = None

    repository = SourceAppResponsePostgresRepository(database)

    input_model = SourceAppResponseInput(
        token="source-response-token",
        source_app_call_token="missing-token",
        output="{}",
    )

    with pytest.raises(ResourceNotFoundError, match="Source app call not found"):
        repository.create(input_model)

    database.session_scope.assert_called_once()
    context_manager.__enter__.assert_called_once()
    session.add.assert_not_called()
    session.flush.assert_not_called()
    session.refresh.assert_not_called()
