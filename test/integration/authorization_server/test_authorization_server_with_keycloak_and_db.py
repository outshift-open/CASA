"""Tests for Authorization Server with Keycloak and PostgresDB integration."""

import pytest
from sqlmodel import SQLModel

from identity_auth_server.core.repositories.app import AppPostgresRepository
from identity_auth_server.core.repositories.authorization_server import AuthorizationServerPostgresRepository
from identity_auth_server.core.types import App
from identity_auth_server.database.postgres.postgres import PostgresDB
from identity_auth_server.services.authorization_server import AuthorizationServerServiceImpl
from identity_auth_server.thirdparty.idp.keycloak.keycloak import KeycloakManager


@pytest.fixture
def session():
    """Pytest fixture to set up and tear down the database for tests.

    - Creates a PostgresDB instance.
    - Drops the tables after all tests in the module are complete.
    """
    # Initialize the database connection using environment variables
    db = PostgresDB()

    # Create
    SQLModel.metadata.create_all(db.engine)

    # Provide a session for the tests
    with db.session_scope() as db_session:
        yield db_session

    # Teardown
    SQLModel.metadata.drop_all(db.engine)


def test_authorization_server(session, client):
    """Provide a database session for each test."""
    # Repositories
    app_repository = AppPostgresRepository(session)
    authorization_server_repository = AuthorizationServerPostgresRepository(session)

    # Keycloak Manager
    keycloak_manager = KeycloakManager()

    # Services
    authorization_server_service = AuthorizationServerServiceImpl(
        authorization_server_repository, app_repository, keycloak_manager, "http://localhost:3000"
    )

    # Create an app
    app = App(name="Test App", type="MCP_SERVER")
    app = app_repository.create(app)

    # Get the metadata
    client.get(f"/{app.id}/oauth2/client-metadata.json")

    # Create elements for app
    # authorization_server_service.create_for_app(app)
