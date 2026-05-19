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

"""Service layer for sessions."""

import json
import logging
import re
from typing import Self
from urllib.parse import urlparse

import jwt
from pydantic import BaseModel, field_validator, model_validator

from casa_auth_server.checks.base import Payload
from casa_auth_server.checks.factory import ToolCheckFactory
from casa_auth_server.core.events import (
    AgentCallStartedEvent,
    LLMCallEndedEvent,
    MCPCallStartedEvent,
    MCPToolBlockingReason,
    MCPToolBlockingType,
    TokenExchangedEvent,
    TokenIssuedEvent,
)
from casa_auth_server.core.idp.idp_client import IdpClient
from casa_auth_server.core.repositories.app import AppRepository
from casa_auth_server.core.repositories.authorization_server import AuthorizationServerRepository
from casa_auth_server.core.repositories.user_input import UserInputRepository
from casa_auth_server.core.types import (
    ActorClaim,
    AppType,
    ClientCredentials,
    TokenIntrospectResponse,
    TokenResponse,
    ToolCheckFlags,
    UserInput,
)
from casa_auth_server.pipelines.conversation.tbac_components import TaskExtractor
from casa_auth_server.services.mcp_discover import McpDiscoverService
from casa_auth_server.telemetry.tracer import Tracer

logger = logging.getLogger(__name__)


class TokenRequest(BaseModel):
    """A model representing a token generation request."""

    client_id: str
    client_secret: str
    user_input: str | None = None
    user_input_id: str | None = None

    @model_validator(mode="after")
    def validate_user_input(self) -> Self:
        if (not self.user_input or self.user_input == "") and (not self.user_input_id or self.user_input_id == ""):
            raise ValueError("Either user_input or user_input_id must be provided.")
        return self


class TokenExchangeRequest(BaseModel):
    """A model representing a token exchange request."""

    client_id: str
    client_secret: str
    subject_token: str
    subject_token_type: str
    scope: str | None = None
    mcp_server_url: str | None = None
    tools: list[str] | None = []

    @field_validator("subject_token_type", mode="before")
    def validate_subject_token_type(cls, v: str) -> str:  # noqa: N805
        """Validate the value of the subject_token_type field."""
        supported_types = ["urn:ietf:params:oauth:token-type:access_token"]
        if v not in supported_types:
            raise ValueError(f"{v} is not supported, supported types: {supported_types}.")
        return v


class ProcessedTool(BaseModel):
    """Object that holds the processed tool info."""

    name: str
    blocked: bool = False
    blocking_type: MCPToolBlockingType | None = None
    blocking_reason: MCPToolBlockingReason | None = None


class AuthorizationServerService:
    """Concrete implementation of AuthorizationServerService."""

    def __init__(
        self,
        authorization_server_repository: AuthorizationServerRepository,
        app_repository: AppRepository,
        idp_client: IdpClient,
        mcp_discover: McpDiscoverService,
        user_input_repository: UserInputRepository,
        tracer: Tracer,
        tool_check_factory: ToolCheckFactory,
        task_extractor: TaskExtractor,
    ):
        """Initialize the service with its dependencies."""
        self.authorization_server_repository = authorization_server_repository
        self.app_repository = app_repository
        self.idp_client = idp_client
        self.mcp_discover = mcp_discover
        self.user_input_repository = user_input_repository
        self.tracer = tracer
        self.tool_check_factory = tool_check_factory
        self.task_extractor = task_extractor

    def generate_token_oauth(self, app_id: str, request: TokenRequest) -> TokenResponse:
        """Generate a new token with client_credential grant type for a trusted App (Clients)."""
        app = self.app_repository.get_app_by_id(app_id)
        if app is None:
            raise Exception(f"App with id {app_id} not found.")

        if app.mas is None:
            raise Exception(f"App {app_id} does not belong to a Multi Agent System.")

        if app.mas.authorization_server is None:
            raise Exception(f"App {app_id} has no authorization server configured.")

        user_input: UserInput | None = None
        task: str | None = None
        if request.user_input and request.user_input != "":
            try:
                task = self.task_extractor.extract_task(request.user_input)
                if task is None:
                    logger.error("task is none, fallbacking to the whole conversation")
            except Exception as e:
                logger.error(
                    f"failed to extract the task from the conversation, fallbacking to the whole conversation: {e}"
                )

            if task is None:
                task = "No task detected"

            # store the user initial prompt
            user_input = self.user_input_repository.create(
                UserInput(
                    prompt=task,
                    app_id=app.id,
                )
            )
        elif request.user_input_id and request.user_input_id != "":
            user_input = self.user_input_repository.get_by_id(request.user_input_id)
            if user_input is None:
                raise Exception(f"User Input with id {request.user_input_id} not found.")
        else:
            raise Exception("User Input must be provided")

        token_payload = self.idp_client.get_token(
            app.mas.authorization_server,
            client_creds=ClientCredentials(client_id=request.client_id, client_secret=request.client_secret),
            sub=request.client_id,
            act=None,
            scopes=[],
            extra={},
            user_input_id=str(user_input.id),
        )

        access_token = token_payload.token["access_token"]

        logger.debug(f"Got token from Keycloak {access_token}")

        self.tracer.record_event(
            TokenIssuedEvent(
                user_input_id=str(user_input.id),
                token=access_token,
                app_id=app_id,
                mas_id=str(app.mas_id),
                prompt=user_input.prompt,
            )
        )

        return TokenResponse(access_token=access_token, token_type="Bearer")

    def exchange_token(self, app_id: str, request: TokenExchangeRequest) -> TokenResponse:
        """Perform a token exchange and generate a JWT."""
        subject_token = self.introspect_token(token=request.subject_token)
        subject_app = self.app_repository.get_app_by_id(subject_token.app_id if subject_token.app_id else "")
        if subject_app is None:
            raise Exception("Invalid subject_token.")

        actor_app = self.app_repository.get_app_by_id(app_id)
        if actor_app is None:
            raise Exception(f"App with id {app_id} not found.")

        if actor_app.mas is None:
            raise Exception(f"App {app_id} does not belong to a Multi Agent System.")

        if actor_app.mas.authorization_server is None:
            raise Exception(f"App {actor_app.id} has no authorization server configured.")

        processed_tools = self._process_requested_tools(request, subject_token, actor_app.mas.enabled_tool_checks)
        approved_tools = [tool.name for tool in processed_tools if not tool.blocked]

        act = ActorClaim(sub=request.client_id)
        if subject_token.act:
            act.act = subject_token.act

        scopes: list[str] = []
        if request.scope:
            scopes = [s for s in request.scope.split(" ") if s]

        if approved_tools:
            scopes.append("call-tools")

        if subject_token.sub is None:
            raise Exception("Invalid subject_token: missing sub.")
        if subject_token.user_input_id is None:
            raise Exception("Invalid subject_token: missing user_input_id.")

        actor_token = self.idp_client.get_token(
            actor_app.mas.authorization_server,
            client_creds=ClientCredentials(client_id=request.client_id, client_secret=request.client_secret),
            sub=subject_token.sub,
            act=act,
            scopes=scopes,
            user_input_id=subject_token.user_input_id,
            tools=approved_tools,
        )

        token = actor_token.token["access_token"]

        logger.debug(f"Got token from Keycloak {token}")

        self.tracer.record_event(
            TokenExchangedEvent(
                user_input_id=subject_token.user_input_id,
                subject_token=request.subject_token,
                act_token=token,
                subject_app_id=str(subject_app.id),
                act_app_id=str(actor_app.id),
                mas_id=str(actor_app.mas_id),
                tools=approved_tools,
            )
        )

        if actor_app.type == AppType.AGENT:
            agent_call_event = AgentCallStartedEvent(
                user_input_id=subject_token.user_input_id,
                token=token,
                callee_app_id=str(actor_app.id),
                caller_app_id=self._get_app_id_from_client_id(subject_token.act.sub)
                if (subject_token.act is not None)
                else subject_token.app_id,
                mas_id=str(actor_app.mas_id),
            )
            self.tracer.record_event(agent_call_event)

        for tool in processed_tools:
            mcp_call_event = MCPCallStartedEvent(
                user_input_id=subject_token.user_input_id,
                token=token,
                tool=tool.name,
                callee_app_id=str(actor_app.id),
                caller_app_id=self._get_app_id_from_client_id(subject_token.act.sub)
                if (subject_token.act is not None)
                else subject_token.app_id,
                mas_id=str(actor_app.mas_id),
                blocked=tool.blocked,
                blocking_type=tool.blocking_type,
                blocking_reason=tool.blocking_reason,
            )
            self.tracer.record_event(mcp_call_event)

        return TokenResponse(access_token=token)

    def _process_requested_tools(
        self,
        request: TokenExchangeRequest,
        subject_token: TokenIntrospectResponse,
        tool_check_flags: ToolCheckFlags | None,
    ) -> list[ProcessedTool]:
        processed_tools = []

        if tool_check_flags is None:
            return []

        if request.mcp_server_url and request.tools and subject_token.user_input_id:
            mcp_server = self.mcp_discover.discover_mcp_tools(request.mcp_server_url)
            user_input = self.user_input_repository.get_by_id(subject_token.user_input_id)
            traces = self.tracer.get_traces_by_user_input_and_event_type(
                subject_token.user_input_id,
                LLMCallEndedEvent.__name__,
            )
            llm_selected_tools: list[str] = []
            for trace in traces:
                event = LLMCallEndedEvent(**trace.event)
                if event.token != request.subject_token or event.tools is None:
                    continue
                matches = re.findall(r"name='(.*?)'", event.tools)
                if matches:
                    llm_selected_tools = llm_selected_tools + list(set(matches))
            for tool in list(set(request.tools)):
                processed_tool = ProcessedTool(name=tool)
                processed_tools.append(processed_tool)

                tool_check = self.tool_check_factory.get_tool_check(tool_check_flags)
                check_result = tool_check.is_satisfied(
                    payload=Payload(
                        llm_selected_tools=llm_selected_tools,
                        requested_tool=tool,
                        mcp_server=mcp_server,
                        user_input=user_input,
                    )
                )

                if check_result.satisfied:
                    processed_tool.blocked = False
                else:
                    processed_tool.blocked = True
                    processed_tool.blocking_type = check_result.blocking_type
                    processed_tool.blocking_reason = check_result.blocking_reason

        return processed_tools

    def introspect_token(self, token: str, tools: list[str] | None = None) -> TokenIntrospectResponse:
        """Introspect a token to check its validity and retrieve metadata."""
        # Decrypt the JWT token and extract claims without using Keycloak
        claims = jwt.decode(token, options={"verify_signature": False})
        sub = claims.get("sub")

        logger.debug("Introspecting token claims")

        app_id = self._get_app_id_from_client_id(sub)

        # The app in the sub must be a trusted client
        sub_app = self.app_repository.get_app_by_id(app_id)
        if sub_app is None or sub_app.type == AppType.MCP_SERVER:
            return TokenIntrospectResponse(active=False)

        mas_id = str(sub_app.mas_id) if sub_app.mas_id else None

        act: ActorClaim | None = None
        act_str = claims.get("act")
        if act_str:
            act = ActorClaim.model_validate_json(act_str)

        tools_claim: list[str] = []
        if claims.get("tools"):
            tools_claim = json.loads(claims.get("tools"))

        if act:
            act_app_id = self._get_app_id_from_client_id(act.sub)
            app_id = act_app_id
            act_sub_app = self.app_repository.get_app_by_id(act_app_id)
            if act_sub_app and act_sub_app.type == AppType.MCP_SERVER and tools:
                if not set(tools).issubset(tools_claim):
                    return TokenIntrospectResponse(active=False)
            if act_sub_app and act_sub_app.mas_id:
                mas_id = str(act_sub_app.mas_id)

        return TokenIntrospectResponse(
            sub=sub,
            client_id=claims.get("client_id"),
            scope=claims.get("scope"),
            exp=claims.get("exp"),
            act=act,
            user_input_id=claims.get("uiid"),
            app_id=app_id,
            mas_id=mas_id,
            tools=tools_claim,
            active=True,
        )

    def _get_app_id_from_client_id(self, client_id: str) -> str:
        parse_result = urlparse(client_id)
        return next(path for path in parse_result.path.split("/") if path)
