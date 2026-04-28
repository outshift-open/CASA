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

"""Service layer for MCP Discovery operations."""

import asyncio
import logging

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from casa_auth_server.types import McpServer

logger = logging.getLogger(__name__)


class McpDiscoverService:
    """Service for discovering tools from MCP servers."""

    def discover_mcp_tools(self, mcp_server_url: str) -> McpServer:
        """Discover MCP tools from the given MCP server URL."""

        async def _discover() -> McpServer:
            # Connect to a streamable HTTP server
            async with streamablehttp_client(mcp_server_url) as (
                read_stream,
                write_stream,
                _,
            ):
                # Create a session using the client streams
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()

                    # Get tools
                    tools = []
                    try:
                        list_tools_response = await session.list_tools()
                        tools = list_tools_response.tools
                    except Exception as e:
                        logger.warning(f"Failed to list tools from {mcp_server_url}: {e}")

                    # Get resources
                    resources = []
                    try:
                        list_resources_response = await session.list_resources()
                        resources = list_resources_response.resources
                    except Exception as e:
                        logger.warning(f"Failed to list resources from {mcp_server_url}: {e}")

                    return McpServer(name="unknown", tools=tools, resources=resources)

        # Run the async function synchronously
        return asyncio.run(_discover())
