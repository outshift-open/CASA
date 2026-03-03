"""Tool access check implementations."""

from dataclasses import dataclass

from identity_auth_server.checks.base import BaseToolCheck, CheckResult, Payload
from identity_auth_server.core.events import MCPToolBlockingReason, MCPToolBlockingType
from identity_auth_server.core.types import ToolCheckFlags
from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import TaskToolMatcher
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchInput


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

    def __init__(self, task_tool_matcher: TaskToolMatcher):
        """Initialize with a task-tool matcher."""
        self.task_tool_matcher = task_tool_matcher

    def is_satisfied(self, payload: Payload):
        """Check if the tool matches the user's intent using AI."""
        check_result = CheckResult(satisfied=True)
        match = self.task_tool_matcher.match(
            TaskToolMatchInput(
                task=payload.user_input.prompt,
                requested_tool=payload.requested_tool,
                mcp_server=payload.mcp_server,
            )
        )
        if not match.task_tool_match:
            # TODO: store them for caching purposes?
            check_result.satisfied = False
            check_result.blocking_type = MCPToolBlockingType.AI_POWERED
            check_result.blocking_reason = MCPToolBlockingReason.TOOL_INTENT_MISMATCH

        return check_result
