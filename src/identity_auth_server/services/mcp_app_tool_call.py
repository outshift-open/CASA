"""Service layer for MCP app tool call operations."""

from abc import ABC, abstractmethod

from identity_auth_server.core.llm_app_response.repository import LlmAppResponseRepository
from identity_auth_server.core.mcp_app_tool_call.repository import McpAppToolCallRepository
from identity_auth_server.core.mcp_app_tool_call.types import BlockedByTypeName, McpAppToolCall, McpAppToolCallInput
from identity_auth_server.core.source_app_call.repository import SourceAppCallRepository
from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import TaskToolMatcher
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchInput
from identity_auth_server.sdk.types import LlmAppResponse, SourceAppCall


class McpAppToolCallService(ABC):
    """Interface for McpAppToolCallService."""

    def __init__(
        self,
        mcp_app_tool_call_repository: McpAppToolCallRepository,
        llm_app_response_repository: LlmAppResponseRepository,
        source_app_call_repository: SourceAppCallRepository,
        task_tool_matcher: TaskToolMatcher,
    ):
        """Initialize the service with the necessary repositories and matchers."""
        self.mcp_app_tool_call_repository = mcp_app_tool_call_repository
        self.llm_app_response_repository = llm_app_response_repository
        self.source_app_call_repository = source_app_call_repository
        self.task_tool_matcher = task_tool_matcher

    @abstractmethod
    def create_mcp_app_tool_call(self, mcp_app_tool_call: McpAppToolCallInput) -> McpAppToolCall:
        """Create a new MCP app tool call."""
        pass


class McpAppToolCallServiceImpl(McpAppToolCallService):
    """Implementation of the McpAppToolCallService."""

    def create_mcp_app_tool_call(self, mcp_app_tool_call: McpAppToolCallInput) -> McpAppToolCall:
        """Create a new MCP app tool call."""
        # retrieve all LLM responses associated with the given llm_app_call_token
        responses: list[LlmAppResponse] = []
        if mcp_app_tool_call.llm_app_call_token is not None:
            responses = self.llm_app_response_repository.get_llm_app_response_by_token(
                mcp_app_tool_call.llm_app_call_token
            )

        # if no responses found, create and return the MCP app tool call with blocked=True
        if len(responses) == 0:
            resp = self.mcp_app_tool_call_repository.create(
                mcp_app_tool_call,
                blocked=True,
                blocked_by_type_id=str(
                    self.mcp_app_tool_call_repository.get_blocked_by_type_by_name(
                        name=BlockedByTypeName.NO_LLM_CALLS_MADE_BY_APP,
                    ).id
                ),
            )

            return resp

        # search for "name='tool'" in each response's tool_calls field, which is a plain string
        tool_found = False
        for response in responses:
            if response.tool_calls:
                pattern = "name='" + mcp_app_tool_call.tool + "'"
                print(f"Checking for pattern {pattern} in tool_calls")
                print(f"Tool call content: {response.tool_calls}")
                if pattern in response.tool_calls:
                    tool_found = True
                    break

        # if tool not found, block with appropriate reason
        if not tool_found:
            return self.mcp_app_tool_call_repository.create(
                mcp_app_tool_call,
                blocked=True,
                blocked_by_type_id=str(
                    self.mcp_app_tool_call_repository.get_blocked_by_type_by_name(
                        name=BlockedByTypeName.TOOL_NOT_SELECTED_BY_LLM,
                    ).id
                ),
            )

        # Non-deterministic checks for task-tool intent

        # Retrieve the task from the source app call associated with this MCP app tool call
        source_app_calls: list[SourceAppCall] = []
        source_app_calls = self.source_app_call_repository.get_by_source_app_call_token(
            token=mcp_app_tool_call.source_app_call_token
        )
        if len(source_app_calls) == 0:
            raise Exception("Source app call not found for token: " + mcp_app_tool_call.source_app_call_token)
        if len(source_app_calls) > 1:
            raise Exception("Multiple source app calls found for token: " + mcp_app_tool_call.source_app_call_token)
        source_app_call = source_app_calls[0]
        task = source_app_call.input

        # Validate task-tool intent match
        task_tool_match_output = self.task_tool_matcher.match(
            input=TaskToolMatchInput(
                task=task,
                requested_tool=mcp_app_tool_call.tool,
                mcp_server=mcp_app_tool_call.mcp_server,
            )
        )

        # if tool intent does not match, block with appropriate reason
        if not task_tool_match_output.task_tool_match:
            return self.mcp_app_tool_call_repository.create(
                mcp_app_tool_call,
                blocked=True,
                blocked_by_type_id=str(
                    self.mcp_app_tool_call_repository.get_blocked_by_type_by_name(
                        name=BlockedByTypeName.TOOL_INTENT_MISMATCH,
                    ).id
                ),
            )

        # all checks passed, create unblocked tool call
        return self.mcp_app_tool_call_repository.create(mcp_app_tool_call)
