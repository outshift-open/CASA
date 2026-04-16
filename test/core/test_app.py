"""Unit tests for App."""

from unittest.mock import MagicMock

import pytest

from identity_auth_server.core.repositories.app import AppPostgresRepository
from identity_auth_server.core.types import App, AppType


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


def test_create_app(database_with_session):
    """Test create an app."""
    _, session = database_with_session
    repository = AppPostgresRepository(session)

    # Create app
    app = repository.create_app(App(name="Test App", type=AppType.MCP_SERVER))

    assert app.id is not None

    # Configure mock so get_app_by_id returns the created app
    session.exec.return_value.first.return_value = app

    # Find by id
    found_app = repository.get_app_by_id(app.id)
    assert found_app is not None
    assert found_app.id == app.id
