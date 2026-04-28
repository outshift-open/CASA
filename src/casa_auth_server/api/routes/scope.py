# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Routing module for Scope operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from casa_auth_server.api.dependencies import Container
from casa_auth_server.api.routes.view_models import ScopeViewModel
from casa_auth_server.core.exceptions import ResourceAlreadyExistsError, ResourceNotFoundError
from casa_auth_server.services.scope_service import ScopeCreateRequest, ScopeService, ScopeUpdateRequest

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
) -> list[ScopeViewModel]:
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
