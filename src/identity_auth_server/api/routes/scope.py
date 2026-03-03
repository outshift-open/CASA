"""Routing module for Scope operations."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from identity_auth_server.api.dependencies import Container
from identity_auth_server.api.routes.view_models import ScopeViewModel
from identity_auth_server.core.exceptions import ResourceAlreadyExistsError, ResourceNotFoundError
from identity_auth_server.services.scope_service import ScopeCreateRequest, ScopeService, ScopeUpdateRequest

router = APIRouter(tags=["Scopes"])


@router.post("/scopes")
def create_scope(
    scope_service: Annotated[ScopeService, Depends(Container.get_scope_service)],
    request: ScopeCreateRequest,
) -> ScopeViewModel:
    """Create a new scope."""
    try:
        scope = scope_service.create_scope(request)
        return ScopeViewModel.model_validate(scope)
    except ResourceAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/scopes")
def get_scopes(
    scope_service: Annotated[ScopeService, Depends(Container.get_scope_service)],
) -> List[ScopeViewModel]:
    """Get all scopes."""
    scopes = scope_service.get_all_scopes()
    return [ScopeViewModel.model_validate(scope) for scope in scopes]


@router.get("/scopes/{scope_id}")
def get_scope(
    scope_service: Annotated[ScopeService, Depends(Container.get_scope_service)],
    scope_id: str,
) -> ScopeViewModel:
    """Get a scope by ID."""
    scope = scope_service.get_scope_by_id(scope_id)
    if not scope:
        raise HTTPException(status_code=404, detail=f"Scope with id '{scope_id}' not found")
    return ScopeViewModel.model_validate(scope)


@router.put("/scopes/{scope_id}")
def update_scope(
    scope_service: Annotated[ScopeService, Depends(Container.get_scope_service)],
    scope_id: str,
    request: ScopeUpdateRequest,
) -> ScopeViewModel:
    """Update an existing scope."""
    try:
        scope = scope_service.update_scope(scope_id, request)
        return ScopeViewModel.model_validate(scope)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ResourceAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/scopes/{scope_id}")
def delete_scope(
    scope_service: Annotated[ScopeService, Depends(Container.get_scope_service)],
    scope_id: str,
) -> dict:
    """Delete a scope."""
    try:
        scope_service.delete_scope(scope_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"message": f"Scope with id '{scope_id}' deleted successfully"}
