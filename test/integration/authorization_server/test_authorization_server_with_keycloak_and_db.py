"""Tests for Authorization Server with Keycloak and PostgresDB integration."""

import json

import pytest
from sqlmodel import SQLModel

from identity_auth_server.core.repositories.app import AppPostgresRepository
from identity_auth_server.core.repositories.authorization_server import \
    AuthorizationServerPostgresRepository
from identity_auth_server.core.types import App, TokenRequestParams, Tool
from identity_auth_server.database.postgres.postgres import PostgresDB
from identity_auth_server.services.authorization_server import \
    AuthorizationServerServiceImpl
from identity_auth_server.thirdparty.idp.keycloak.keycloak import \
    KeycloakManager


@pytest.fixture
def database_with_session():
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
        yield db, db_session

    # Teardown
    SQLModel.metadata.drop_all(db.engine)


def test_authorization_server(database_with_session, api_server):
    """Provide a database session for each test."""
    db, session = database_with_session

    # Repositories
    app_repository = AppPostgresRepository(db, session)
    authorization_server_repository = AuthorizationServerPostgresRepository(db, session)

    # Keycloak Manager
    keycloak_manager = KeycloakManager()

    # Services
    authorization_server_service = AuthorizationServerServiceImpl(
        authorization_server_repository, app_repository, keycloak_manager, "http://localhost:3000"
    )

    # Create an app
    app = App(
        name="Test App",
        type="MCP_SERVER",
    )
    app = app_repository.create_app(app)

    # Create two tools
    tool1 = app_repository.create_tool(
        Tool(
            name="Test Tool 1",
            description="A tool for testing",
            input_schema=json.dumps({"type": "object", "properties": {"input": {"type": "string"}}}),
            output_schema=json.dumps({"type": "object", "properties": {"output": {"type": "string"}}}),
            app_id=app.id,
        )
    )

    app_repository.create_tool(
        Tool(
            name="Test Tool 2",
            description="Another tool for testing",
            input_schema=json.dumps({"type": "object", "properties": {"input": {"type": "string"}}}),
            output_schema=json.dumps({"type": "object", "properties": {"output": {"type": "string"}}}),
            app_id=app.id,
        )
    )

    # Search app
    found_app = app_repository.get_app_by_id(app.id)

    assert found_app.id is not None
    assert found_app.name == "Test App"
    assert app.tools is not None
    assert len(app.tools) == 2

    # Commit session
    session.commit()

    # Create elements for app
    app = authorization_server_service.create_for_app(app)
    app_repository.update_app(app)

    assert app.authorization_server_id is not None
    assert app.client_credentials_id is not None

    # Get the authorization server
    authorization_server = authorization_server_repository.get_authorization_server_by_id(app.authorization_server_id)

    # Try to get a token without act
    token = authorization_server_service.generate_token(
        authorization_server,
        TokenRequestParams(app=app, grant_type="client_credentials", tools=[tool1]),
    )

    assert token.access_token is not None

    # Create an act app
    act_app = App(name="Act App", type="MCP_SERVER")
    act_app = app_repository.create_app(act_app)

    # Commit session
    session.commit()

    act_app = authorization_server_service.create_for_app(act_app)
    app_repository.update_app(act_app)
    assert act_app.authorization_server_id is not None

    # Try to get a token with act
    token_with_act = authorization_server_service.generate_token(
        authorization_server,
        TokenRequestParams(
            app=app,
            grant_type="client_credentials",
            tools=[tool1],
            act=act_app,
        ),
    )

    assert token_with_act.access_token is not None
