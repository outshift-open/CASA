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

"""Routing module for Session operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Form

from casa_auth_server.api.dependencies import Container
from casa_auth_server.core.types import AppMetadataResponse, TokenIntrospectResponse, TokenResponse
from casa_auth_server.services.app_service import AppService
from casa_auth_server.services.authorization_server import (
    AuthorizationServerService,
    TokenExchangeRequest,
    TokenRequest,
)

"""Expose authorizationService routes backed by the authorizationService service implementation."""

router = APIRouter(tags=["Authorization Server"])


@router.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/{app_id}/oauth2/client-metadata.json", generate_unique_id_function=lambda _: "app_metadata")
def app_metadata(
    app_service: Annotated[AppService, Depends(Container.get_app_service)],
    app_id: str,
) -> AppMetadataResponse:
    """Get an Application client metadata."""
    return app_service.app_metadata(app_id)


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
            user_input_id=data.user_input_id,
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
    tools: Annotated[list[str] | None, Form()] = None,
) -> TokenIntrospectResponse:
    """Introspect a token and evaluate it against the requested tools."""
    return auth_service.introspect_token(token, tools)
