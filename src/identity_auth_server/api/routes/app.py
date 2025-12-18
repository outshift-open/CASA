"""Routing module for App operations."""

from typing import Annotated

from fastapi import APIRouter, Depends

from identity_auth_server.api.dependencies import Container
from identity_auth_server.core.types import App
from identity_auth_server.services.app_service import AppRequest, AppService
from identity_auth_server.services.authorization_server import AuthorizationServerService

router = APIRouter()


@router.post("/apps")
def create_app(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
    auth_service: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
    request: AppRequest,
) -> App:
    """Create a new App"""
    app = app_service.create_app(request)
    return auth_service.create_for_app(app)
