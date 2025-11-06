"""Routing module for MCP app tool call operations."""

import logging
from abc import ABC

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.mcp_app_tool_call.types import McpAppToolCall, McpAppToolCallInput
from identity_auth_server.services.mcp_app_tool_call import McpAppToolCallService

logger = logging.getLogger(__name__)


class McpAppToolCallRoute(ABC):
    """Interface for McpAppToolCallRoute."""

    router: APIRouter


class McpAppToolCallRouteImpl:
    """Expose MCP app tool call routes backed by the postgres implementation."""

    def __init__(self, mcp_app_tool_call_service: McpAppToolCallService):
        """Initialize the McpAppToolCallRoute with a service."""
        self.router = APIRouter()
        self.service = mcp_app_tool_call_service

        @self.router.post("/mcp-app-tool-call")
        def create_mcp_app_tool_call(mcp_app_tool_call_input: McpAppToolCallInput) -> McpAppToolCall:
            """Create a new MCP app tool call."""
            try:
                return self.service.create_mcp_app_tool_call(mcp_app_tool_call_input)
            except ResourceNotFoundError as exc:
                logger.warning(
                    "MCP tool call creation failed: resource missing",
                    extra={
                        "source_app_call_token": mcp_app_tool_call_input.source_app_call_token,
                        "llm_app_call_token": mcp_app_tool_call_input.llm_app_call_token,
                        "mcp_app_tool_call_token": mcp_app_tool_call_input.token,
                    },
                )
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except IntegrityError as exc:
                # Handle foreign key violations and other integrity errors
                if "foreign key" in str(exc).lower():
                    # Check which foreign key constraint was violated
                    if "llm_app_call" in str(exc).lower():
                        raise HTTPException(
                            status_code=404,
                            detail=f"LLM app call with ID '{mcp_app_tool_call_input.llm_app_call_id}' not found",
                        ) from exc
                    elif "llm_app_response" in str(exc).lower():
                        raise HTTPException(
                            status_code=404,
                            detail=f"LLM app response with ID '{mcp_app_tool_call_input.llm_app_response_id}' not found",
                        ) from exc
                    else:
                        raise HTTPException(status_code=404, detail="Referenced record not found") from exc
                logger.exception(
                    "MCP tool call creation failed: integrity error",
                    extra={
                        "source_app_call_token": mcp_app_tool_call_input.source_app_call_token,
                        "llm_app_call_token": mcp_app_tool_call_input.llm_app_call_token,
                        "mcp_app_tool_call_token": mcp_app_tool_call_input.token,
                    },
                )
                raise HTTPException(status_code=400, detail="Database integrity error: " + str(exc.orig)) from exc
            except ValueError as exc:
                logger.warning(
                    "MCP tool call creation failed: invalid payload",
                    extra={
                        "source_app_call_token": mcp_app_tool_call_input.source_app_call_token,
                        "llm_app_call_token": mcp_app_tool_call_input.llm_app_call_token,
                        "mcp_app_tool_call_token": mcp_app_tool_call_input.token,
                    },
                )
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except Exception as exc:
                logger.exception(
                    "MCP tool call creation failed: unhandled error",
                    extra={
                        "source_app_call_token": mcp_app_tool_call_input.source_app_call_token,
                        "llm_app_call_token": mcp_app_tool_call_input.llm_app_call_token,
                        "mcp_app_tool_call_token": mcp_app_tool_call_input.token,
                    },
                )
                raise HTTPException(
                    status_code=500,
                    detail="An unexpected error occurred while creating the MCP app tool call: " + str(exc),
                ) from exc
