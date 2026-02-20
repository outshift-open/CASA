"""Routing module for MAS operations."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from identity_auth_server.api.dependencies import Container
from identity_auth_server.api.routes.view_models import AppViewModel
from identity_auth_server.core.types import MultiAgentSystem
from identity_auth_server.services.app_service import AppService
from identity_auth_server.services.mas_service import (
    MultiAgentSystemAppsBindingRequest,
    MultiAgentSystemCreateRequest,
    MultiAgentSystemService,
    MultiAgentSystemUpdateRequest,
)

router = APIRouter(tags=["Multi Agent Systems"])


@router.put("/mas")
def create_mas(
    mas_service: Annotated[MultiAgentSystemService, Depends(Container.get_mas_service)],
    request: MultiAgentSystemCreateRequest,
) -> MultiAgentSystem:
    """Create a new multi agent system."""
    mas = mas_service.create_mas(request)
    return mas


@router.post("/mas/{mas_id}/bind_apps", status_code=204)
def bind_apps(
    mas_service: Annotated[MultiAgentSystemService, Depends(Container.get_mas_service)],
    mas_id: str,
    request: MultiAgentSystemAppsBindingRequest,
):
    """Bind a list of apps with an existing multi agent system."""
    mas_service.bind_apps(mas_id, request)


@router.post("/mas/{mas_id}")
def update_mas(
    mas_service: Annotated[MultiAgentSystemService, Depends(Container.get_mas_service)],
    mas_id: str,
    request: MultiAgentSystemUpdateRequest,
) -> MultiAgentSystem:
    """Update an existing multi agent system instance."""
    return mas_service.update_mas(mas_id, request)


@router.delete("/mas/{mas_id}")
def delete_mas(
    mas_service: Annotated[MultiAgentSystemService, Depends(Container.get_mas_service)],
    mas_id: str,
):
    """Delete an existing multi agent system."""
    mas_service.delete_mas(mas_id)

    return {"message": f"MAS with id '{mas_id}' deleted successfully"}


@router.get("/mas")
def get_all_mas(
    mas_service: Annotated[MultiAgentSystemService, Depends(Container.get_mas_service)],
) -> List[MultiAgentSystem]:
    """Get the list of all multi agent systems."""
    return mas_service.get_all_mas()


@router.get("/mas/{mas_id}")
def get_mas_by_id(
    mas_service: Annotated[MultiAgentSystemService, Depends(Container.get_mas_service)],
    mas_id: str,
) -> MultiAgentSystem:
    """Get a multi agent system by id."""
    mas = mas_service.get_mas_by_id(mas_id)
    if not mas:
        raise HTTPException(status_code=404, detail=f"MAS with id '{mas_id}' not found")
    return mas


@router.get("/mas/{mas_id}/apps")
def get_mas_apps(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
    mas_id: str,
) -> List[AppViewModel]:
    """Get all the apps related to a MAS."""
    apps = app_service.get_mas_apps(mas_id)
    return [AppViewModel.model_validate(app) for app in apps]
