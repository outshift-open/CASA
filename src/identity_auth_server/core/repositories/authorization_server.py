"""PostgreSQL implementation of SessionRepository."""

from abc import ABC, abstractmethod
from hashlib import sha256

from sqlmodel import Session, select

from identity_auth_server.core.types import AuthorizationServer, ClientCredentials, Token


class AuthorizationServerRepository(ABC):
    """Interface for AuthorizationServerRepository."""

    @abstractmethod
    def create_authorization_server(self, authorization_server: AuthorizationServer) -> AuthorizationServer:
        """Create a new authorization server."""

    @abstractmethod
    def delete_authorization_server(self, authorization_server: AuthorizationServer) -> None:
        """Delete an existing authorization server."""

    @abstractmethod
    def get_authorization_server_by_id(self, authorization_server_id: str) -> AuthorizationServer | None:
        """Retrieve an authorization server by its ID."""

    @abstractmethod
    def create_client_credentials(self, client_credential: ClientCredentials) -> ClientCredentials:
        """Create new client credentials."""

    @abstractmethod
    def get_client_credentials_by_client_id(self, client_id: str) -> ClientCredentials | None:
        """Find client credentials by client ID."""

    @abstractmethod
    def create_token(self, token: Token) -> Token:
        """Create a new token."""


class AuthorizationServerPostgresRepository(AuthorizationServerRepository):
    """PostgreSQL-backed token repository implementation."""

    def __init__(self, session: Session):
        """Initialize the repository with a database session."""
        self._session = session

    def create_authorization_server(self, authorization_server: AuthorizationServer) -> AuthorizationServer:
        """Persist an authorization server and return the created object."""
        self._session.add(authorization_server)

        return authorization_server

    def delete_authorization_server(self, authorization_server: AuthorizationServer) -> None:
        """Delete an existing authorization server."""
        self._session.delete(authorization_server)

    def get_authorization_server_by_id(self, authorization_server_id: str) -> AuthorizationServer | None:
        """Retrieve an authorization server by its ID."""
        statement = select(AuthorizationServer).where(AuthorizationServer.id == authorization_server_id)
        authorization_server = self._session.exec(statement).first()

        return authorization_server

    def create_client_credentials(self, client_credential: ClientCredentials) -> ClientCredentials:
        """Persist client credentials and return the created object."""
        self._session.add(client_credential)

        return client_credential

    def get_client_credentials_by_client_id(self, client_id: str) -> ClientCredentials | None:
        """Find client credentials by client ID."""
        statement = select(ClientCredentials).where(ClientCredentials.client_id == client_id)
        authorization_server = self._session.exec(statement).first()

        return authorization_server

    def create_token(self, token: Token) -> Token:
        """Persist a source app session and return the generated token."""
        # Hash the token value before storing
        token.value = sha256(token.value.encode("utf-8")).hexdigest()

        self._session.add(token)

        return token
