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

"""Tool access check implementations."""

from dataclasses import dataclass

from casa_auth_server.checks.base import BaseToolCheck, CheckResult, Payload
from casa_auth_server.core.events import MCPToolBlockingReason, MCPToolBlockingType
from casa_auth_server.core.types import ToolCheckFlags
from casa_auth_server.pipelines.conversation.tbac_components import TaskToolMatcherInput, TaskToToolMatcher


@dataclass(frozen=True)
class ToolSelectedDeterministicCheck(BaseToolCheck):
    """Check that verifies the tool was selected by the LLM."""

    flag = ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED

    def is_satisfied(self, payload: Payload) -> CheckResult:
        """Check if the requested tool was selected by the LLM."""
        check_result = CheckResult(satisfied=True)
        if payload.requested_tool not in payload.llm_selected_tools:
            check_result.satisfied = False
            check_result.blocking_type = MCPToolBlockingType.DETERMINISTIC
            check_result.blocking_reason = MCPToolBlockingReason.TOOL_NOT_SELECTED_BY_LLM

        return check_result


@dataclass(frozen=True)
class LlmSelectedToolsDeterministicCheck(BaseToolCheck):
    """Check that verifies the LLM selected at least one tool."""

    flag = ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS

    def is_satisfied(self, payload: Payload) -> CheckResult:
        """Check if the LLM selected at least one tool."""
        check_result = CheckResult(satisfied=True)
        if len(payload.llm_selected_tools) == 0:
            check_result.satisfied = False
            check_result.blocking_type = MCPToolBlockingType.DETERMINISTIC
            check_result.blocking_reason = MCPToolBlockingReason.NO_LLM_CALLS_MADE_BY_APP

        return check_result


class ToolIntentAICheck(BaseToolCheck):
    """AI-powered check that verifies tool matches user intent."""

    flag = ToolCheckFlags.AI_POWERED_TOOL_MATCH

    def __init__(self, task_tool_matcher: TaskToToolMatcher):
        """Initialize with a task-tool matcher."""
        self.task_tool_matcher = task_tool_matcher

    def is_satisfied(self, payload: Payload):
        """Check if the tool matches the user's intent using AI."""
        check_result = CheckResult(satisfied=True)

        tool_description: str = ""
        for tool in payload.mcp_server.tools:
            if tool.name == payload.requested_tool:
                tool_description = tool.description
                break

        match = self.task_tool_matcher.match_task_to_tool(
            TaskToolMatcherInput(
                task=payload.user_input.prompt,
                tool_name=payload.requested_tool,
                tool_description=tool_description,
            )
        )
        if not match or not match.appropriate:
            # TODO: store them for caching purposes?
            check_result.satisfied = False
            check_result.blocking_type = MCPToolBlockingType.AI_POWERED
            check_result.blocking_reason = MCPToolBlockingReason.TOOL_INTENT_MISMATCH
            check_result.reasoning = match.reasoning if match else "match_task_to_tool() returned None"

        return check_result
