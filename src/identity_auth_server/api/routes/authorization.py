"""Routing module for Session operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Form

from identity_auth_server.api.dependencies import Container
from identity_auth_server.core.types import AppMetadataResponse, TokenResponse
from identity_auth_server.services.authorization_server import AuthorizationServerService

"""Expose authorizationService routes backed by the authorizationService service implementation."""

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/{app_id}/oauth2/client-metadata.json")
def app_metadata(
    auth_service: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
    app_id: str,
) -> AppMetadataResponse:
    """Generate a new token based on the request parameters."""
    return auth_service.app_metadata(app_id)


@router.post("/{app_id}/oauth2/token")
def token(
    auth_service: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
    app_id: str,
    grant_type: Annotated[str, Form()],
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str, Form()],
    input: Annotated[str, Form()] = "",
) -> TokenResponse:
    """Generate a new token based on the request parameters."""
    return auth_service.generate_token_oauth(app_id, grant_type, client_id, client_secret)
