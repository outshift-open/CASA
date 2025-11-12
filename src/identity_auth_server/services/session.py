"""Service layer for sessions."""

import re
from abc import ABC, abstractmethod
from uuid import uuid4

from identity_auth_server.core.llm_app_response.repository import LlmAppResponseRepository
from identity_auth_server.core.session.repository import SessionRepository
from identity_auth_server.core.session.types import (
    SessionLlmAppInput,
    SessionLlmAppOutput,
    SessionMcpAppInput,
    SessionMcpAppOutput,
    SessionSourceAppInput,
    SessionSourceAppOutput,
)
from identity_auth_server.core.token.types import ActorClaim, TokenIntrospectParams, TokenRequestParams
from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import TaskToolMatcher
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchInput
from identity_auth_server.services.mcp_discover import McpDiscoverService
from identity_auth_server.services.token import TokenService


class SessionService(ABC):
    """Interface defining trace service methods."""

    def __init__(
        self,
        session_repository: SessionRepository,
        llm_app_response_repository: LlmAppResponseRepository,
        token_service: TokenService,
        mcp_discover_service: McpDiscoverService,
        task_tool_matcher: TaskToolMatcher,
    ):
        """Initialize the service with a session repository."""
        self.session_repository = session_repository
        self.llm_app_response_repository = llm_app_response_repository
        self.token_service = token_service
        self.mcp_discover_service = mcp_discover_service
        self.task_tool_matcher = task_tool_matcher

    @abstractmethod
    def create_source_app_session(self, input: SessionSourceAppInput, data: TokenRequestParams) -> str:
        """Create a new source app session and return its token."""
        pass

    @abstractmethod
    def create_llm_app_session(self, input: SessionLlmAppInput, data: TokenRequestParams) -> str:
        """Create a new llm app session and return its token."""
        pass

    @abstractmethod
    def create_mcp_app_session(self, input: SessionMcpAppInput, data: TokenRequestParams) -> str:
        """Create a new mcp app session and return its token."""
        pass

    @abstractmethod
    def validate_source_app_call_token(self, source_app_call_token: str) -> SessionSourceAppOutput:
        """Validate a source app call token."""
        pass

    @abstractmethod
    def validate_llm_app_call_token(self, llm_app_call_token: str) -> SessionLlmAppOutput:
        """Validate an llm app call token."""
        pass

    @abstractmethod
    def validate_mcp_app_call_token(self, mcp_app_call_token: str) -> SessionMcpAppOutput:
        """Validate an mcp app call token."""
        pass


class SessionServiceImpl(SessionService):
    """Concrete implementation of SessionService."""

    def __init__(
        self,
        session_repository: SessionRepository,
        llm_app_response_repository: LlmAppResponseRepository,
        token_service: TokenService,
        mcp_discover_service: McpDiscoverService,
        task_tool_matcher: TaskToolMatcher,
    ):
        """Store the backing session repository."""
        super().__init__(
            session_repository, llm_app_response_repository, token_service, mcp_discover_service, task_tool_matcher
        )

    def create_source_app_session(self, input: SessionSourceAppInput, data: TokenRequestParams) -> str:
        """Create a new source app session and return its token."""
        input_id = uuid4()
        data.input_id = str(input_id)
        input.input_id = str(input_id)

        token_response = self.token_service.generate_token(data)
        access_token = token_response.access_token
        return self.session_repository.create_source_app_session(input, access_token)

    def create_llm_app_session(self, input: SessionLlmAppInput, data: TokenRequestParams) -> str:
        """Create a new llm app session and return its token."""
        # Validate the source app call token exists and extract the client_id
        source_session_output = self.session_repository.validate_source_app_call_token(input.source_app_call_token)
        if not source_session_output.valid:
            raise ValueError("Invalid source app call token")

        # Add the client_id to the token request params as ActorClaim
        token_values = self.token_service.introspect_token(TokenIntrospectParams(token=input.source_app_call_token))
        data.act = ActorClaim(sub=token_values.client_id)
        data.input = token_values.input
        data.input_id = token_values.input_id

        token_response = self.token_service.generate_token(data)
        access_token = token_response.access_token
        return self.session_repository.create_llm_app_session(input, access_token)

    def create_mcp_app_session(self, input: SessionMcpAppInput, data: TokenRequestParams) -> str:
        """Create a new mcp app session and return its token."""
        # Validate the source app call token exists and extract the client_id
        source_session_output = self.session_repository.validate_source_app_call_token(input.source_app_call_token)
        if not source_session_output.valid:
            raise ValueError("Invalid source app call token")

        # Add the client_id to the token request params as ActorClaim
        token_values = self.token_service.introspect_token(TokenIntrospectParams(token=input.source_app_call_token))
        data.act = ActorClaim(sub=token_values.client_id)
        data.input = token_values.input
        data.input_id = token_values.input_id

        # Validate the llm app call token exists and find all tool calls associated with it
        llm_session_output = self.session_repository.validate_llm_app_call_token(input.llm_app_call_token)
        if not llm_session_output.valid:
            raise ValueError("Invalid llm app call token")

        # Retrieve tools for the llm app call token
        llm_app_responses = self.llm_app_response_repository.get_llm_app_response_by_token(input.llm_app_call_token)

        llm_tool_calls: list[str] = []
        for response in llm_app_responses:
            tool_calls = response.tool_calls

            # regex to extract tool names from tool_calls if needed (name='add') etc.
            regex = r"name='(.*?)'"
            matches = re.findall(regex, str(tool_calls))

            # append only if matches found
            if matches:
                llm_tool_calls = llm_tool_calls + matches

        # remove duplicates
        requested_tools = list(set(llm_tool_calls))

        # Get existing tool approvals from database
        existing_tools = self.session_repository.get_tools_for_source_app_session(input.source_app_call_token)
        existing_tools_dict = {tool_name: approved for tool_name, approved in existing_tools}

        # for each tool, check if it exists in database, otherwise validate with task tool matcher
        mcp_server_url = input.mcp_server_url
        if mcp_server_url is None:
            raise ValueError("MCP server URL is required for MCP app session creation")

        mcp_server = self.mcp_discover_service.discover_mcp_tools(mcp_server_url)

        approved_tools = []
        for tool in requested_tools:
            if tool in existing_tools_dict:
                # Use existing approval from database
                approved = existing_tools_dict[tool]
                if approved:
                    approved_tools.append(tool)
            else:
                # Use task tool matcher for new tools
                match = self.task_tool_matcher.match(
                    TaskToolMatchInput(
                        task=token_values.input,
                        requested_tool=tool,
                        mcp_server=mcp_server,
                    )
                )
                # Store the result in database (only if not already present)
                try:
                    self.session_repository.create_source_app_session_tools(
                        input.source_app_call_token, tool, match.task_tool_match
                    )
                except Exception as e:
                    # Tool may have been added by another concurrent request
                    print(f"Warning: Could not store tool approval for {tool}: {e}")

                if match.task_tool_match:
                    approved_tools.append(tool)

        data.tools = approved_tools

        token_response = self.token_service.generate_token(data)
        access_token = token_response.access_token
        return self.session_repository.create_mcp_app_session(input, access_token)

    def validate_source_app_call_token(self, source_app_call_token: str) -> SessionSourceAppOutput:
        """Validate a source app call token."""
        return self.session_repository.validate_source_app_call_token(source_app_call_token)

    def validate_llm_app_call_token(self, llm_app_call_token: str) -> SessionLlmAppOutput:
        """Validate an llm app call token."""
        return self.session_repository.validate_llm_app_call_token(llm_app_call_token)

    def validate_mcp_app_call_token(self, mcp_app_call_token: str) -> SessionMcpAppOutput:
        """Validate an mcp app call token."""
        return self.session_repository.validate_mcp_app_call_token(mcp_app_call_token)
