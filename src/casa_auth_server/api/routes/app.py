"""Routing module for App operations."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from casa_auth_server.api.dependencies import Container
from casa_auth_server.api.routes.view_models import AppViewModel
from casa_auth_server.services.app_service import AppRequest, AppService

router = APIRouter(tags=["Apps"])


@router.post("/apps")
def create_app(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
    request: AppRequest,
) -> AppViewModel:
    """Create a new App."""
    app = app_service.create_app(request)
    if app.id is None:
        raise HTTPException(status_code=500, detail="App creation failed: missing ID")

    return AppViewModel.model_validate(app)


@router.get("/apps")
def get_apps(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
) -> List[AppViewModel]:
    """Get all Apps."""
    apps = app_service.get_all_apps()
    return [AppViewModel.model_validate(app) for app in apps]


@router.get("/apps/{app_id}")
def get_app(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
    app_id: str,
) -> AppViewModel:
    """Get an App by ID."""
    app = app_service.get_app_by_id(app_id)
    if not app:
        raise HTTPException(status_code=404, detail=f"App with id '{app_id}' not found")
    return AppViewModel.model_validate(app)


@router.put("/apps/{app_id}")
def update_app(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
    app_id: str,
    request: AppRequest,
) -> AppViewModel:
    """Update an existing App."""
    try:
        app = app_service.update_app(app_id, request)
        return AppViewModel.model_validate(app)
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
