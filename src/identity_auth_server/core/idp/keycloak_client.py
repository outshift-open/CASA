"""Idp entity module."""

import json
import logging
import os

from keycloak import KeycloakAdmin, KeycloakOpenID

from identity_auth_server.core.idp.idp_client import IdpClient, TokenPayload
from identity_auth_server.core.types import ActorClaim, AppMetadataResponse, AuthorizationServer, ClientCredentials

# pylint:disable=logging-fstring-interpolation

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30  # seconds


class KeycloakClient(IdpClient):
    """Manages Keycloak client and token operations."""

    def __init__(
        self,
        server_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        """Initialize Keycloak Manager.

        Args:
            server_url: Keycloak server URL (defaults to IDP_SERVER_URL env var or http://localhost:8080/)
            username: Admin username (defaults to IDP_ADMIN_USERNAME env var or 'admin')
            password: Admin password (defaults to IDP_ADMIN_PASSWORD env var or 'admin')
        """
        self.server_url = server_url or os.getenv("IDP_SERVER_URL", "http://localhost:8080/")
        self.username = username or os.getenv("IDP_ADMIN_USERNAME", "admin")
        self.password = password or os.getenv("IDP_ADMIN_PASSWORD", "admin")

    def create_authorization_server(self, authz_serv: AuthorizationServer) -> None:
        """Create a new Keycloak Authorization Server (Realm).

        Args:
            authz_serv: The AuthorizationServer object containing realm information
        """
        try:
            # Create realm and first admin user
            self._get_keycloak_admin(None).create_realm(
                payload={
                    "realm": authz_serv.realm,
                    "users": [
                        {
                            "username": self.username,
                            "firstName": "Admin",
                            "lastName": "User",
                            "enabled": True,
                            "email": "admin@admin.org",
                            "emailVerified": True,
                            "credentials": [{"value": self.password, "type": "password", "temporary": False}],
                            "clientRoles": {"realm-management": ["realm-admin"]},
                        }
                    ],
                    "enabled": True,
                },
                skip_exists=False,
            )
        except Exception:
            pass  # Realm already exists

    def delete_authorization_server(self, authz_serv: AuthorizationServer) -> None:
        try:
            self._get_keycloak_admin(authz_serv).delete_realm(authz_serv.realm)
        except Exception as e:
            logger.error(f"Unable to delete the ream {authz_serv.realm}", e)

    def create_scopes(self, authz_serv: AuthorizationServer, scopes: list[str]) -> None:
        """Add scopes to the Keycloak Authorization Server (Realm).

        Args:
            authz_serv: The AuthorizationServer object containing realm information
            scopes: List of scope names to add
        """
        try:
            # Create scopes
            for scope in scopes:
                logger.info(f"Creating scope: {scope}")
                self._get_keycloak_admin(authz_serv).create_client_scope(
                    {"name": scope, "protocol": "openid-connect"}, True
                )
        except Exception:
            logger.warning(f"Some scopes may already exist in realm {authz_serv.realm}")

    def update_scope(self, authz_serv: AuthorizationServer, old_name: str, new_name: str) -> None:
        """Update a scope in the Keycloak Authorization Server (Realm).

        Args:
            authz_serv: The AuthorizationServer object containing realm information
            old_name: Current name of the scope
            new_name: New name for the scope
        """
        try:
            # Get the existing scope
            scope = self._get_keycloak_admin(authz_serv).get_client_scope_by_name(old_name)
            if scope:
                # Keycloak doesn't support renaming, so delete and recreate
                self._get_keycloak_admin(authz_serv).delete_client_scope(scope["id"])
                logger.info(f"Deleted scope: {old_name}")

                # Create with new name
                self._get_keycloak_admin(authz_serv).create_client_scope(
                    {"name": new_name, "protocol": "openid-connect"}, True
                )
                logger.info(f"Created scope: {new_name}")
        except Exception as e:
            logger.error(f"Unable to update scope {old_name} to {new_name} in realm {authz_serv.realm}", e)

    def delete_scope(self, authz_serv: AuthorizationServer, scope_name: str) -> None:
        """Delete a scope from the Keycloak Authorization Server (Realm).

        Args:
            authz_serv: The AuthorizationServer object containing realm information
            scope_name: Name of the scope to delete
        """
        try:
            # Get the scope by name
            scope = self._get_keycloak_admin(authz_serv).get_client_scope_by_name(scope_name)
            if scope:
                self._get_keycloak_admin(authz_serv).delete_client_scope(scope["id"])
                logger.info(f"Deleted scope: {scope_name}")
        except Exception as e:
            logger.error(f"Unable to delete scope {scope_name} in realm {authz_serv.realm}", e)

    def create_client_credentials(
        self,
        authz_serv: AuthorizationServer,
        client_creds: ClientCredentials,
        metadata: AppMetadataResponse,
    ) -> ClientCredentials:
        """Create a new Keycloak client.

        Args:
            authz_serv: The AuthorizationServer object containing realm information
            client_credentials: The ClientCredentials object containing client information

        Returns:
            ClientCredentials object containing client information

        Raises:
            ValueError: If metadata cannot be fetched from the client_id URL
        """
        # Read if client exists
        try:
            # Define new client data
            payload = {
                "clientId": client_creds.client_id,
                "name": metadata.client_name if len(metadata.client_name) > 0 else "Unnamed Client",
                "enabled": True,
                "publicClient": metadata.token_endpoint_auth_method == "none",
                "serviceAccountsEnabled": metadata.grant_types == ["client_credentials"],
                "redirectUris": [],
                "protocol": "openid-connect",
            }

            # Create the client
            _ = self._get_keycloak_admin(authz_serv).create_client(payload=payload, skip_exists=False)
        except Exception:
            pass  # Client already exists

        # Get the Keycloak internal id
        client_int_id = self._get_keycloak_admin(authz_serv).get_client_id(client_creds.client_id)
        if not client_int_id:
            raise ValueError(f"Client ID not found for client_int_id: {client_creds.client_id}")

        # Add Protocol Mappers
        self._add_protocol_mappers(authz_serv, client_int_id)

        # Add the necessary scopes
        self._get_keycloak_admin(authz_serv).create_client_scope(
            payload={"name": "call-tools", "protocol": "openid-connect"}, skip_exists=True
        )

        # Return client
        client = self._get_keycloak_admin(authz_serv).get_client(client_int_id)

        # Add secret
        client_creds.client_secret = client.get("secret", "")

        return client_creds

    def delete_client_credentials(self, authz_serv: AuthorizationServer, client_creds: ClientCredentials) -> None:
        """Delete a client credentials from an authorization server."""
        keycloak_admin = self._get_keycloak_admin(authz_serv)

        client_int_id = keycloak_admin.get_client_id(client_creds.client_id)
        if not client_int_id:
            raise ValueError(f"Client ID not found for client_int_id: {client_creds.client_id}")

        try:
            keycloak_admin.delete_client(client_int_id)
        except Exception as e:
            logger.error(
                f"Unable to delete the Keycloak client {client_creds.client_id} in realm {authz_serv.realm}", e
            )

    def _add_protocol_mappers(self, authorization_server: AuthorizationServer, client_int_id: str):
        """Add protocol mappers to the client.

        Args:
            authorization_server: The authorization server
            client_int_id: The client database ID
        """
        # Remove all existing mappers
        existing_scopes = self._get_keycloak_admin(authorization_server).get_client_scopes()
        for scope in existing_scopes:
            mappers = self._get_keycloak_admin(authorization_server).get_mappers_from_client_scope(scope["id"])
            for mapper in mappers:
                self._get_keycloak_admin(authorization_server).delete_mapper_from_client_scope(
                    scope["id"], mapper["id"]
                )

        # Add Protocol Mapper for X-Requested-Extra
        self._get_keycloak_admin(authorization_server).add_mapper_to_client(
            client_int_id,
            {
                "protocol": "openid-connect",
                "protocolMapper": "POIT-gethttpheader",
                "name": "X-Requested-Extra",
                "config": {
                    "http-header": "X-Requested-Extra",
                    "claim.name": "extra",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "lightweight.claim": "false",
                    "userinfo.token.claim": "true",
                    "introspection.token.claim": "true",
                },
            },
        )

        # Add protocol Mapper for X-Requested-Input-Id
        self._get_keycloak_admin(authorization_server).add_mapper_to_client(
            client_int_id,
            {
                "protocol": "openid-connect",
                "protocolMapper": "POIT-gethttpheader",
                "name": "X-Requested-Input-Id",
                "config": {
                    "http-header": "X-Requested-Input-Id",
                    "claim.name": "uiid",  # user input id
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "lightweight.claim": "false",
                    "userinfo.token.claim": "true",
                    "introspection.token.claim": "true",
                },
            },
        )

        # Add Protocol Mapper for X-Requested-Act
        self._get_keycloak_admin(authorization_server).add_mapper_to_client(
            client_int_id,
            {
                "protocol": "openid-connect",
                "protocolMapper": "POIT-gethttpheader",
                "name": "X-Requested-Act",
                "config": {
                    "http-header": "X-Requested-Act",
                    "claim.name": "act",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "lightweight.claim": "false",
                    "userinfo.token.claim": "true",
                    "introspection.token.claim": "true",
                },
            },
        )

        # Add Protocol Mapper for X-Requested-Tools
        self._get_keycloak_admin(authorization_server).add_mapper_to_client(
            client_int_id,
            {
                "protocol": "openid-connect",
                "protocolMapper": "POIT-gethttpheader",
                "name": "X-Requested-Tools",
                "config": {
                    "http-header": "X-Requested-Tools",
                    "claim.name": "tools",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "lightweight.claim": "false",
                    "userinfo.token.claim": "true",
                    "introspection.token.claim": "true",
                },
            },
        )

        # Add Protocol Mapper for X-Requested-Sub
        self._get_keycloak_admin(authorization_server).add_mapper_to_client(
            client_int_id,
            {
                "protocol": "openid-connect",
                "protocolMapper": "POIT-gethttpheader",
                "name": "X-Requested-Sub",
                "config": {
                    "http-header": "X-Requested-Sub",
                    "claim.name": "sub",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "lightweight.claim": "false",
                    "userinfo.token.claim": "true",
                    "introspection.token.claim": "true",
                },
            },
        )

    def get_token(
        self,
        authz_serv: AuthorizationServer,
        client_creds: ClientCredentials,
        sub: str = "",
        act: ActorClaim | None = None,
        scopes: list[str] = [],
        extra: dict | None = None,
        user_input_id: str = "",
        tools: list[str] = [],
    ) -> TokenPayload:
        """Get a token from Keycloak for the given client.

        Args:
            authz_serv: The AuthorizationServer object containing realm information
            client_creds: The ClientCredentials object containing client information
            sub: Subject for the token
            act: Actor claim for delegation
            scopes: List of scopes to request
            extra: Extra parameters for the token request
            user_input_id: the id of the initial user prompt
            tools: the list of approved tools

        Returns:
            Token response from Keycloak
        """
        # Get client internal ID
        client_int_id = self._get_keycloak_admin(authz_serv).get_client_id(client_creds.client_id)
        if not client_int_id:
            raise ValueError(f"Client ID not found for client_int_id: {client_creds.client_id}")

        compiled_scopes = ["openid", "offline_access"]

        for scope in scopes:
            scope_obj = self._get_keycloak_admin(authz_serv).get_client_scope_by_name(scope)
            if scope_obj:
                self._get_keycloak_admin(authz_serv).add_client_optional_client_scope(
                    client_int_id, scope_obj["id"], {}
                )
                compiled_scopes.append(scope)

        extra_string = json.dumps(extra) if extra else "{}"

        logger.debug(
            f"Requesting token with sub: {sub}, act: {act}, extra: {extra_string}, scopes: {compiled_scopes}, user input id: {user_input_id}"
        )
        logger.debug(f"Client ID: {client_creds.client_id}, Client Int ID: {client_int_id}")
        logger.debug(f"Authorization Server Realm: {authz_serv.realm}")
        logger.debug(f"Client Secret: {client_creds.client_secret}")

        custom_headers = {
            "X-Requested-Sub": sub,
            "X-Requested-Act": act.model_dump_json(exclude_none=True) if act else "",
            "X-Requested-Extra": extra_string,
            "X-Requested-Input-Id": user_input_id,
        }

        if tools:
            custom_headers["X-Requested-Tools"] = json.dumps(tools)

        keycloak_openid = KeycloakOpenID(
            server_url=self.server_url,
            client_id=client_creds.client_id,
            realm_name=authz_serv.realm,
            client_secret_key=client_creds.client_secret,
            custom_headers=custom_headers,
        )

        return TokenPayload(
            token=keycloak_openid.token(grant_type="client_credentials", scope=" ".join(compiled_scopes)),
            sub=sub,
            act=act,
            extra=extra,
            scopes=compiled_scopes,
            tools=tools,
        )

    def _get_keycloak_admin(self, authorization_server: AuthorizationServer | None) -> KeycloakAdmin:
        """Get the Keycloak admin instance.

        Args:
            authorization_server: The AuthorizationServer object containing realm information

        Returns:
            KeycloakAdmin instance
        """
        realm = authorization_server.realm if authorization_server else "master"

        # Connect to Keycloak Admin API
        return KeycloakAdmin(
            server_url=self.server_url,
            username=self.username,
            password=self.password,
            realm_name=realm,
        )
