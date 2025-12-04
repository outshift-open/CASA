"""Service layer for sessions."""

import logging
from abc import ABC, abstractmethod

import jwt

from identity_auth_server.core.repositories.app import AppRepository
from identity_auth_server.core.repositories.authorization_server import AuthorizationServerRepository
from identity_auth_server.core.types import (
    App,
    AppMetadataResponse,
    AuthorizationServer,
    ClientCredentials,
    TokenIntrospectParams,
    TokenIntrospectResponse,
    TokenRequestParams,
    TokenResponse,
)
from identity_auth_server.thirdparty.idp.keycloak.keycloak import KeycloakManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class AuthorizationServerService(ABC):
    """Interface defining AS service methods."""

    def __init__(
        self,
        authorization_server_repository: AuthorizationServerRepository,
        app_repository: AppRepository,
        keycloak_manager: KeycloakManager,
        api_url: str,
    ):
        """Initialize the service with its dependencies."""
        self.authorization_server_repository = authorization_server_repository
        self.app_repository = app_repository
        self.keycloak_manager = keycloak_manager
        self.api_url = api_url

    @abstractmethod
    def create_for_app(self, app: App) -> App:
        """Create a new authorization server for an App."""

    @abstractmethod
    def app_metadata(self, app_id: str) -> AppMetadataResponse:
        """Generate app metadata response."""

    @abstractmethod
    def generate_token(self, data: TokenRequestParams, source: App | None) -> TokenResponse:
        """Generate a new token based on the request parameters and source App."""

    @abstractmethod
    def introspect_token(self, data: TokenIntrospectParams) -> TokenIntrospectResponse:
        """Introspect a token to check its validity and retrieve metadata."""


class AuthorizationServerServiceImpl(AuthorizationServerService):
    """Concrete implementation of TokenService."""

    def __init__(
        self,
        authorization_server_repository: AuthorizationServerRepository,
        app_repository: AppRepository,
        keycloak_manager: KeycloakManager,
        api_url: str,
    ):
        """Store the backing session repository, keycloak manager, and client repository."""
        super().__init__(authorization_server_repository, app_repository, keycloak_manager, api_url)

    def create_for_app(self, app: App) -> App:
        """Create a new authorization server for an App."""
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

        self.keycloak_manager.create_client_credentials(authorization_server, client_credentials)

        # Add all scopes from the app to the authorization server
        self.keycloak_manager.add_authorization_server_scopes(
            authorization_server,
            scopes=list(map(lambda t: "call_" + str(t.id), app.tools)),
        )

        # Add AuthorizationServer and ClientCredentials to the app
        app.authorization_server_id = authorization_server.id
        app.client_credentials_id = client_credentials.id

        return app

    def app_metadata(self, app_id: str) -> AppMetadataResponse:
        """Generate app metadata response."""
        # Get app
        app = self.app_repository.get_app_by_id(app_id)

        return AppMetadataResponse(
            client_name=app.name,
            client_id=f"{self.api_url}/{app.id}/oauth2/client-metadata.json",
            grant_types=["client_credentials"],
            response_types=["token"],
            token_endpoint_auth_method="private_key_jwt",
            jwks_uri=f"{self.api_url}/{app.id}/oauth2/.well-known/jwks.json",
        )

    def generate_token(self, authorization_server: AuthorizationServer, data: TokenRequestParams) -> TokenResponse:
        """Generate a new token based on the request parameters."""
        client_credentials = self.authorization_server_repository.find_client_credentials_by_client_id(data.client_id)

        data_act = data.act if data.act else None
        data_extra = data.extra if data.other else {}
        data_sub = data.sub if data.sub else client_credentials.client_id
        data_scopes = data.scopes if data.scopes else []

        # Get a access_token from keycloak
        keycloak_token = self.keycloak_manager.get_token(
            authorization_server,
            client_credentials,
            sub=data_sub,
            act=data_act,
            scopes=data_scopes,
            extra=data_extra,
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
            act=claims.get("act"),
            extra=claims.get("extra"),
        )
