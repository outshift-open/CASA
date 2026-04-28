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

"""Service layer for managing applications and their tools."""

import logging
from uuid import uuid4

from pydantic import BaseModel

from casa_auth_server.core.exceptions import ResourceAlreadyExistsError
from casa_auth_server.core.idp.idp_client import IdpClient
from casa_auth_server.core.repositories.app import AppRepository
from casa_auth_server.core.repositories.authorization_server import AuthorizationServerRepository
from casa_auth_server.core.repositories.multi_agent_system import MultiAgentSystemRepository
from casa_auth_server.core.repositories.scope import ScopeRepository
from casa_auth_server.core.types import (
    App,
    AppMetadataResponse,
    AppType,
    AuthorizationServer,
    ClientCredentials,
    Scope,
    Tool,
)

logger = logging.getLogger(__name__)


class ToolRequest(BaseModel):
    """Request model for tool creation."""

    name: str
    description: str
    input_schema: str
    output_schema: str
    scopes: list[str] | None = None


class AppRequest(BaseModel):
    """Request model for app creation and updates."""

    type: AppType
    name: str
    base_url: str
    mas_id: str
    tools: list[ToolRequest] = []


class AppService:
    """Service for managing application lifecycle and operations."""

    def __init__(
        self,
        app_repository: AppRepository,
        scope_repository: ScopeRepository,
        auth_repository: AuthorizationServerRepository,
        mas_repository: MultiAgentSystemRepository,
        idp_client: IdpClient,
        api_url: str,
    ):
        """Initialize the app service."""
        self.app_repository = app_repository
        self.scope_repository = scope_repository
        self.auth_repository = auth_repository
        self.mas_repository = mas_repository
        self.idp_client = idp_client
        self.api_url = api_url

    def _resolve_scopes(self, scope_names: list[str] | None) -> list[Scope]:
        if not scope_names:
            return []

        cleaned_names = [name.strip() for name in scope_names if name.strip()]
        if not cleaned_names:
            return []

        existing_scopes = self.scope_repository.get_scopes_by_names(cleaned_names)
        existing_by_name = {scope.name: scope for scope in existing_scopes}

        for name in cleaned_names:
            if name in existing_by_name:
                continue
            try:
                created = self.scope_repository.create_scope(Scope(name=name))
                existing_by_name[name] = created
            except ResourceAlreadyExistsError:
                scope = self.scope_repository.get_scope_by_name(name)
                if scope is not None:
                    existing_by_name[name] = scope

        return list(existing_by_name.values())

    def create_app(self, request: AppRequest) -> App:
        """Create app."""
        mas = self.mas_repository.get_by_id(request.mas_id)
        if mas is None:
            raise Exception(f"Multi Agent System with id {request.mas_id} not found.")

        authorization_server = mas.authorization_server
        if authorization_server is None or authorization_server.id is None:
            raise Exception(f"Mutli Agent System with id {request.mas_id} does not have an authorization server")

        app_id = uuid4()
        app = App(
            id=app_id,
            type=request.type,
            name=request.name,
            base_url=request.base_url,
            mas_id=mas.id,
            tools=[
                Tool(
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.input_schema,
                    output_schema=tool.output_schema,
                    scopes=self._resolve_scopes(tool.scopes),
                )
                for tool in request.tools
            ],
            client_credentials=ClientCredentials(
                id=uuid4(),
                name=f"{request.name}-client-credentials",
                client_id=f"{self.api_url}/{app_id}/oauth2/client-metadata.json",
                authorization_server_id=authorization_server.id,
            ),
        )

        logger.debug(f"Creating client credentials in IdP for app {app.id}")

        if not app.client_credentials:
            raise Exception(f"App {app.id} does not have client credentials")

        client_credentials = self.idp_client.create_client_credentials(
            authorization_server, app.client_credentials, self._get_app_metadata(app)
        )
        app.client_credentials.client_secret = client_credentials.client_secret

        return self.app_repository.create_app(app)

    def app_metadata(self, app_id: str) -> AppMetadataResponse:
        """Generate app metadata response."""
        # Get app
        app = self.app_repository.get_app_by_id(app_id)
        if app is None:
            raise Exception(f"App with id {app_id} not found.")

        return self._get_app_metadata(app)

    def _get_app_metadata(self, app: App) -> AppMetadataResponse:
        """Generate app metadata response."""
        return AppMetadataResponse(
            client_name=app.name,
            client_id=f"{self.api_url}/{app.id}/oauth2/client-metadata.json",
            grant_types=["client_credentials"],
            response_types=["token"],
            token_endpoint_auth_method="private_key_jwt",
            jwks_uri=f"{self.api_url}/{app.id}/oauth2/.well-known/jwks.json",
        )

    def get_all_apps(self) -> list[App]:
        """Get all apps."""
        return self.app_repository.get_all_apps()

    def get_mas_apps(self, mas_id: str) -> list[App]:
        """Get all apps in a MAS."""
        return self.app_repository.get_mas_apps(mas_id)

    def get_app_by_id(self, app_id: str) -> App | None:
        """Get app by ID."""
        return self.app_repository.get_app_by_id(app_id)

    def update_app(self, app_id: str, request: AppRequest) -> App:
        """Update app."""
        app = self.app_repository.get_app_by_id(app_id)
        if not app:
            raise ValueError(f"App with id '{app_id}' not found")

        app.type = request.type
        app.name = request.name
        app.base_url = request.base_url
        app.tools = [
            Tool(
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema,
                output_schema=tool.output_schema,
                scopes=self._resolve_scopes(tool.scopes),
            )
            for tool in request.tools
        ]

        return self.app_repository.update_app(app)

    def delete_app(self, app_id: str) -> None:
        """Delete app."""
        app = self.app_repository.get_app_by_id(app_id)
        if not app:
            raise ValueError(f"App with id {app_id} not found")

        client_credentials = app.client_credentials
        mas = app.mas
        authorization_server: AuthorizationServer | None = None
        if mas:
            authorization_server = mas.authorization_server

        logger.debug(f"Deleting app {app.id} from the database")
        self.app_repository.delete_app(app)

        if client_credentials and mas and authorization_server:
            logger.debug(f"Deleting client credentials {client_credentials.id} for app {app.id}")

            self.auth_repository.delete_client_credentials(client_credentials)
            self.idp_client.delete_client_credentials(authorization_server, client_credentials)
