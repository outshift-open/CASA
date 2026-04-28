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

"""PostgreSQL implementation of SessionRepository."""

from abc import ABC, abstractmethod

from sqlmodel import Session, select

from casa_auth_server.core.types import AuthorizationServer, ClientCredentials


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
    def delete_client_credentials(self, client_credential: ClientCredentials) -> None:
        """Delete existing client credentials."""

    @abstractmethod
    def get_client_credentials_by_client_id(self, client_id: str) -> ClientCredentials | None:
        """Find client credentials by client ID."""


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

    def delete_client_credentials(self, client_credential: ClientCredentials) -> None:
        """Delete existing client credentials."""
        self._session.delete(client_credential)

    def get_client_credentials_by_client_id(self, client_id: str) -> ClientCredentials | None:
        """Find client credentials by client ID."""
        statement = select(ClientCredentials).where(ClientCredentials.client_id == client_id)
        authorization_server = self._session.exec(statement).first()

        return authorization_server
