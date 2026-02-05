from typing import List

from pydantic import BaseModel
from identity_auth_server.core.repositories.app import AppRepository
from identity_auth_server.core.repositories.multi_agent_system import MultiAgentSystemRepository
from identity_auth_server.core.types import MultiAgentSystem


class MultiAgentSystemCreateRequest(BaseModel):
    """Request model for MAS creation."""

    name: str


class MultiAgentSystemUpdateRequest(BaseModel):
    """Request model for updating an existing MAS instance."""

    name: str


class MultiAgentSystemAppsBindingRequest(BaseModel):
    """Request model for binding/unbinding a list of apps to a MAS instance."""

    app_ids: List[str]


class MultiAgentSystemService:
    """A service exposing the APIs related to managing and using MAS."""

    def __init__(self, mas_repository: MultiAgentSystemRepository, app_repository: AppRepository):
        self._mas_repository = mas_repository
        self._app_repository = app_repository

    def create_mas(self, request: MultiAgentSystemCreateRequest) -> MultiAgentSystem:
        """Create a new Multi Agent System."""
        mas = MultiAgentSystem(name=request.name)
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

        return self._mas_repository.update(mas)

    def delete_mas(self, id: str):
        """Delete an existing Multi Agent System along side its list of Apps."""
        mas = self._mas_repository.get_by_id(id)
        if not mas:
            raise ValueError(f"MAS with id {id} not found")

        for app in mas.apps:
            self._app_repository.delete_app(app)

        return self._mas_repository.delete(mas)

    def get_all_mas(self) -> List[MultiAgentSystem]:
        """Get all the existing Multi Agent Systems."""
        return self._mas_repository.get_all()

    def get_mas_by_id(self, id: str) -> MultiAgentSystem:
        """Get a Multi Agent System by ID."""
        return self._mas_repository.get_by_id(id)
