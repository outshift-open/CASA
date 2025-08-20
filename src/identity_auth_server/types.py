"""Common type definitions for Identity Auth Server."""

from typing import List

from mcp import types as mcp_types

# Base Types
Task = str  # Type alias for task descriptions
ToolName = str  # Type alias for tool names
McpBadge = str  # Type alias for MCP identity badges containing tool objects
AvailableTools = List[ToolName]  # Type alias for list of available tool names
McpTools = List[mcp_types.Tool]  # Type alias for list of MCP tool objects
