"""Service layer for managing applications and their tools."""

from typing import List

from pydantic import BaseModel

from identity_auth_server.core.repositories.app import AppRepository
from identity_auth_server.core.types import App, AppType, Tool


class ToolRequest(BaseModel):
    """Request model for tool creation."""

    name: str
    description: str
    input_schema: str
    output_schema: str


class AppRequest(BaseModel):
    """Request model for app creation and updates."""

    type: AppType
    name: str
    base_url: str
    tools: List[ToolRequest] = []


class AppService:
    """Service for managing application lifecycle and operations."""

    def __init__(self, app_repository: AppRepository):
        """Initialize the app service.

        Args:
            app_repository: Repository for app persistence operations.
        """
        self.app_repository = app_repository

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
                )
                for tool in request.tools
            ],
        )

        return self.app_repository.create_app(app)

    def get_all_apps(self) -> List[App]:
        """Get all apps."""
        return self.app_repository.get_all_apps()

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
            )
            for tool in request.tools
        ]

        return self.app_repository.update_app(app)

    def delete_app(self, app_id: str) -> None:
        """Delete app."""
        self.app_repository.delete_app(app_id)
