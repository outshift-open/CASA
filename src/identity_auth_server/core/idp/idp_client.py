"""IdP client interface."""

from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from identity_auth_server.core.types import ActorClaim, AppMetadataResponse, AuthorizationServer, ClientCredentials


class TokenPayload(BaseModel):
    """Token payload returned by an IdP after successful authentication."""

    token: dict
    sub: str
    act: ActorClaim | None = None
    extra: dict | None = None
    scopes: List[str] = []
    tools: List[str] = []


class IdpClient(ABC):
    """Interface defining the API exposed by an IdP."""

    def __init__(self):
        """Initialize the IdP client."""
        pass

    @abstractmethod
    def create_authorization_server(self, authz_serv: AuthorizationServer) -> None:
        """Create a new authorization server in the IdP."""
        raise NotImplementedError()

    @abstractmethod
    def delete_authorization_server(self, authz_serv: AuthorizationServer) -> None:
        """Delete an authorization server from the IdP."""
        raise NotImplementedError()

    @abstractmethod
    def create_scopes(self, authz_serv: AuthorizationServer, scopes: list[str]) -> None:
        """Create scopes in the given authorization server."""
        raise NotImplementedError()

    @abstractmethod
    def update_scope(self, authz_serv: AuthorizationServer, old_name: str, new_name: str) -> None:
        """Rename a scope in the given authorization server."""
        raise NotImplementedError()

    @abstractmethod
    def delete_scope(self, authz_serv: AuthorizationServer, scope_name: str) -> None:
        """Delete a scope from the given authorization server."""
        raise NotImplementedError()

    @abstractmethod
    def create_client_credentials(
        self,
        authz_serv: AuthorizationServer,
        client_creds: ClientCredentials,
        metadata: AppMetadataResponse,
    ) -> ClientCredentials:
        """Create client credentials in the given authorization server."""
        raise NotImplementedError()

    @abstractmethod
    def delete_client_credentials(self, authz_serv: AuthorizationServer, client_creds: ClientCredentials) -> None:
        """Delete client credentials from the given authorization server."""
        raise NotImplementedError()

    @abstractmethod
    def get_token(
        self,
        authz_serv: AuthorizationServer,
        client_creds: ClientCredentials,
        sub: str = "",
        act: ActorClaim | None = None,
        scopes: list[str] = [],
        extra: dict | None = None,
        user_input_id: str = "",
        tools: list[str] = [],
    ) -> TokenPayload:
        """Obtain a token from the IdP for the given client credentials."""
        raise NotImplementedError()
