"""Unit tests for AS."""

from unittest.mock import MagicMock

import pytest

from identity_auth_server.core.repositories.authorization_server import AuthorizationServerPostgresRepository
from identity_auth_server.core.types import AuthorizationServer, ClientCredentials


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


def test_create_all(database_with_session):
    """Test creating client credentials."""
    db, _ = database_with_session
    repository = AuthorizationServerPostgresRepository(db)

    # Create AuthorizationServer
    authorization_server = repository.create_authorization_server(AuthorizationServer(realm="test-realm"))

    assert authorization_server.realm == "test-realm"

    # Create ClientCredentials
    client_credential = repository.create_client_credentials(
        ClientCredentials(
            name="test",
            client_id="client-id",
            client_secret="client-secret",
            authorization_server_id=authorization_server.id,
        )
    )

    assert client_credential.id is not None
    assert client_credential.authorization_server_id == authorization_server.id

    # Find ClientCredentials by client_id
    found_credential = repository.get_client_credentials_by_client_id(client_credential.client_id)
    assert found_credential is not None
