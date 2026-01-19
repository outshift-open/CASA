"""Routing module for Session operations."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form

from identity_auth_server.api.dependencies import Container
from identity_auth_server.core.types import AppMetadataResponse, TokenIntrospectResponse, TokenResponse
from identity_auth_server.services.authorization_server import (
    AuthorizationServerService,
    TokenExchangeRequest,
    TokenRequest,
)

"""Expose authorizationService routes backed by the authorizationService service implementation."""

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/{app_id}/oauth2/client-metadata.json", generate_unique_id_function=lambda _: "app_metadata")
def app_metadata(
    auth_service: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
    app_id: str,
) -> AppMetadataResponse:
    """Generate a new token based on the request parameters."""
    return auth_service.app_metadata(app_id)


@router.post("/{app_id}/oauth2/token", generate_unique_id_function=lambda _: "token")
def token(
    auth_service: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
    app_id: str,
    data: Annotated[TokenRequest, Form()],
) -> TokenResponse:
    """Generate a new token based on the request parameters."""
    return auth_service.generate_token_oauth(
        app_id,
        TokenRequest(
            client_id=data.client_id,
            client_secret=data.client_secret,
            user_input=data.user_input,
        ),
    )


@router.post("/{app_id}/oauth2/token_exchange", generate_unique_id_function=lambda _: "token_exchange")
def token_exchange(
    auth_service: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
    app_id: str,
    data: Annotated[TokenExchangeRequest, Form()],
) -> TokenResponse:
    """Do a token exchange for an app."""
    return auth_service.exchange_token(
        app_id,
        TokenExchangeRequest(
            client_id=data.client_id,
            client_secret=data.client_secret,
            subject_token=data.subject_token,
            subject_token_type=data.subject_token_type,
            scope=None,
            mcp_server_url=data.mcp_server_url,
            tools=data.tools,
        ),
    )


@router.post("/oauth2/introspect", generate_unique_id_function=lambda _: "introspect")
def introspect(
    auth_service: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
    token: Annotated[str, Form()],
    tools: Annotated[Optional[list[str]], Form()] = None,
) -> TokenIntrospectResponse:
    return auth_service.introspect_token(token, tools)
