from typing import List

from pydantic import BaseModel

from identity_auth_server.core.repositories.app import AppRepository
from identity_auth_server.core.types import App, AppType, Tool


class ToolRequest(BaseModel):
    name: str
    description: str
    input_schema: str
    output_schema: str


class AppRequest(BaseModel):
    type: AppType
    name: str
    base_url: str
    tools: List[ToolRequest] = []


class AppService:
    def __init__(self, app_repository: AppRepository):
        self.app_repository = app_repository

    def create_app(self, request: AppRequest) -> App:
        """Create app"""
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
