"""Service layer for sessions."""

import logging
from abc import ABC, abstractmethod

import jwt

from identity_auth_server.core.client.repository import ClientRepository
from identity_auth_server.core.client.types import ClientInput
from identity_auth_server.core.token.repository import TokenRepository
from identity_auth_server.core.token.types import (ActorClaim,
                                                   TokenIntrospectParams,
                                                   TokenIntrospectResponse,
                                                   TokenRequestParams,
                                                   TokenResponse)
from identity_auth_server.thirdparty.idp.keycloak.keycloak import \
    KeycloakManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class AuthorizationServerService(ABC):
    """Interface defining AS service methods."""

    def __init__(
        self,
        authorization_server_repository: AuthorizationServerRepository,
        keycloak_manager: KeycloakManager,
        client_repository: ClientRepository,
    ):
        """Initialize the service with its dependencies."""
        self.authorization_server_repository = authorization_server_repository
        self.keycloak_manager = keycloak_manager
        self.client_repository = client_repository

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

    def __init__(
        self, token_repository: TokenRepository, keycloak_manager: KeycloakManager, client_repository: ClientRepository
    ):
        """Store the backing session repository, keycloak manager, and client repository."""
        super().__init__(token_repository, keycloak_manager, client_repository)

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
        # Check if client exists in the database
        existing_client = self.client_repository.get_by_client_id(data.client_id)

        if existing_client:
            keycloak_client = existing_client
            logger.debug(f"Found existing client in DB: {keycloak_client}")
        else:
            # Create client in Keycloak
            keycloak_response = self.keycloak_manager.create_client(data.client_id)

            # Store client in database
            client_input = ClientInput(
                client_id=keycloak_response["clientId"],
                name=keycloak_response["name"],
                secret=keycloak_response.get("secret"),
            )
            keycloak_client = self.client_repository.create(client_input)
            logger.debug(f"Created new client: {keycloak_client}")

        data_tools = data.tools if data.tools else []
        data_act = data.act if data.act else None
        data_input_id = data.input_id if data.input_id else ""
        data_sub = data.sub if data.sub else keycloak_client.client_id
        data_scopes = data.scopes if data.scopes else []
        data_type = data.type if data.type else "source"

        # Get a access_token from keycloak
        keycloak_token = self.keycloak_manager.get_token(
            client_id=keycloak_client.client_id,
            client_secret=keycloak_client.secret if keycloak_client.secret else "",
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
