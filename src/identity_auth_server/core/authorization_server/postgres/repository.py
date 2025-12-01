"""PostgreSQL implementation of SessionRepository."""

from hashlib import sha256

from sqlmodel import select

from identity_auth_server.core.authorization_server.repository import AuthorizationServerRepository
from identity_auth_server.core.authorization_server.types import AuthorizationServer, ClientCredentials, Token
from identity_auth_server.database.postgres.postgres import PostgresDB


class AuthorizationServerPostgresRepository(AuthorizationServerRepository):
    """PostgreSQL-backed token repository implementation."""

    def __init__(self, database: PostgresDB):
        """Initialize the repository with a database session."""
        self.database = database

    def create_authorization_server(self, authorization_server: AuthorizationServer) -> AuthorizationServer:
        """Persist an authorization server and return the created object."""
        with self.database.session_scope() as session:
            session.add(authorization_server)
            session.flush()
            session.refresh(authorization_server)

            return authorization_server

    def find_client_credentials_by_client_id(self, client_id: str) -> ClientCredentials | None:
        """Find client credentials by client ID."""
        with self.database.session_scope() as session:
            statement = select(ClientCredentials).where(ClientCredentials.client_id == client_id)
            result = session.exec(statement).first()

            return result

    def create_client_credentials(self, client_credential: ClientCredentials) -> ClientCredentials:
        """Persist client credentials and return the created object."""
        with self.database.session_scope() as session:
            session.add(client_credential)
            session.flush()
            session.refresh(client_credential)

            return client_credential

    def create_token(self, token: Token) -> Token:
        """Persist a source app session and return the generated token."""
        with self.database.session_scope() as session:
            # Hash the token value before storing
            token.value = sha256(token.value.encode("utf-8")).hexdigest()

            session.add(token)
            session.flush()
            session.refresh(token)

            return token
