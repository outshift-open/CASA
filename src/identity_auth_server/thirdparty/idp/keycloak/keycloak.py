"""Idp entity module."""

import json
import logging
import os

import requests
from keycloak import KeycloakAdmin, KeycloakOpenID

from identity_auth_server.core.authorization_server.types import (
    ActorClaim, AuthorizationServer, ClientCredentials)

# pylint:disable=logging-fstring-interpolation

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30  # seconds


class KeycloakManager:
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

    def create_authorization_server(self, authorization_server: AuthorizationServer):
        """Create a new Keycloak Authorization Server (Realm).

        Args:
            authorization_server: The AuthorizationServer object containing realm information
        """
        try:
            # Create realm
            self._get_keycloak_admin(None).create_realm(
                payload={"realm": authorization_server.realm, "enabled": True}, skip_exists=False
            )
        except Exception:
            pass  # Realm already exists

    def add_authorization_server_scopes(self, authorization_server: AuthorizationServer, scopes: list[str]):
        """Add scopes to the Keycloak Authorization Server (Realm).

        Args:
            authorization_server: The AuthorizationServer object containing realm information
            scopes: List of scope names to add
        """
        try:
            # Create scopes
            for scope in scopes:
                logger.info(f"Creating scope: {scope}")
                self._get_keycloak_admin(authorization_server).create_client_scope(
                    {"name": scope, "protocol": "openid-connect"}, True
                )
        except Exception:
            pass  # Realm already exists

    def create_client_credentials(
        self, authorization_server: AuthorizationServer, client_metadata_url: str
    ) -> ClientCredentials:
        """Create a new Keycloak client.

        Args:
            authorization_server: The AuthorizationServer object containing realm information
            client_metadata_url: URL to fetch client metadata from

        Returns:
            ClientCredentials object containing client information

        Raises:
            ValueError: If metadata cannot be fetched from the client_id URL
        """
        # Parse the contents of the url
        try:
            metadata = requests.get(client_metadata_url, timeout=REQUEST_TIMEOUT).json()
        except Exception as e:
            raise ValueError(f"Failed to fetch metadata from {client_metadata_url}: {e}")

        # Read if client exists
        try:
            # Define new client data
            payload = {
                "clientId": client_metadata_url,
                "name": metadata.get("client_name", "Unnamed Client"),
                "enabled": True,
                "publicClient": metadata.get("token_endpoint_auth_method", "") == "none",
                "serviceAccountsEnabled": metadata.get("grant_types", []) == ["client_credentials"],
                "redirectUris": metadata.get("redirect_uris", []),
                "protocol": "openid-connect",
            }

            # Create the client
            _ = self._get_keycloak_admin(authorization_server).create_client(payload=payload, skip_exists=False)
        except Exception:
            pass  # Client already exists

        # Get the Keycloak internal id
        client_int_id = self._get_keycloak_admin(authorization_server).get_client_id(client_metadata_url)
        if not client_int_id:
            raise ValueError(f"Client ID not found for client_int_id: {client_metadata_url}")

        # Add Protocol Mappers
        self._add_protocol_mappers(authorization_server, client_int_id)

        # Return client
        client_credentials = self._get_keycloak_admin(authorization_server).get_client(client_int_id)

        return ClientCredentials(
            name=client_credentials["name"],
            client_id=client_metadata_url,
            client_secret=client_credentials.get("secret", ""),
            authorization_server_id=authorization_server.id,
        )

    def _add_protocol_mappers(self, authorization_server: AuthorizationServer, client_int_id: str):
        """Add protocol mappers to the client.

        Args:
            realm: The realm name
            client_db_id: The client database ID
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
        authorization_server: AuthorizationServer,
        client_credentials: ClientCredentials,
        sub: str = "",
        act: ActorClaim | None = None,
        scopes: list[str] = [],
        extra: dict | None = None,
    ):
        """Get a token from Keycloak for the given client.

        Args:
            authorization_server: The AuthorizationServer object containing realm information
            client_credentials: The ClientCredentials object containing client information
            sub: Subject for the token
            act: Actor claim for delegation
            scopes: List of scopes to request
            extra: Extra parameters for the token request

        Returns:
            Token response from Keycloak
        """
        # Assign client scopes to client
        client_int_id = self._get_keycloak_admin(authorization_server).get_client_id(client_credentials.client_id)
        if not client_int_id:
            raise ValueError(f"Client ID not found for client_int_id: {client_credentials.client_id}")

        for scope in scopes:
            scope_obj = self._get_keycloak_admin(authorization_server).get_client_scope_by_name(scope)
            self._get_keycloak_admin(authorization_server).add_client_optional_client_scope(
                client_int_id, scope_obj["id"], {}
            )

        act_string = json.dumps(act.model_dump(exclude_none=True)) if act else "{}"
        extra_string = json.dumps(extra) if extra else "{}"

        keycloak_openid = KeycloakOpenID(
            server_url=self.server_url,
            client_id=client_int_id,
            realm_name=authorization_server.realm,
            client_secret_key=client_credentials.client_secret,
            custom_headers={
                "X-Requested-Sub": sub,
                "X-Requested-Act": act_string,
                "X-Requested-Extra": extra_string,
            },
        )

        return {
            "token": keycloak_openid.token(grant_type="client_credentials", scope=" ".join(scopes)),
            "sub": sub,
            "act": act,
            "extra": extra,
            "scopes": scopes,
        }

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
