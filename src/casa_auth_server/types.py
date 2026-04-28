# Copyright 2025 Cisco Systems, Inc. and its affiliates
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

"""Common type definitions for Identity Auth Server."""

from mcp import types as mcp_types
from pydantic import BaseModel

# Base Types
Task = str  # Type alias for task descriptions
ToolName = str  # Type alias for tool names
McpBadge = str  # Type alias for MCP identity badges containing tool objects
McpResources = list[mcp_types.Resource]  # Type alias for list of MCP resource objects
McpServerName = str  # Type alias for MCP server names
McpTools = list[mcp_types.Tool]  # Type alias for list of MCP tool objects


class McpServer(BaseModel):
    """MCP Server with tools and resources."""

    name: McpServerName
    tools: list[mcp_types.Tool]
    resources: list[mcp_types.Resource]
