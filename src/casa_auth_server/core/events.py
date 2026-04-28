# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Domain events."""

import uuid
from abc import ABC
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class BaseEvent(BaseModel, ABC):
    """Base class for all domain events."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_input_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TokenIssuedEvent(BaseEvent):
    """Event emitted when a new access token is issued to a trusted client."""

    token: str
    app_id: str
    mas_id: str | None = None
    prompt: str


class TokenExchangedEvent(BaseEvent):
    """Event emitted when a token exchange occurs between an agent and an MCP server."""

    subject_token: str
    act_token: str
    subject_app_id: str
    act_app_id: str
    mas_id: str | None = None
    tools: list[str] | None


class LLMCallStartedEvent(BaseEvent):
    """Event emitted when an LLM call begins (recorded by the agent)."""

    call_id: str
    token: str
    app_id: str
    mas_id: str | None = None
    prompt: str
    tools: str | None


class LLMCallEndedEvent(BaseEvent):
    """Event emitted when an LLM call completes (recorded by the agent)."""

    call_id: str
    token: str
    app_id: str
    mas_id: str | None = None
    response: str
    tools: str | None


class MCPToolBlockingReason(StrEnum):
    """Enumerates the seeded blocked-by reason names."""

    NO_LLM_CALLS_MADE_BY_APP = "no_llm_calls_made_by_app"
    TOOL_NOT_SELECTED_BY_LLM = "tool_not_selected_by_llm"
    TOOL_INTENT_MISMATCH = "tool_intent_mismatch"
    TOOL_PARAMETERS_MISMATCH = "tool_parameters_mismatch"
    MODIFIED_MCP_TOOL_DEFS = "modified_mcp_tool_defs"
    INSUFFICIENT_SCOPE = "insufficient_scope"


class MCPToolBlockingType(StrEnum):
    """Enumerates the MCP tool blocking type."""

    DETERMINISTIC = "DETERMINISTIC"
    AI_POWERED = "AI_POWERED"


class MCPCallStartedEvent(BaseEvent):
    """Event emitted when an MCP tool call is initiated (approved or blocked)."""

    token: str = ""
    caller_app_id: str = ""
    callee_app_id: str = ""
    mas_id: str | None = None
    tool: str
    blocked: bool = False
    blocking_type: MCPToolBlockingType | None = None
    blocking_reason: MCPToolBlockingReason | None = None
