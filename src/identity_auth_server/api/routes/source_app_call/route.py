"""Routing module for source app call operations."""

from abc import ABC

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from identity_auth_server.core.source_app_call.types import SourceAppCall, SourceAppCallInput
from identity_auth_server.services.source_app_call import SourceAppCallService


# interface for source app call service
class SourceAppCallRoute(ABC):
    """Interface for SourceAppCallRoute."""

    router: APIRouter


class SourceAppCallRouteImpl:
    """Expose source app call routes backed by the postgres implementation."""

    def __init__(self, source_app_call_service: SourceAppCallService):
        """Initialize the SourceAppCallRoute with a service."""
        self.router = APIRouter()
        self.service = source_app_call_service

        @self.router.post("/source-app-call")
        def create_source_app_call(source_app_call_input: SourceAppCallInput) -> SourceAppCall:
            """Create a new source app call."""
            try:
                return self.service.create_source_app_call(source_app_call_input)
            except IntegrityError as exc:
                # Handle unique constraint violation for token
                if "uq_source_app_calls_token" in str(exc) or "duplicate key" in str(exc).lower():
                    raise HTTPException(
                        status_code=409,
                        detail=f"Source app call with token '{source_app_call_input.token}' already exists",
                    ) from exc
                # Handle other integrity errors (e.g., foreign key violations)
                raise HTTPException(status_code=400, detail="Database integrity error: " + str(exc.orig)) from exc
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except Exception as exc:
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred while creating the source app call"
                ) from exc
