"""Routing module for App operations."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from identity_auth_server.api.dependencies import Container
from identity_auth_server.core.types import App
from identity_auth_server.services.app_service import AppRequest, AppService
from identity_auth_server.services.authorization_server import AuthorizationServerService

router = APIRouter(tags=["Apps"])


@router.post("/apps")
def create_app(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
    auth_service: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
    request: AppRequest,
) -> App:
    """Create a new App."""
    app = app_service.create_app(request)
    if app.id is None:
        raise HTTPException(status_code=500, detail="App creation failed: missing ID")
    return auth_service.create_for_app(str(app.id))


@router.get("/apps")
def get_apps(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
) -> List[App]:
    """Get all Apps."""
    return app_service.get_all_apps()


@router.get("/apps/{app_id}", response_model=None)
def get_app(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
    app_id: str,
) -> dict:
    """Get an App by ID."""
    app = app_service.get_app_by_id(app_id)
    if not app:
        raise HTTPException(status_code=404, detail=f"App with id '{app_id}' not found")
    payload = app.model_dump(mode="json", exclude_none=True)
    payload["tools"] = [
        {
            "id": tool.id,
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
            "output_schema": tool.output_schema,
            "scopes": [{"id": scope.id, "name": scope.name} for scope in tool.scopes],
        }
        for tool in app.tools
    ]
    return payload


@router.put("/apps/{app_id}")
def update_app(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
    app_id: str,
    request: AppRequest,
) -> App:
    """Update an existing App."""
    try:
        return app_service.update_app(app_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/apps/{app_id}")
def delete_app(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
    app_id: str,
) -> dict:
    """Delete an App."""
    app = app_service.get_app_by_id(app_id)
    if not app:
        raise HTTPException(status_code=404, detail=f"App with id '{app_id}' not found")

    app_service.delete_app(app_id)
    return {"message": f"App with id '{app_id}' deleted successfully"}
