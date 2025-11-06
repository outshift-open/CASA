"""Data models and helpers for MCP app tool calls."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel

from identity_auth_server.types import McpServer


class BlockedByTypeName(StrEnum):
    """Enumerates the seeded blocked-by reason names."""

    NO_LLM_CALLS_MADE_BY_APP = "no_llm_calls_made_by_app"
    TOOL_NOT_SELECTED_BY_LLM = "tool_not_selected_by_llm"
    TOOL_INTENT_MISMATCH = "tool_intent_mismatch"
    TOOL_PARAMETERS_MISMATCH = "tool_parameters_mismatch"
    MODIFIED_MCP_TOOL_DEFS = "modified_mcp_tool_defs"


class McpAppToolCallInput(BaseModel):
    """Input model for creating an MCP app tool call."""

    token: str
    source_app_call_token: str
    llm_app_call_token: str | None = None
    tool: str
    mcp_server: McpServer


class McpAppToolCall(BaseModel):
    """Data model for an MCP app tool call."""

    id: UUID
    source_app_call_id: UUID
    llm_app_call_id: UUID | None
    llm_app_response_id: UUID | None
    token: str | None = None
    tool: str
    blocked: bool
    blocked_by_type_id: UUID | None
    created_at: datetime


class BlockedByType(BaseModel):
    """Data model for a blocked by type."""

    id: UUID
    name: str
    description: str
    type: str
