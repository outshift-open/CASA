"""Service layer for MCP Discovery operations."""

import asyncio
from abc import ABC, abstractmethod

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from identity_auth_server.types import McpServer


class McpDiscoverService(ABC):
    """Interface for McpDiscover."""

    def __init__(self):
        """Initialize the service."""

    @abstractmethod
    def discover_mcp_tools(self, mcp_server_url: str) -> McpServer:
        """Discover MCP tools from the given MCP server URL."""
        pass


class McpDiscoverServiceImpl(McpDiscoverService):
    """Implementation of the McpAppToolCallService."""

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
                        print(e)

                    # Get resources
                    resources = []
                    try:
                        list_resources_response = await session.list_resources()
                        resources = list_resources_response.resources
                    except Exception as e:
                        print(e)

                    return McpServer(name="unknown", tools=tools, resources=resources)

        # Run the async function synchronously
        return asyncio.run(_discover())
