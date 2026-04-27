"""Common type definitions for Identity Auth Server."""

from typing import List

from mcp import types as mcp_types
from pydantic import BaseModel

# Base Types
Task = str  # Type alias for task descriptions
ToolName = str  # Type alias for tool names
McpBadge = str  # Type alias for MCP identity badges containing tool objects
McpResources = List[mcp_types.Resource]  # Type alias for list of MCP resource objects
McpServerName = str  # Type alias for MCP server names
McpTools = List[mcp_types.Tool]  # Type alias for list of MCP tool objects


class McpServer(BaseModel):
    """MCP Server with tools and resources."""

    name: McpServerName
    tools: List[mcp_types.Tool]
    resources: List[mcp_types.Resource]
