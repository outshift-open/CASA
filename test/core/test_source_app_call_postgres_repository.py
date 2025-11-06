"""Unit tests for SourceAppCallPostgresRepository."""

import datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from identity_auth_server.core.source_app_call.postgres.repository import SourceAppCallPostgresRepository
from identity_auth_server.core.source_app_call.types import SourceAppCallInput


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


def test_create_source_app_call_persists_record(monkeypatch, database_with_session):
    """It should persist a new source app call and return it."""
    database, session = database_with_session

    expected_id = uuid4()
    expected_created_at = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)

    monkeypatch.setattr(
        "identity_auth_server.core.source_app_call.postgres.repository.uuid4",
        lambda: expected_id,
    )

    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return expected_created_at

    monkeypatch.setattr(
        "identity_auth_server.core.source_app_call.postgres.repository.datetime.datetime",
        FixedDateTime,
    )

    repository = SourceAppCallPostgresRepository(database)
    input_model = SourceAppCallInput(token="source-token", input="{}")

    result = repository.create(input_model)

    database.session_scope.assert_called_once()
    session.add.assert_called_once()
    session.flush.assert_called_once()
    session.refresh.assert_called_once()

    assert isinstance(result.id, UUID)
    assert result.id == expected_id
    assert result.token == "source-token"
    assert result.input == "{}"
    assert result.created_at == expected_created_at
