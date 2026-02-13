"""Service layer for managing scopes."""

import logging

from pydantic import BaseModel

from identity_auth_server.core.repositories.scope import ScopeRepository
from identity_auth_server.core.types import Scope

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class ScopeRequest(BaseModel):
    """Request model for scope creation and updates."""

    name: str


class ScopeService:
    """Service for managing scope lifecycle and operations."""

    def __init__(self, scope_repository: ScopeRepository):
        """Create a scope service.

        Args:
            scope_repository: Repository used to persist and query scopes.
        """
        self.scope_repository = scope_repository

    def create_scope(self, request: ScopeRequest) -> Scope:
        """Create a new scope."""
        scope = Scope(name=request.name)
        return self.scope_repository.create_scope(scope)

    def update_scope(self, scope_id: str, request: ScopeRequest) -> Scope:
        """Update an existing scope."""
        scope = self.scope_repository.get_scope_by_id(scope_id)
        if not scope:
            raise ValueError(f"Scope with id '{scope_id}' not found")
        scope.name = request.name
        return self.scope_repository.update_scope(scope)

    def delete_scope(self, scope_id: str) -> None:
        """Delete a scope."""
        scope = self.scope_repository.get_scope_by_id(scope_id)
        if not scope:
            raise ValueError(f"Scope with id '{scope_id}' not found")
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
