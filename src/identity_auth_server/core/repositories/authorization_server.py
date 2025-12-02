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
    def create_client_credentials(self, client_credential: ClientCredentials) -> ClientCredentials:
        """Create new client credentials."""

    @abstractmethod
    def find_client_credentials_by_client_id(self, client_id: str) -> ClientCredentials | None:
        """Find client credentials by client ID."""

    @abstractmethod
    def create_token(self, token: Token) -> Token:
        """Create a new token."""


class AuthorizationServerPostgresRepository(AuthorizationServerRepository):
    """PostgreSQL-backed token repository implementation."""

    def __init__(self, session: Session):
        """Initialize the repository with a database session."""
        self.session = session

    def create_authorization_server(self, authorization_server: AuthorizationServer) -> AuthorizationServer:
        """Persist an authorization server and return the created object."""
        self.session.add(authorization_server)
        self.session.flush()
        self.session.refresh(authorization_server)

        return authorization_server

    def find_client_credentials_by_client_id(self, client_id: str) -> ClientCredentials | None:
        """Find client credentials by client ID."""
        statement = select(ClientCredentials).where(ClientCredentials.client_id == client_id)
        result = self.session.exec(statement).first()

        return result

    def create_client_credentials(self, client_credential: ClientCredentials) -> ClientCredentials:
        """Persist client credentials and return the created object."""
        self.session.add(client_credential)
        self.session.flush()
        self.session.refresh(client_credential)

        return client_credential

    def create_token(self, token: Token) -> Token:
        """Persist a source app session and return the generated token."""
        # Hash the token value before storing
        token.value = sha256(token.value.encode("utf-8")).hexdigest()

        self.session.add(token)
        self.session.flush()
        self.session.refresh(token)

        return token
