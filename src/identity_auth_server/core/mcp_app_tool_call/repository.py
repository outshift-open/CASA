"""Repository interface for McpAppToolCall."""

from abc import ABC, abstractmethod

from identity_auth_server.core.mcp_app_tool_call.types import (
    BlockedByType,
    BlockedByTypeName,
    McpAppToolCall,
    McpAppToolCallInput,
)


class McpAppToolCallRepository(ABC):
    """Interface for repositories handling MCP app tool calls."""

    @abstractmethod
    def create(
        self,
        mcp_app_tool_call: McpAppToolCallInput,
        blocked: bool = False,
        blocked_by_type_id: str | None = None,
    ) -> McpAppToolCall:
        """Persist a new MCP app tool call and return the stored model."""
        pass

    @abstractmethod
    def get_blocked_by_type_by_name(self, *, name: BlockedByTypeName) -> BlockedByType:
        """Fetch a blocked-by type definition by its canonical name."""
        pass
