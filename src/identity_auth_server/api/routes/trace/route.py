"""Routing module for trace operations."""

from abc import ABC
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.trace.types import Trace, TraceList
from identity_auth_server.services.trace import TraceService


class TraceRoute(ABC):
    """Interface for TraceRoute."""

    router: APIRouter


class TraceRouteImpl:
    """Expose trace retrieval routes backed by the postgres implementation."""

    def __init__(self, trace_service: TraceService):
        """Initialize the TraceRoute with a service."""
        self.router = APIRouter()
        self.service = trace_service

        @self.router.get("/trace/{source_app_call_id}")
        def get_trace(source_app_call_id: UUID) -> Trace:
            """Retrieve a trace for a specific source app call."""
            try:
                return self.service.get_trace(source_app_call_id)
            except ResourceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except Exception as exc:
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred while retrieving the trace"
                ) from exc

        @self.router.get("/trace")
        def get_traces(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)) -> TraceList:
            """Retrieve paginated traces for all source app calls."""
            try:
                return self.service.get_traces(page, page_size)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except Exception as exc:
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred while retrieving traces"
                ) from exc
