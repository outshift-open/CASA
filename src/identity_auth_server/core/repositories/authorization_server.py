"""PostgreSQL implementation of SessionRepository."""

from abc import ABC, abstractmethod
from hashlib import sha256

from sqlmodel import Session, select

from identity_auth_server.core.types import (AuthorizationServer,
                                             ClientCredentials, Token)
from identity_auth_server.database.database import Database


class AuthorizationServerRepository(ABC):
    """Interface for AuthorizationServerRepository."""

    @abstractmethod
    def create_authorization_server(self, authorization_server: AuthorizationServer) -> AuthorizationServer:
        """Create a new authorization server."""

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

    def __init__(self, database: Database, session: Session | None = None):
        """Initialize the repository with a database session."""
        self.database = database
        self._session = session

    def create_authorization_server(self, authorization_server: AuthorizationServer) -> AuthorizationServer:
        """Persist an authorization server and return the created object."""
        if self._session:
            self._session.add(authorization_server)
            self._session.flush()
            self._session.refresh(authorization_server)

            return authorization_server

        with self.database.session_scope() as session:
            session.add(authorization_server)
            session.flush()
            session.refresh(authorization_server)
            session.expunge(authorization_server)

            return authorization_server

    def get_authorization_server_by_id(self, authorization_server_id: str) -> AuthorizationServer | None:
        """Retrieve an authorization server by its ID."""
        if self._session:
            statement = select(AuthorizationServer).where(AuthorizationServer.id == authorization_server_id)
            authorization_server = self._session.exec(statement).first()

            return authorization_server

        with self.database.session_scope() as session:
            statement = select(AuthorizationServer).where(AuthorizationServer.id == authorization_server_id)
            authorization_server = session.exec(statement).first()
            session.expunge(authorization_server)

            return authorization_server

    def create_client_credentials(self, client_credential: ClientCredentials) -> ClientCredentials:
        """Persist client credentials and return the created object."""
        if self._session:
            self._session.add(client_credential)
            self._session.flush()
            self._session.refresh(client_credential)

            return client_credential

        with self.database.session_scope() as session:
            session.add(client_credential)
            session.flush()
            session.refresh(client_credential)
            session.expunge(client_credential)

            return client_credential

    def get_client_credentials_by_client_id(self, client_id: str) -> ClientCredentials | None:
        """Find client credentials by client ID."""
        if self._session:
            statement = select(ClientCredentials).where(ClientCredentials.client_id == client_id)
            authorization_server = self._session.exec(statement).first()

            return authorization_server

        with self.database.session_scope() as session:
            statement = select(ClientCredentials).where(ClientCredentials.client_id == client_id)
            authorization_server = session.exec(statement).first()
            session.expunge(authorization_server)

            return authorization_server

    def create_token(self, token: Token) -> Token:
        """Persist a source app session and return the generated token."""
        # Hash the token value before storing
        token.value = sha256(token.value.encode("utf-8")).hexdigest()

        if self._session:
            self._session.add(token)
            self._session.flush()
            self._session.refresh(token)

            return token

        with self.database.session_scope() as session:
            session.add(token)
            session.flush()
            session.refresh(token)
            session.expunge(token)

            return token
