# Copyright 2025 Cisco Systems, Inc. and its affiliates
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

"""Routing module for App operations."""

from typing import Annotated

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
) -> list[AppViewModel]:
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
