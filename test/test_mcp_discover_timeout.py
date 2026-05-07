"""Unit tests for McpDiscoverService timeout behavior."""

import asyncio
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch

import pytest

from casa_auth_server.services.mcp_discover import McpDiscoverService


def test_discover_mcp_tools_raises_on_timeout():
    """discover_mcp_tools raises TimeoutError when MCP server is unreachable within timeout."""
    service = McpDiscoverService()

    @asynccontextmanager
    async def slow_client(*args, **kwargs):
        await asyncio.sleep(999)
        yield MagicMock(), MagicMock(), MagicMock()

    with patch("casa_auth_server.services.mcp_discover.streamablehttp_client", slow_client):
        with pytest.raises((TimeoutError, asyncio.TimeoutError)):
            service.discover_mcp_tools("http://slow-server/mcp", timeout_seconds=0.01)
