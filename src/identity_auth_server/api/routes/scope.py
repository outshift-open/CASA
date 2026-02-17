"""Routing module for Scope operations."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from identity_auth_server.api.dependencies import Container
from identity_auth_server.core.exceptions import ResourceAlreadyExistsError, ResourceNotFoundError
from identity_auth_server.core.types import Scope
from identity_auth_server.services.scope_service import ScopeRequest, ScopeService

router = APIRouter(tags=["Scopes"])


@router.post("/scopes")
def create_scope(
    scope_service: Annotated[ScopeService, Depends(Container.get_scope_service)],
    request: ScopeRequest,
) -> Scope:
    """Create a new scope."""
    try:
        return scope_service.create_scope(request)
    except ResourceAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/scopes")
def get_scopes(
    scope_service: Annotated[ScopeService, Depends(Container.get_scope_service)],
) -> List[Scope]:
    """Get all scopes."""
    return scope_service.get_all_scopes()


@router.get("/scopes/{scope_id}")
def get_scope(
    scope_service: Annotated[ScopeService, Depends(Container.get_scope_service)],
    scope_id: str,
) -> Scope:
    """Get a scope by ID."""
    scope = scope_service.get_scope_by_id(scope_id)
    if not scope:
        raise HTTPException(status_code=404, detail=f"Scope with id '{scope_id}' not found")
    return scope


@router.put("/scopes/{scope_id}")
def update_scope(
    scope_service: Annotated[ScopeService, Depends(Container.get_scope_service)],
    scope_id: str,
    request: ScopeRequest,
) -> Scope:
    """Update an existing scope."""
    try:
        return scope_service.update_scope(scope_id, request)
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
