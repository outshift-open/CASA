"""Type definitions for Identity Auth Server - API."""

from pydantic import BaseModel

from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchInput, TaskToolMatchOutput
from identity_auth_server.types import AvailableTools, McpBadge, Task, ToolName


# Request/Response Models
class IntentMcpBadgeToolMatchRequest(BaseModel):
    """Request model for MCP badge tool match endpoint."""

    task: Task
    requested_tool: ToolName
    available_tools: AvailableTools
    mcp_badge: McpBadge


# Type aliases
IntentMcpBadgeToolMatchResult = TaskToolMatchOutput  # Type alias for MCP badge tool match result
IntentMcpToolMatchRequest = TaskToolMatchInput  # Type alias for MCP tool match request
IntentMcpToolMatchResult = TaskToolMatchOutput  # Type alias for MCP tool match result
