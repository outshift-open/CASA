"""Routing module for Session operations."""

from abc import ABC

from fastapi import APIRouter

from identity_auth_server.core.types import AppMetadataResponse
from identity_auth_server.services.authorization_server import AuthorizationServerService


class AuthorizationServiceRoute(ABC):
    """Interface for AuthorizationServiceRoute."""

    router: APIRouter


class AuthorizationServiceRouteImpl:
    """Expose authorizationService routes backed by the authorizationService service implementation."""

    def __init__(self, authorization_service: AuthorizationServerService):
        """Initialize the AuthorizationServiceRoute with a service."""
        self.router = APIRouter()
        self.service = authorization_service

        @self.router.get("/health")
        def health_check() -> dict:
            """Health check endpoint."""
            return {"status": "ok"}

        @self.router.get("/{app_id}/oauth2/client-metadata.json")
        def app_metadata(
            app_id: str,
        ) -> AppMetadataResponse:
            """Generate a new token based on the request parameters."""
            return self.service.app_metadata(app_id)
