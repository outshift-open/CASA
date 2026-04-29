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

"""Unit tests for deterministic tool access checks."""

from mcp import types as mcp_types

from casa_auth_server.checks.base import Payload
from casa_auth_server.checks.checks import LlmSelectedToolsDeterministicCheck, ToolSelectedDeterministicCheck
from casa_auth_server.core.types import UserInput
from casa_auth_server.types import McpServer


def _payload(requested_tool: str, llm_selected_tools: list[str]) -> Payload:
    tool = mcp_types.Tool(name=requested_tool, inputSchema={})
    server = McpServer(name="test-server", tools=[tool], resources=[])
    user_input = UserInput(prompt="do something", tag=None)
    return Payload(
        llm_selected_tools=llm_selected_tools,
        requested_tool=requested_tool,
        mcp_server=server,
        user_input=user_input,
    )


def test_llm_selected_tools_check_unsatisfied_when_no_tools() -> None:
    payload = _payload(requested_tool="read_file", llm_selected_tools=[])
    result = LlmSelectedToolsDeterministicCheck().is_satisfied(payload)
    assert not result.satisfied


def test_tool_selected_check_satisfied_when_tool_present() -> None:
    payload = _payload(requested_tool="read_file", llm_selected_tools=["read_file", "write_file"])
    result = ToolSelectedDeterministicCheck().is_satisfied(payload)
    assert result.satisfied
