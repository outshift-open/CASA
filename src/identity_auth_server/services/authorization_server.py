"""Service layer for sessions."""

import logging

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
from identity_auth_server.thirdparty.idp.keycloak import KeycloakManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class AuthorizationServerService:
    """Concrete implementation of AuthorizationServerService."""

    def __init__(
        self,
        authorization_server_repository: AuthorizationServerRepository,
        app_repository: AppRepository,
        keycloak_manager: KeycloakManager,
        api_url: str,
    ):
        """Store the backing session repository, keycloak manager, and client repository."""
        self.authorization_server_repository = authorization_server_repository
        self.app_repository = app_repository
        self.keycloak_manager = keycloak_manager
        self.api_url = api_url

    def create_for_app(self, app: App) -> App:
        app = self.app_repository.get_app_by_id(app.id)

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

        return AppMetadataResponse(
            client_name=app.name,
            client_id=f"{self.api_url}/{app.id}/oauth2/client-metadata.json",
            grant_types=["client_credentials"],
            response_types=["token"],
            token_endpoint_auth_method="private_key_jwt",
            jwks_uri=f"{self.api_url}/{app.id}/oauth2/.well-known/jwks.json",
        )

    def generate_token_oauth(self, app_id: str, grant_type: str, client_id: str, client_secret: str) -> TokenResponse:
        """Generate a new token with client_credential grant type for a trusted App."""
        app = self.app_repository.get_app_by_id(app_id)
        if app is None:
            raise Exception(f"App with id {app_id} not found.")

        token = self.keycloak_manager.get_token(
            app.authorization_server,
            client_credentials=ClientCredentials(client_id=client_id, client_secret=client_secret),
            sub=client_id,
            act=None,
            scopes=[],
            extra={},
        )

        token = token["token"]

        logger.debug(f"Got token from Keycloak {token}")

        return TokenResponse(access_token=token["access_token"], token_type="Bearer")

    def generate_token(self, authorization_server: AuthorizationServer, data: TokenRequestParams) -> TokenResponse:
        """Generate a new token based on the request parameters."""
        client_credentials = data.app.client_credentials
        act_client_credentials = data.act.client_credentials if data.act else None

        # Get sub and act values
        sub = client_credentials.client_id
        act = None
        if act_client_credentials:
            sub = act_client_credentials.client_id
            act = client_credentials.client_id

        scopes = []
        for tool in data.tools:
            scopes.append("call_" + str(tool.id))

        # Get a access_token from keycloak
        keycloak_token = self.keycloak_manager.get_token(
            authorization_server,
            client_credentials,
            sub=sub,
            act=act,
            scopes=scopes,
            extra=data.other if data.other else {},
        )

        keycloak_token = keycloak_token["token"]

        logger.debug(f"Got token from Keycloak {keycloak_token}")

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
