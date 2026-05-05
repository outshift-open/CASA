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

"""Routing module for MAS operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from casa_auth_server.api.dependencies import Container
from casa_auth_server.api.routes.view_models import (
    AppSummaryViewModel,
    AppViewModel,
    MASDetailViewModel,
    MASListItemViewModel,
    MASListResponse,
)
from casa_auth_server.core.types import MultiAgentSystem
from casa_auth_server.services.app_service import AppService
from casa_auth_server.services.mas_service import (
    MultiAgentSystemAppsBindingRequest,
    MultiAgentSystemCreateRequest,
    MultiAgentSystemService,
    MultiAgentSystemUpdateRequest,
)
from casa_auth_server.telemetry.tracer_repository import TracerRepository

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
    tracer_repository: Annotated[TracerRepository, Depends(Container.get_tracer_repository)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None),
    include_metrics: bool = Query(False),
) -> MASListResponse:
    """Get a paginated list of multi agent systems, with inline app summaries and optional trace counts."""
    items, total = mas_service.get_all_mas_paginated(page, page_size, q)
    trace_counts: dict[str, object] = {}
    if include_metrics:
        mas_ids = [str(mas.id) for mas in items]
        trace_counts = {s.mas_id: s for s in tracer_repository.get_mas_trace_counts(mas_ids)}
    return MASListResponse(
        items=[
            MASListItemViewModel(
                id=mas.id,
                name=mas.name,
                namespace=mas.namespace,
                k8s_name=mas.k8s_name,
                enabled_tool_checks=mas.enabled_tool_checks,
                authorization_server_id=mas.authorization_server_id,
                created_at=mas.created_at,
                apps=[AppSummaryViewModel.model_validate(a) for a in (mas.apps or []) if a.deleted_at is None],
                traces=trace_counts.get(str(mas.id)),  # type: ignore[arg-type]
            )
            for mas in items
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/mas/{mas_id}")
def get_mas_by_id(
    mas_service: Annotated[MultiAgentSystemService, Depends(Container.get_mas_service)],
    tracer_repository: Annotated[TracerRepository, Depends(Container.get_tracer_repository)],
    mas_id: str,
    include_metrics: bool = Query(False),
) -> MASDetailViewModel:
    """Get a multi agent system by id."""
    mas = mas_service.get_mas_by_id(mas_id)
    if not mas:
        raise HTTPException(status_code=404, detail=f"MAS with id '{mas_id}' not found")
    traces = None
    if include_metrics:
        stats = tracer_repository.get_mas_trace_counts([mas_id])
        traces = stats[0] if stats else None
    return MASDetailViewModel(
        id=mas.id,
        name=mas.name,
        namespace=mas.namespace,
        k8s_name=mas.k8s_name,
        enabled_tool_checks=mas.enabled_tool_checks,
        authorization_server_id=mas.authorization_server_id,
        created_at=mas.created_at,
        apps=[AppSummaryViewModel.model_validate(a) for a in (mas.apps or []) if a.deleted_at is None],
        traces=traces,
    )


@router.get("/mas/{mas_id}/apps")
def get_mas_apps(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
    mas_id: str,
) -> list[AppViewModel]:
    """Get all the apps related to a MAS."""
    apps = app_service.get_mas_apps(mas_id)
    return [AppViewModel.model_validate(app) for app in apps]
