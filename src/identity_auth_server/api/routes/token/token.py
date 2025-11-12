"""Routing module for Session operations."""

from abc import ABC
from typing import Annotated

from fastapi import APIRouter, Form

from identity_auth_server.core.token.types import (
    TokenIntrospectParams,
    TokenIntrospectResponse,
    TokenRequestParams,
    TokenResponse,
)
from identity_auth_server.services.token import TokenService


class TokenRoute(ABC):
    """Interface for TokenRoute."""

    router: APIRouter


class TokenRouteImpl:
    """Expose token routes backed by the token service implementation."""

    def __init__(self, token_service: TokenService):
        """Initialize the TokenRoute with a service."""
        self.router = APIRouter()
        self.service = token_service

        @self.router.post("/oauth2/default/v1/token")
        def generate_token(
            client_id: Annotated[str, Form()],
            grant_type: Annotated[str, Form()],
            client_assertion_type: Annotated[str, Form()],
            client_assertion: Annotated[str, Form()],
            state: Annotated[str | None, Form()] = None,
        ) -> TokenResponse:
            """Generate a new token based on the request parameters."""
            data = TokenRequestParams(
                client_id=client_id,
                grant_type=grant_type,
                client_assertion_type=client_assertion_type,
                client_assertion=client_assertion,
            )
            return self.service.generate_token(data)

        @self.router.post("/oauth2/default/v1/introspect")
        def introspect_token(
            client_id: Annotated[str, Form()], token: Annotated[str, Form()]
        ) -> TokenIntrospectResponse:
            """Introspect a token to check its validity and retrieve metadata."""
            data = TokenIntrospectParams(client_id=client_id, token=token)

            print("Introspect token with data:", data)
            return self.service.introspect_token(data)
