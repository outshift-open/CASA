"""Routing module for LLM app response operations."""

from abc import ABC

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.llm_app_response.types import LlmAppResponse, LlmAppResponseInput
from identity_auth_server.services.llm_app_response import LlmAppResponseService


class LlmAppResponseRoute(ABC):
    """Interface for LlmAppResponseRoute."""

    router: APIRouter


class LlmAppResponseRouteImpl:
    """Expose LLM app response routes backed by the postgres implementation."""

    def __init__(self, llm_app_response_service: LlmAppResponseService):
        """Initialize the LlmAppResponseRoute with a service."""
        self.router = APIRouter()
        self.service = llm_app_response_service

        @self.router.post("/llm-app-response")
        def create_llm_app_response(llm_app_response_input: LlmAppResponseInput) -> LlmAppResponse:
            """Create a new LLM app response."""
            try:
                return self.service.create_llm_app_response(llm_app_response_input)
            except ResourceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except IntegrityError as exc:
                # Handle foreign key violations and other integrity errors
                if "foreign key" in str(exc).lower():
                    raise HTTPException(
                        status_code=404,
                        detail=f"LLM app call with proxy ID '{llm_app_response_input.proxy_call_id}' not found",
                    ) from exc
                raise HTTPException(status_code=400, detail="Database integrity error: " + str(exc.orig)) from exc
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except Exception as exc:
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred while creating the LLM app response"
                ) from exc
