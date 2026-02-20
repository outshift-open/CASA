"""Service layer for managing applications and their tools."""

import logging
from typing import List

from pydantic import BaseModel

from identity_auth_server.core.exceptions import ResourceAlreadyExistsError
from identity_auth_server.core.repositories.app import AppRepository
from identity_auth_server.core.repositories.authorization_server import AuthorizationServerRepository
from identity_auth_server.core.repositories.scope import ScopeRepository
from identity_auth_server.core.types import App, AppType, Scope, Tool
from identity_auth_server.thirdparty.idp.keycloak import KeycloakManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


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
    tools: List[ToolRequest] = []


class AppService:
    """Service for managing application lifecycle and operations."""

    def __init__(
        self,
        app_repository: AppRepository,
        scope_repository: ScopeRepository,
        keycloak_manager: KeycloakManager,
        auth_repository: AuthorizationServerRepository,
    ):
        """Initialize the app service."""
        self.app_repository = app_repository
        self.scope_repository = scope_repository
        self.keycloak_manager = keycloak_manager
        self.auth_repository = auth_repository

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
        app = App(
            type=request.type,
            name=request.name,
            base_url=request.base_url,
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
        )

        return self.app_repository.create_app(app)

    def get_all_apps(self) -> List[App]:
        """Get all apps."""
        return self.app_repository.get_all_apps()

    def get_mas_apps(self, mas_id: str) -> List[App]:
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

        logger.debug(f"Deleting app {app.id} from the database")
        self.app_repository.delete_app(app)

        if app.authorization_server:
            logger.debug(f"Deleting the authorization server {app.authorization_server_id} for app {app.id}")

            self.auth_repository.delete_authorization_server(app.authorization_server)
            self.keycloak_manager.delete_authorization_server(app.authorization_server)
