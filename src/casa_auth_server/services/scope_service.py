# Copyright 2025 Cisco Systems, Inc. and its affiliates
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

"""Service layer for managing scopes."""

import logging
from uuid import UUID

from pydantic import BaseModel

from casa_auth_server.core.exceptions import ResourceNotFoundError
from casa_auth_server.core.idp.idp_client import IdpClient
from casa_auth_server.core.repositories.multi_agent_system import MultiAgentSystemRepository
from casa_auth_server.core.repositories.scope import ScopeRepository
from casa_auth_server.core.types import Scope

logger = logging.getLogger(__name__)


class ScopeCreateRequest(BaseModel):
    """Request model for scope creation."""

    name: str
    mas_id: UUID


class ScopeUpdateRequest(BaseModel):
    """Request model for scope updates."""

    name: str


class ScopeService:
    """Service for managing scope lifecycle and operations."""

    def __init__(
        self,
        scope_repository: ScopeRepository,
        mas_repository: MultiAgentSystemRepository,
        idp_client: IdpClient,
    ):
        """Create a scope service.

        Args:
            scope_repository: Repository used to persist and query scopes.
            mas_repository: Repository used to query multi-agent systems.
            idp_client: Client used to interact with the identity provider.
        """
        self.scope_repository = scope_repository
        self.mas_repository = mas_repository
        self.idp_client = idp_client

    def create_scope(self, request: ScopeCreateRequest) -> Scope:
        """Create a new scope."""
        try:
            mas = self.mas_repository.get_by_id(str(request.mas_id))
        except Exception as e:
            raise ValueError(f"Invalid Multi Agent System ID: {request.mas_id}") from e

        db_scope = self.scope_repository.create_scope(Scope(name=request.name, mas_id=request.mas_id))

        if mas.authorization_server:
            try:
                self.idp_client.create_scopes(mas.authorization_server, [db_scope.name])
            except Exception as e:
                logger.error(f"Failed to create scope {db_scope.name} in IDP: {e}")

        return db_scope

    def update_scope(self, scope_id: str, request: ScopeUpdateRequest) -> Scope:
        """Update an existing scope."""
        scope = self.scope_repository.get_scope_by_id(scope_id)
        if not scope:
            raise ResourceNotFoundError(f"Scope with id '{scope_id}' not found")

        old_name = scope.name
        name_changed = request.name is not None and old_name != request.name
        if name_changed:
            scope.name = request.name
            updated_scope = self.scope_repository.update_scope(scope)

            # Sync with IdP
            if scope.mas and scope.mas.authorization_server:
                self.idp_client.update_scope(scope.mas.authorization_server, old_name, scope.name)
            else:
                logger.warning("Scope has no MAS or authorization server, skipping IdP update")

            return updated_scope

        return scope

    def delete_scope(self, scope_id: str) -> None:
        """Delete a scope."""
        scope = self.scope_repository.get_scope_by_id(scope_id)
        if not scope:
            raise ResourceNotFoundError(f"Scope with id '{scope_id}' not found")

        if scope.mas and scope.mas.authorization_server:
            try:
                self.idp_client.delete_scope(scope.mas.authorization_server, scope.name)
            except Exception as e:
                logger.error(f"Failed to delete scope {scope.name} from Idp: {e}")

        self.scope_repository.delete_scope(scope)

    def get_scope_by_id(self, scope_id: str) -> Scope | None:
        """Get a scope by ID."""
        return self.scope_repository.get_scope_by_id(scope_id)

    def get_scope_by_name(self, name: str) -> Scope | None:
        """Get a scope by name."""
        return self.scope_repository.get_scope_by_name(name)

    def get_scopes_by_names(self, names: list[str]) -> list[Scope]:
        """Get scopes by names."""
        return self.scope_repository.get_scopes_by_names(names)

    def get_all_scopes(self) -> list[Scope]:
        """Get all scopes."""
        return self.scope_repository.get_all_scopes()
