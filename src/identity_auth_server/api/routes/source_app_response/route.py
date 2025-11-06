"""Routing module for source app response operations."""

from abc import ABC

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.source_app_response.types import SourceAppResponse, SourceAppResponseInput
from identity_auth_server.services.source_app_response import SourceAppResponseService


class SourceAppResponseRoute(ABC):
    """Interface for SourceAppResponseRoute."""

    router: APIRouter


class SourceAppResponseRouteImpl:
    """Expose source app response routes backed by the postgres implementation."""

    def __init__(self, source_app_response_service: SourceAppResponseService):
        """Initialize the SourceAppResponseRoute with a service."""
        self.router = APIRouter()
        self.service = source_app_response_service

        @self.router.post("/source-app-response")
        def create_source_app_response(source_app_response_input: SourceAppResponseInput) -> SourceAppResponse:
            """Create a new source app response."""
            try:
                return self.service.create_source_app_response(source_app_response_input)
            except ResourceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except IntegrityError as exc:
                # Handle foreign key violations and other integrity errors
                if "foreign key" in str(exc).lower():
                    raise HTTPException(
                        status_code=404,
                        detail=f"Source app call with ID '{source_app_response_input.source_app_call_id}' not found",
                    ) from exc
                raise HTTPException(status_code=400, detail="Database integrity error: " + str(exc.orig)) from exc
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except Exception as exc:
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred while creating the source app response"
                ) from exc
