# Copyright 2026 Google LLC
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

"""Service layer for Multi-Agent System business logic."""

import logging
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel

from casa_auth_server.core.idp.idp_client import IdpClient
from casa_auth_server.core.repositories.app import AppRepository
from casa_auth_server.core.repositories.authorization_server import AuthorizationServerRepository
from casa_auth_server.core.repositories.multi_agent_system import MultiAgentSystemRepository
from casa_auth_server.core.types import AuthorizationServer, MultiAgentSystem, ToolCheckFlags

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class MultiAgentSystemCreateRequest(BaseModel):
    """Request model for MAS creation."""

    name: str
    enabled_tool_checks: Optional[ToolCheckFlags] = None
    namespace: Optional[str] = None
    k8s_name: Optional[str] = None


class MultiAgentSystemUpdateRequest(BaseModel):
    """Request model for updating an existing MAS instance."""

    name: str
    enabled_tool_checks: Optional[ToolCheckFlags] = None


class MultiAgentSystemAppsBindingRequest(BaseModel):
    """Request model for binding/unbinding a list of apps to a MAS instance."""

    app_ids: List[str]


class MultiAgentSystemService:
    """A service exposing the APIs related to managing and using MAS."""

    def __init__(
        self,
        mas_repository: MultiAgentSystemRepository,
        app_repository: AppRepository,
        auth_srv_repository: AuthorizationServerRepository,
        idp_client: IdpClient,
    ):
        """Initialize the MultiAgentSystemService with its dependencies."""
        self._mas_repository = mas_repository
        self._app_repository = app_repository
        self._auth_srv_repository = auth_srv_repository
        self._idp_client = idp_client

    def create_mas(self, request: MultiAgentSystemCreateRequest) -> MultiAgentSystem:
        """Create a new Multi Agent System."""
        mas = MultiAgentSystem(
            id=uuid4(),
            name=request.name,
            namespace=request.namespace,
            k8s_name=request.k8s_name,
        )

        if request.enabled_tool_checks is not None:
            mas.enabled_tool_checks = request.enabled_tool_checks

        logger.debug(f"Creating authorization server for Multi Agent System {mas.id}")

        authorization_server = self._auth_srv_repository.create_authorization_server(
            AuthorizationServer(
                realm=f"{mas.name}-{mas.id}-auth-server",
            )
        )
        self._idp_client.create_authorization_server(authorization_server)

        mas.authorization_server_id = authorization_server.id

        return self._mas_repository.create(mas)

    def bind_apps(self, mas_id: str, request: MultiAgentSystemAppsBindingRequest):
        """Bind a list of Apps with an existing Multi Agent System."""
        mas = self._mas_repository.get_by_id(mas_id)
        if not mas:
            raise ValueError(f"MAS with id {id} not found")

        for app_id in request.app_ids:
            app = self._app_repository.get_app_by_id(app_id)
            if app:
                app.mas_id = mas.id
                self._app_repository.update_app(app)

    def update_mas(self, mas_id: str, request: MultiAgentSystemUpdateRequest) -> MultiAgentSystem:
        """Update an existing Multi Agent System."""
        mas = self._mas_repository.get_by_id(mas_id)
        if not mas:
            raise ValueError(f"MAS with id {id} not found")

        mas.name = request.name

        if request.enabled_tool_checks is not None:
            mas.enabled_tool_checks = request.enabled_tool_checks

        return self._mas_repository.update(mas)

    def delete_mas(self, id: str):
        """Delete an existing Multi Agent System along side its list of Apps."""
        mas = self._mas_repository.get_by_id(id)
        if not mas:
            raise ValueError(f"MAS with id {id} not found")

        # Use repository query instead of mas.apps relationship to respect soft-delete filter
        apps = self._app_repository.get_mas_apps(str(mas.id))
        for app in apps:
            self._app_repository.delete_app(app)

        # deleting the mas means deleting the auth server for now
        if mas.authorization_server:
            logger.debug(
                f"Deleting the authorization server {mas.authorization_server_id} for the Multi Agent System {mas.id}"
            )
            self._auth_srv_repository.delete_authorization_server(mas.authorization_server)
            self._idp_client.delete_authorization_server(mas.authorization_server)

        return self._mas_repository.delete(mas)

    def get_all_mas(self) -> List[MultiAgentSystem]:
        """Get all the existing Multi Agent Systems."""
        return self._mas_repository.get_all()

    def get_mas_by_id(self, id: str) -> MultiAgentSystem:
        """Get a Multi Agent System by ID."""
        return self._mas_repository.get_by_id(id)

    def get_mas_by_name(self, name: str, namespace: str) -> MultiAgentSystem:
        """Get MAS ID by name and namespace."""
        return self._mas_repository.get_by_name_and_namespace(name, namespace)
