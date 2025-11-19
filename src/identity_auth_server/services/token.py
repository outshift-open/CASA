"""Service layer for sessions."""

import logging
from abc import ABC, abstractmethod
from typing import Any

import jwt
from pydantic import BaseModel

from identity_auth_server.core.token.repository import TokenRepository
from identity_auth_server.core.token.types import (
    ActorClaim,
    TokenIntrospectParams,
    TokenIntrospectResponse,
    TokenRequestParams,
    TokenResponse,
)
from identity_auth_server.thirdparty.idp.keycloak.keycloak import KeycloakManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Client(BaseModel):
    """Pydantic model for a client."""

    client_id: str
    name: str
    secret: str | None = None


class TokenService(ABC):
    """Interface defining token service methods."""

    def __init__(self, token_repository: TokenRepository, keycloak_manager: KeycloakManager):
        """Initialize the service with a token repository and keycloak manager."""
        self.token_repository = token_repository
        self.keycloak_manager = keycloak_manager

    @abstractmethod
    def generate_act_token(self, data: TokenRequestParams, source_client_id: str) -> TokenResponse:
        """Generate a new token with an 'act' claim for delegation."""
        pass

    @abstractmethod
    def generate_token(self, data: TokenRequestParams) -> TokenResponse:
        """Generate a new token based on the request parameters."""
        pass

    @abstractmethod
    def introspect_token(self, data: TokenIntrospectParams) -> TokenIntrospectResponse:
        """Introspect a token to check its validity and retrieve metadata."""
        pass


class TokenServiceImpl(TokenService):
    """Concrete implementation of TokenService."""

    def __init__(self, token_repository: TokenRepository, keycloak_manager: KeycloakManager):
        """Store the backing session repository and keycloak manager."""
        super().__init__(token_repository, keycloak_manager)
        self.clients_db: dict[Any, Any] = {}  # Temporary in-memory client storage

    def generate_act_token(self, data: TokenRequestParams, source_client_id: str) -> TokenResponse:
        """Generate a new token with an 'act' claim for delegation."""
        actor_token = self.generate_token(data).access_token

        # Introspect the actor token to get its claims, we need the sub
        actor_claims = self.introspect_token(TokenIntrospectParams(token=actor_token))

        # create a new act claim with the sub from the actor token
        act_claim = ActorClaim(
            sub=actor_claims.sub,
        )

        # replace the client id with the source client id, and set the act claim
        data.sub = source_client_id
        data.act = act_claim

        # generate a new token with the updated data
        return self.generate_token(data)

    def generate_token(self, data: TokenRequestParams) -> TokenResponse:
        """Generate a new token based on the request parameters."""
        # Create client

        # Check if client exists in our temp DB
        if data.client_id in self.clients_db:
            keycloak_client = self.clients_db[data.client_id]
            logger.debug(f"Found existing client in DB: {keycloak_client}")
        else:
            # Create client
            keycloak_client = self.keycloak_manager.create_client(data.client_id)

            # Store client in temp DB
            keycloak_client = Client(
                client_id=keycloak_client["clientId"],
                name=keycloak_client["name"],
                secret=keycloak_client.get("secret"),
            )
            self.clients_db[data.client_id] = keycloak_client

        data_tools = data.tools if data.tools else []
        data_act = data.act if data.act else None
        data_input_id = data.input_id if data.input_id else ""
        data_sub = data.sub if data.sub else keycloak_client.client_id
        data_scopes = data.scopes if data.scopes else []
        data_type = data.type if data.type else "source"

        # Get a access_token from keycloak
        keycloak_token = self.keycloak_manager.get_token(
            client_id=keycloak_client.client_id,
            client_secret=keycloak_client.secret,
            tools=data_tools,
            act=data_act,
            input_id=data_input_id,
            sub=data_sub,
            scopes=data_scopes,
            type=data_type,
        )

        keycloak_token = keycloak_token["token"]

        return TokenResponse(access_token=keycloak_token["access_token"], token_type="Bearer")

    def introspect_token(self, data: TokenIntrospectParams) -> TokenIntrospectResponse:
        """Introspect a token to check its validity and retrieve metadata."""
        # Decrypt the JWT token and extract claims without using Keycloak
        claims = jwt.decode(data.token, options={"verify_signature": False})

        return TokenIntrospectResponse(
            sub=claims.get("sub"),
            client_id=claims.get("client_id"),
            scope=claims.get("scope"),
            exp=claims.get("exp"),
            tools=claims.get("tools"),
            act=claims.get("act"),
            input_id=claims.get("input_id"),
        )
