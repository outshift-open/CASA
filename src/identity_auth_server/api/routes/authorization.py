"""Routing module for Session operations."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form

from identity_auth_server.api.dependencies import Container
from identity_auth_server.core.types import AppMetadataResponse, TokenResponse
from identity_auth_server.services.authorization_server import AuthorizationServerService, TokenExchangeRequest, TokenRequest

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
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str, Form()],
    user_input: Annotated[str, Form()] = "",
) -> TokenResponse:
    """Generate a new token based on the request parameters."""
    return auth_service.generate_token_oauth(TokenRequest(
        app_id=app_id,
        client_id=client_id,
        client_secret=client_secret,
        user_input=user_input,
    ))


@router.post("/{app_id}/oauth2/token_exchange")
def token_exchange(
    auth_service: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
    app_id: str,
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str, Form()],
    subject_token: Annotated[str, Form()],
    subject_token_type: Annotated[str, Form()],
    mcp_server_url: Annotated[Optional[str], Form()] = None,
    tools: Annotated[Optional[list[str]], Form()] = None,
) -> TokenResponse:
    """Do a token exchange for an app."""
    return auth_service.exchange_token(
        request=TokenExchangeRequest(
            app_id=app_id,
            client_id=client_id,
            client_secret=client_secret,
            subject_token=subject_token,
            subject_token_type=subject_token_type,
            scope=None,
            mcp_server_url=mcp_server_url,
            tools=tools,
        ),
    )
