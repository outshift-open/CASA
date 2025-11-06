"""Routing module for LLM app call operations."""

from abc import ABC

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.llm_app_call.types import LlmAppCall, LlmAppCallInput
from identity_auth_server.services.llm_app_call import LlmAppCallService


class LlmAppCallRoute(ABC):
    """Interface for LlmAppCallRoute."""

    router: APIRouter


class LlmAppCallRouteImpl:
    """Expose LLM app call routes backed by the postgres implementation."""

    def __init__(self, llm_app_call_service: LlmAppCallService):
        """Initialize the LlmAppCallRoute with a service."""
        self.router = APIRouter()
        self.service = llm_app_call_service

        @self.router.post("/llm-app-call")
        def create_llm_app_call(llm_app_call_input: LlmAppCallInput) -> LlmAppCall:
            """Create a new LLM app call."""
            try:
                return self.service.create_llm_app_call(llm_app_call_input)
            except ResourceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except IntegrityError as exc:
                # Handle foreign key violations and other integrity errors
                if "foreign key" in str(exc).lower():
                    raise HTTPException(
                        status_code=404,
                        detail=f"Source app call with ID '{llm_app_call_input.source_app_call_id}' not found",
                    ) from exc
                raise HTTPException(status_code=400, detail="Database integrity error: " + str(exc.orig)) from exc
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except Exception as exc:
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred while creating the LLM app call"
                ) from exc
