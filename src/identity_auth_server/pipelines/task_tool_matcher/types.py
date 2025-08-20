"""Type definitions for Identity Auth Server - Pipelines - Task Tool Matcher."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel

from identity_auth_server.types import AvailableTools, McpTools, Task, ToolName


class TaskToolMatcherType(str, Enum):
    """Available task-tool matcher types."""

    RANDOM = "random"


class TaskToolMatchReason(str, Enum):
    """Common reasons for task tool match results."""

    # Validation errors
    TOOL_NOT_AVAILABLE = "tool_not_available"
    TASK_EMPTY = "task_empty"
    NO_AVAILABLE_TOOLS = "no_available_tools"

    # Matcher-specific reasons
    RANDOM_NO_MATCH = "Random matcher decided this tool doesn't match the task"


class TaskToolMatchInput(BaseModel):
    """Request model for MCP tool match endpoint."""

    task: Task
    requested_tool: ToolName
    available_tools: AvailableTools
    mcp_tools: McpTools


class TaskToolMatchOutput(BaseModel):
    """Result of task tool matching."""

    task_tool_match: bool
    reason: Optional[TaskToolMatchReason] = None
