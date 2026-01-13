"""Domain events"""

from abc import ABC
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
import uuid

from pydantic import BaseModel, Field


class BaseEvent(BaseModel, ABC):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_input_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TokenIssuedEvent(BaseEvent):
    token: str
    app_id: str

class TokenExchangedEvent(BaseEvent):
    subject_token: str
    act_token: str
    subject_app_id: str
    act_app_id: str
    tools: Optional[list[str]]

class LLMCallStartedEvent(BaseEvent):
    call_id: str
    token: str
    app_id: str
    prompt: str
    tools: Optional[list[str]]

class LLMCallEndedEvent(BaseEvent):
    call_id: str
    token: str
    app_id: str
    response: str
    tools: Optional[list[str]]

class MCPToolBlockingReason(StrEnum):
    """Enumerates the seeded blocked-by reason names."""

    NO_LLM_CALLS_MADE_BY_APP = "no_llm_calls_made_by_app"
    TOOL_NOT_SELECTED_BY_LLM = "tool_not_selected_by_llm"
    TOOL_INTENT_MISMATCH = "tool_intent_mismatch"
    TOOL_PARAMETERS_MISMATCH = "tool_parameters_mismatch"
    MODIFIED_MCP_TOOL_DEFS = "modified_mcp_tool_defs"

class MCPToolBlockingType(StrEnum):
    """Enumerates the MCP tool blocking type"""
    DETERMINISTIC = "DETERMINISTIC"
    AI_POWERED = "AI_POWERED"

class MCPCallStartedEvent(BaseEvent):
    token: str = ""
    caller_app_id: str = ""
    callee_app_id: str = ""
    tool: str
    blocked: bool = False
    blocking_type: Optional[MCPToolBlockingType] = None
    blocking_reason: Optional[MCPToolBlockingReason] = None