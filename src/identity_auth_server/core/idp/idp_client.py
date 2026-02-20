"""IdP client interface"""

from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from identity_auth_server.core.types import ActorClaim, AppMetadataResponse, AuthorizationServer, ClientCredentials


class TokenPayload(BaseModel):
    token: dict
    sub: str
    act: ActorClaim | None = None
    extra: dict | None = None
    scopes: List[str] = []
    tools: List[str] = []


class IdpClient(ABC):
    """Interface defining the API exposed by an IdP"""

    def __init__(self):
        pass

    @abstractmethod
    def create_authorization_server(self, authz_serv: AuthorizationServer) -> None:
        raise NotImplementedError()

    @abstractmethod
    def delete_authorization_server(self, authz_serv: AuthorizationServer) -> None:
        raise NotImplementedError()

    @abstractmethod
    def create_scopes(self, authz_serv: AuthorizationServer, scopes: list[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def create_client_credentials(
        self,
        authz_serv: AuthorizationServer,
        client_creds: ClientCredentials,
        metadata: AppMetadataResponse,
    ) -> ClientCredentials:
        raise NotImplementedError()

    @abstractmethod
    def delete_client_credentials(self, authz_serv: AuthorizationServer, client_creds: ClientCredentials) -> None:
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
        raise NotImplementedError()
