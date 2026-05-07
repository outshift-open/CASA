# Copyright 2026 Cisco Systems, Inc. and its affiliates
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

"""Unit tests for K8sCRDService MCP tool auto-discovery."""

import json
from unittest.mock import MagicMock, patch
from uuid import uuid4

from mcp import types as mcp_types

from casa_auth_server.core.types import App, AppType, MultiAgentSystem, ToolCheckFlags
from casa_auth_server.k8s.k8s_crd_service import K8sCRDService
from casa_auth_server.k8s.k8s_types import (
    AppSpec,
    AppSpecBaseUrl,
    MASCreateRequest,
    MultiAgentSystemMetadata,
    MultiAgentSystemSpec,
)
from casa_auth_server.types import McpServer


def _make_service(mcp_discover=None):
    mas_service = MagicMock()
    app_service = MagicMock()
    idp_client = MagicMock()
    k8s_mas_repository = MagicMock()
    mcp_discover = mcp_discover or MagicMock()
    return K8sCRDService(mas_service, app_service, idp_client, k8s_mas_repository, mcp_discover)


def _make_mcp_app(base_url: str = "http://mcp-server") -> App:
    return App(
        id=uuid4(),
        type=AppType.MCP_SERVER,
        name="my-mcp",
        base_url=base_url,
        mas_id=uuid4(),
    )


def _make_mas_create_request(app_type: AppType = AppType.MCP_SERVER) -> MASCreateRequest:
    return MASCreateRequest(
        metadata=MultiAgentSystemMetadata(name="test-mas", namespace="default"),
        spec=MultiAgentSystemSpec(
            name="Test MAS",
            apps=[
                AppSpec(
                    name="my-mcp",
                    type=app_type,
                    baseUrl=AppSpecBaseUrl(host="mcp-server:8080", scheme="http"),
                )
            ],
        ),
    )


def test_discover_and_register_tools_calls_update_app_on_success():
    """When discovery succeeds, update_app is called with discovered tools."""
    mcp_tool = mcp_types.Tool(
        name="read_file",
        description="Reads a file",
        inputSchema={"type": "object", "properties": {"path": {"type": "string"}}},
    )
    mcp_server = McpServer(name="my-mcp", tools=[mcp_tool], resources=[])

    mock_discover = MagicMock()
    mock_discover.discover_mcp_tools.return_value = mcp_server

    service = _make_service(mcp_discover=mock_discover)
    app = _make_mcp_app()

    service._discover_and_register_tools(app)

    mock_discover.discover_mcp_tools.assert_called_once_with("http://mcp-server")
    service._app_service.update_app.assert_called_once()
    call_args = service._app_service.update_app.call_args
    app_id_arg = call_args[0][0]
    request_arg = call_args[0][1]

    assert app_id_arg == str(app.id)
    assert len(request_arg.tools) == 1
    assert request_arg.tools[0].name == "read_file"
    assert request_arg.tools[0].description == "Reads a file"
    assert request_arg.tools[0].input_schema == json.dumps(
        {"type": "object", "properties": {"path": {"type": "string"}}}
    )
    assert request_arg.tools[0].output_schema == "{}"


def test_discover_and_register_tools_skips_on_discovery_failure():
    """When discovery raises, update_app is NOT called and no exception propagates."""
    mock_discover = MagicMock()
    mock_discover.discover_mcp_tools.side_effect = TimeoutError("timeout")

    service = _make_service(mcp_discover=mock_discover)
    app = _make_mcp_app()

    service._discover_and_register_tools(app)

    service._app_service.update_app.assert_not_called()


def test_discover_and_register_tools_skips_on_update_failure():
    """When update_app raises, no exception propagates."""
    mcp_tool = mcp_types.Tool(name="write_file", description=None, inputSchema={})
    mcp_server = McpServer(name="my-mcp", tools=[mcp_tool], resources=[])

    mock_discover = MagicMock()
    mock_discover.discover_mcp_tools.return_value = mcp_server

    service = _make_service(mcp_discover=mock_discover)
    service._app_service.update_app.side_effect = Exception("db error")
    app = _make_mcp_app()

    service._discover_and_register_tools(app)


def test_discover_and_register_tools_handles_none_description():
    """Tools with no description map to empty string."""
    mcp_tool = mcp_types.Tool(name="ping", description=None, inputSchema={})
    mcp_server = McpServer(name="my-mcp", tools=[mcp_tool], resources=[])

    mock_discover = MagicMock()
    mock_discover.discover_mcp_tools.return_value = mcp_server

    service = _make_service(mcp_discover=mock_discover)
    app = _make_mcp_app()

    service._discover_and_register_tools(app)

    request_arg = service._app_service.update_app.call_args[0][1]
    assert request_arg.tools[0].description == ""


def test_create_mas_from_crd_triggers_discovery_for_mcp_server():
    """create_mas_from_crd calls _discover_and_register_tools for MCP_SERVER apps."""
    mock_discover = MagicMock()
    service = _make_service(mcp_discover=mock_discover)

    mas_id = uuid4()
    mock_mas = MagicMock(spec=MultiAgentSystem)
    mock_mas.id = mas_id
    mock_mas.name = "Test MAS"
    mock_mas.enabled_tool_checks = ToolCheckFlags.NONE
    mock_mas.authorization_server = None

    service._mas_service.create_mas.return_value = mock_mas
    service._mas_service._mas_repository.get_by_name_and_namespace.side_effect = Exception("not found")

    created_app = _make_mcp_app()
    created_app.mas_id = mas_id
    service._app_service.create_app.return_value = created_app
    service._app_service.get_mas_apps.return_value = [created_app]
    service._k8s_mas_repository.create_mas.return_value = None

    with patch.object(service, "_discover_and_register_tools") as mock_drt:
        service.create_mas_from_crd(_make_mas_create_request(AppType.MCP_SERVER))
        mock_drt.assert_called_once_with(created_app)


def test_create_mas_from_crd_skips_discovery_for_non_mcp_apps():
    """create_mas_from_crd does NOT call _discover_and_register_tools for AGENT apps."""
    mock_discover = MagicMock()
    service = _make_service(mcp_discover=mock_discover)

    mas_id = uuid4()
    mock_mas = MagicMock(spec=MultiAgentSystem)
    mock_mas.id = mas_id
    mock_mas.name = "Test MAS"
    mock_mas.enabled_tool_checks = ToolCheckFlags.NONE
    mock_mas.authorization_server = None

    service._mas_service.create_mas.return_value = mock_mas
    service._mas_service._mas_repository.get_by_name_and_namespace.side_effect = Exception("not found")

    agent_app = App(id=uuid4(), type=AppType.AGENT, name="my-agent", base_url="http://agent/", mas_id=mas_id)
    service._app_service.create_app.return_value = agent_app
    service._app_service.get_mas_apps.return_value = [agent_app]
    service._k8s_mas_repository.create_mas.return_value = None

    with patch.object(service, "_discover_and_register_tools") as mock_drt:
        service.create_mas_from_crd(_make_mas_create_request(AppType.AGENT))
        mock_drt.assert_not_called()
