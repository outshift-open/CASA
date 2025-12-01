"""Repository interface for Client."""

from abc import ABC, abstractmethod

from identity_auth_server.core.authorization_server.types import (
    AuthorizationServer, ClientCredentials, Token)


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
