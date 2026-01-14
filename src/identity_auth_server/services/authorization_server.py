"""Service layer for sessions."""

import json
import logging
from typing import Optional
from urllib.parse import urlparse

import jwt
from pydantic import BaseModel, field_validator

from identity_auth_server.core.events import (
    MCPCallStartedEvent,
    MCPToolBlockingReason,
    MCPToolBlockingType,
    TokenExchangedEvent,
    TokenIssuedEvent,
)
from identity_auth_server.core.repositories.app import AppRepository
from identity_auth_server.core.repositories.authorization_server import AuthorizationServerRepository
from identity_auth_server.core.repositories.user_input import UserInputRepository
from identity_auth_server.core.types import (
    ActorClaim,
    App,
    AppMetadataResponse,
    AppType,
    AuthorizationServer,
    ClientCredentials,
    TokenIntrospectResponse,
    TokenResponse,
    UserInput,
)
from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import TaskToolMatcher
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchInput
from identity_auth_server.services.mcp_discover import McpDiscoverService
from identity_auth_server.telemetry.tracer import Tracer
from identity_auth_server.thirdparty.idp.keycloak import KeycloakManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class TokenRequest(BaseModel):
    """A model representing a token generation request."""

    client_id: str
    client_secret: str
    user_input: str


class TokenExchangeRequest(BaseModel):
    """A model representing a token exchange request."""

    client_id: str
    client_secret: str
    subject_token: str
    subject_token_type: str
    scope: Optional[str] = None
    mcp_server_url: Optional[str] = None
    tools: Optional[list[str]] = []

    @field_validator("subject_token_type", mode="before")
    def validate_subject_token_type(cls, v: str) -> str:  # noqa: N805
        """Validate the value of the subject_token_type field."""
        supported_types = ["urn:ietf:params:oauth:token-type:access_token"]
        if v not in supported_types:
            raise ValueError(f"{v} is not supported, supported types: {supported_types}.")
        return v


class AuthorizationServerService:
    """Concrete implementation of AuthorizationServerService."""

    def __init__(
        self,
        authorization_server_repository: AuthorizationServerRepository,
        app_repository: AppRepository,
        keycloak_manager: KeycloakManager,
        api_url: str,
        mcp_discover: McpDiscoverService,
        task_tool_matcher: TaskToolMatcher,
        user_input_repository: UserInputRepository,
        tracer: Tracer,
    ):
        """Store the backing session repository, keycloak manager, and client repository."""
        self.authorization_server_repository = authorization_server_repository
        self.app_repository = app_repository
        self.keycloak_manager = keycloak_manager
        self.api_url = api_url
        self.mcp_discover = mcp_discover
        self.task_tool_matcher = task_tool_matcher
        self.user_input_repository = user_input_repository
        self.tracer = tracer

    def create_for_app(self, app_id: str) -> App:
        """Create a new authorization server for an App."""
        app = self.app_repository.get_app_by_id(app_id)
        if app is None:
            raise Exception(f"App with id {app_id} not found.")

        # Create the authorization server object
        authorization_server = AuthorizationServer(
            realm=f"{app.name}-auth-server",
        )

        # Create the client_credentials object
        client_credentials = ClientCredentials(
            name=f"{app.name}-client-credentials", client_id=f"{self.api_url}/{app.id}/oauth2/client-metadata.json"
        )

        # Persist the authorization server
        authorization_server = self.authorization_server_repository.create_authorization_server(authorization_server)

        # Persist the client credentials
        client_credentials.authorization_server_id = authorization_server.id
        self.authorization_server_repository.create_client_credentials(client_credentials)

        logger.debug(f"Creating authorization server {authorization_server.id} for app {app.id}")

        # Create in Keycloak
        self.keycloak_manager.create_authorization_server(authorization_server)

        logger.debug(f"Creating client credentials in Keycloak for app {app.id}")

        client_credentials = self.keycloak_manager.create_client_credentials(authorization_server, client_credentials)
        # Add all scopes from the app to the authorization server
        self.keycloak_manager.add_authorization_server_scopes(
            authorization_server,
            scopes=list(map(lambda t: "call_" + str(t.id), app.tools)),
        )

        # Add AuthorizationServer and ClientCredentials to the app
        app.authorization_server_id = authorization_server.id
        app.client_credentials_id = client_credentials.id

        self.app_repository.update_app(app)

        return app

    def app_metadata(self, app_id: str) -> AppMetadataResponse:
        """Generate app metadata response."""
        # Get app
        app = self.app_repository.get_app_by_id(app_id)
        if app is None:
            raise Exception(f"App with id {app_id} not found.")

        return AppMetadataResponse(
            client_name=app.name,
            client_id=f"{self.api_url}/{app.id}/oauth2/client-metadata.json",
            grant_types=["client_credentials"],
            response_types=["token"],
            token_endpoint_auth_method="private_key_jwt",
            jwks_uri=f"{self.api_url}/{app.id}/oauth2/.well-known/jwks.json",
        )

    def generate_token_oauth(self, app_id: str, request: TokenRequest) -> TokenResponse:
        """Generate a new token with client_credential grant type for a trusted App (Clients)."""
        app = self.app_repository.get_app_by_id(app_id)
        if app is None:
            raise Exception(f"App with id {app_id} not found.")

        if app.authorization_server is None:
            raise Exception(f"App {app_id} has no authorization server configured.")

        # store the user initial prompt
        user_input = self.user_input_repository.create(
            UserInput(
                prompt=request.user_input,
                app_id=app.id,
            )
        )

        token = self.keycloak_manager.get_token(
            app.authorization_server,
            client_credentials=ClientCredentials(client_id=request.client_id, client_secret=request.client_secret),
            sub=request.client_id,
            act=None,
            scopes=[],
            extra={},
            user_input_id=str(user_input.id),
        )

        token = token["token"]["access_token"]

        logger.debug(f"Got token from Keycloak {token}")

        self.tracer.record_event(TokenIssuedEvent(user_input_id=str(user_input.id), token=token, app_id=str(app.id)))

        return TokenResponse(access_token=token, token_type="Bearer")

    def exchange_token(self, app_id: str, request: TokenExchangeRequest) -> TokenResponse:
        """Perform a token exchange and generate a JWT."""
        subject_token = self._introspect_token(token=request.subject_token)
        subject_app = self.app_repository.get_app_by_id(subject_token.app_id)
        if subject_app is None:
            raise Exception("Invalid subject_token.")

        actor_app = self.app_repository.get_app_by_id(app_id)
        if actor_app is None:
            raise Exception(f"App with id {app_id} not found.")

        if actor_app.authorization_server is None:
            raise Exception(f"App {actor_app.id} has no authorization server configured.")

        approved_tools = []
        mcp_call_event: Optional[MCPCallStartedEvent] = None

        # TODO: add deterministic check using the LLM response (from the events)
        if request.mcp_server_url and request.tools:
            mcp_server = self.mcp_discover.discover_mcp_tools(request.mcp_server_url)
            user_input = self.user_input_repository.get_by_id(subject_token.user_input_id)
            for tool in list(set(request.tools)):
                # TODO: add a check with existing approved tools (App.tools)
                match = self.task_tool_matcher.match(
                    TaskToolMatchInput(
                        task=user_input.prompt,
                        requested_tool=tool,
                        mcp_server=mcp_server,
                    )
                )
                # TODO: store them for caching purposes?
                if match.task_tool_match:
                    approved_tools.append(tool)
                    mcp_call_event = MCPCallStartedEvent(
                        user_input_id=subject_token.user_input_id,
                        tool=tool,
                        blocked=False,
                    )
                else:
                    mcp_call_event = MCPCallStartedEvent(
                        user_input_id=subject_token.user_input_id,
                        tool=tool,
                        blocked=True,
                        blocking_type=MCPToolBlockingType.AI_POWERED,
                        blocking_reason=MCPToolBlockingReason.TOOL_INTENT_MISMATCH,
                    )

        act = ActorClaim(sub=request.client_id)
        if subject_token.act:
            act.act = subject_token.act

        scopes: list[str] = []
        if request.scope:
            scopes = [s for s in request.scope.split("") if s]

        # TODO: add call-tool scope
        # if approved_tools:
        #     scopes.append("call-tools")

        actor_token = self.keycloak_manager.get_token(
            actor_app.authorization_server,
            client_credentials=ClientCredentials(client_id=request.client_id, client_secret=request.client_secret),
            sub=subject_token.sub,
            act=act,
            scopes=scopes,
            user_input_id=subject_token.user_input_id,
            tools=approved_tools,
        )

        token = actor_token["token"]["access_token"]

        logger.debug(f"Got token from Keycloak {token}")

        self.tracer.record_event(
            TokenExchangedEvent(
                user_input_id=subject_token.user_input_id,
                subject_token=request.subject_token,
                act_token=token,
                subject_app_id=str(subject_app.id),
                act_app_id=str(actor_app.id),
                tools=approved_tools,
            )
        )

        if mcp_call_event is not None:
            mcp_call_event.token = token
            mcp_call_event.callee_app_id = str(actor_app.id)
            if subject_token.act is not None:
                mcp_call_event.caller_app_id = self._get_app_id_from_client_id(subject_token.act.sub)
            else:
                mcp_call_event.caller_app_id = subject_token.app_id
            self.tracer.record_event(mcp_call_event)

        return TokenResponse(access_token=token)

    def introspect_token(
        self,
        # client_id: str,
        # client_secret: str,
        token: str,
        tools: Optional[list[str]] = None,
    ) -> TokenIntrospectResponse:
        response = self._introspect_token(token, tools)
        return response

    # def generate_token(self, authorization_server: AuthorizationServer, data: TokenRequestParams) -> TokenResponse:
    #     """Generate a new token based on the request parameters."""
    #     client_credentials = data.app.client_credentials
    #     act_client_credentials = data.act.client_credentials if data.act else None

    #     if client_credentials is None:
    #         raise Exception(f"App {data.app.id} has no client credentials.")

    #     # Get sub and act values
    #     sub = client_credentials.client_id
    #     act = None
    #     if act_client_credentials:
    #         sub = act_client_credentials.client_id
    #         act = ActorClaim(sub=client_credentials.client_id)

    #     scopes = []
    #     for tool in data.tools:
    #         scopes.append("call_" + str(tool.id))

    #     # Get a access_token from keycloak
    #     keycloak_token = self.keycloak_manager.get_token(
    #         authorization_server,
    #         client_credentials,
    #         sub=sub,
    #         act=act,
    #         scopes=scopes,
    #         extra=data.other if data.other else {},
    #     )

    #     keycloak_token = keycloak_token["token"]

    #     logger.debug(f"Got token from Keycloak {keycloak_token}")

    #     return TokenResponse(access_token=keycloak_token["access_token"], token_type="Bearer")

    def _introspect_token(self, token: str, tools: Optional[list[str]] = None) -> TokenIntrospectResponse:
        """Introspect a token to check its validity and retrieve metadata."""
        # Decrypt the JWT token and extract claims without using Keycloak
        claims = jwt.decode(token, options={"verify_signature": False})
        sub = claims.get("sub")

        app_id = self._get_app_id_from_client_id(sub)

        # The app in the sub must be a trusted client
        sub_app = self.app_repository.get_app_by_id(app_id)
        if sub_app is None or sub_app.type != AppType.CLIENT:
            return TokenIntrospectResponse(active=False)

        act: Optional[ActorClaim] = None
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

        return TokenIntrospectResponse(
            sub=sub,
            client_id=claims.get("client_id"),
            scope=claims.get("scope"),
            exp=claims.get("exp"),
            act=act,
            extra=claims.get("extra"),
            user_input_id=claims.get("uiid"),
            app_id=app_id,
            tools_claim=tools_claim,
            active=True,
        )

    def _get_app_id_from_client_id(self, client_id: str) -> str:
        parse_result = urlparse(client_id)
        return next(path for path in parse_result.path.split("/") if path)
