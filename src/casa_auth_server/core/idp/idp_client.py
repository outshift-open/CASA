# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""IdP client interface."""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from casa_auth_server.core.types import ActorClaim, AppMetadataResponse, AuthorizationServer, ClientCredentials


class TokenPayload(BaseModel):
    """Token payload returned by an IdP after successful authentication."""

    token: dict
    sub: str
    act: ActorClaim | None = None
    extra: dict | None = None
    scopes: list[str] = []
    tools: list[str] = []


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
