"""Trace domain models."""

from typing import List, Optional

from pydantic import BaseModel

from identity_auth_server.core.llm_app_call.types import LlmAppCall
from identity_auth_server.core.llm_app_response.types import LlmAppResponse
from identity_auth_server.core.mcp_app_tool_call.types import McpAppToolCall
from identity_auth_server.core.source_app_call.types import SourceAppCall
from identity_auth_server.core.source_app_response.types import SourceAppResponse


class TraceLlmAppCall(BaseModel):
    """LLM app call paired with a single response."""

    llm_app_call: LlmAppCall
    llm_app_response: Optional[LlmAppResponse]


class TraceMcpAppToolCall(BaseModel):
    """MCP app tool call entry."""

    tool_call: McpAppToolCall
    blocked_by_description: str | None = None
    blocked_by_type: str | None = None


class Trace(BaseModel):
    """Full trace rooted at a source app call."""

    source_app_call: SourceAppCall
    source_app_response: SourceAppResponse | None
    llm_app_calls: List[TraceLlmAppCall]
    mcp_app_tool_calls: List[TraceMcpAppToolCall]


class TraceList(BaseModel):
    """Paginated list of traces."""

    items: List[Trace]
    total: int
    page: int
    page_size: int
