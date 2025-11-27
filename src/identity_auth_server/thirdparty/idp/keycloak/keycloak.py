"""Idp entity module."""

import json
import logging
import os

import requests
from keycloak import KeycloakAdmin, KeycloakOpenID

from identity_auth_server.core.authorization_server.types import ActorClaim

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

    def create_realm(self, realm: str, scopes: list[str] | None = None):
        """Create a new Keycloak realm.

        Args:
            realm_name: The name of the realm to create
        """
        try:
            # Create realm
            self._get_keycloak_admin().create_realm(payload={"realm": realm, "enabled": True}, skip_exists=False)

            # Create scopes
            for scope in scopes:
                logger.info(f"Creating scope: {scope}")
                self._get_keycloak_admin(realm).create_client_scope({"name": scope, "protocol": "openid-connect"}, True)
        except Exception:
            pass  # Realm already exists

    def create_client(self, realm: str, client_id: str):
        """Create a new Keycloak client.

        Args:
            realm: The realm in which to create the client
            client_id: The client identifier

        Returns:
            The created client object

        Raises:
            ValueError: If metadata cannot be fetched from the client_id URL
        """
        # Parse the contents of the url
        try:
            metadata = requests.get(client_id, timeout=REQUEST_TIMEOUT).json()
        except Exception as e:
            raise ValueError(f"Failed to fetch metadata from {client_id}: {e}")

        # Read if client exists
        try:
            # Define new client data
            payload = {
                "clientId": client_id,
                "name": metadata.get("client_name", "Unnamed Client"),
                "enabled": True,
                "publicClient": metadata.get("token_endpoint_auth_method", "") == "none",
                "serviceAccountsEnabled": metadata.get("grant_types", []) == ["client_credentials"],
                "redirectUris": metadata.get("redirect_uris", []),
                "protocol": "openid-connect",
            }

            # Create the client
            client = self._get_keycloak_admin(realm=realm).create_client(payload=payload, skip_exists=False)
        except Exception:
            pass  # Client already exists

        # Get the client database ID
        client_db_id = self._get_keycloak_admin(realm=realm).get_client_id(client_id)

        # Add Protocol Mappers
        self._add_protocol_mappers(realm, client_db_id)

        # Return client
        client = self._get_keycloak_admin(realm=realm).get_client(client_db_id)

        return client

    def _add_protocol_mappers(self, realm: str, client_db_id: str):
        """Add protocol mappers to the client.

        Args:
            realm: The realm name
            client_db_id: The client database ID
        """
        # Remove all existing mappers
        existing_scopes = self._get_keycloak_admin(realm=realm).get_client_scopes()
        for scope in existing_scopes:
            mappers = self._get_keycloak_admin(realm=realm).get_mappers_from_client_scope(scope["id"])
            for mapper in mappers:
                self._get_keycloak_admin(realm=realm).delete_mapper_from_client_scope(scope["id"], mapper["id"])

        # Add Protocol Mapper for X-Requested-Tools
        self._get_keycloak_admin(realm=realm).add_mapper_to_client(
            client_db_id,
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

        # Add Protocol Mapper for X-Requested-Input
        self._get_keycloak_admin(realm=realm).add_mapper_to_client(
            client_db_id,
            {
                "protocol": "openid-connect",
                "protocolMapper": "POIT-gethttpheader",
                "name": "X-Requested-Input",
                "config": {
                    "http-header": "X-Requested-Input",
                    "claim.name": "input",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "lightweight.claim": "false",
                    "userinfo.token.claim": "true",
                    "introspection.token.claim": "true",
                },
            },
        )

        # Add Protocol Mapper for X-Requested-Input
        self._get_keycloak_admin(realm=realm).add_mapper_to_client(
            client_db_id,
            {
                "protocol": "openid-connect",
                "protocolMapper": "POIT-gethttpheader",
                "name": "X-Requested-Input-Id",
                "config": {
                    "http-header": "X-Requested-Input-Id",
                    "claim.name": "input_id",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "lightweight.claim": "false",
                    "userinfo.token.claim": "true",
                    "introspection.token.claim": "true",
                },
            },
        )

        # Add Protocol Mapper for X-Requested-Act
        self._get_keycloak_admin(realm=realm).add_mapper_to_client(
            client_db_id,
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
        self._get_keycloak_admin(realm=realm).add_mapper_to_client(
            client_db_id,
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
        client_id: str,
        client_secret: str,
        realm: str,
        act: ActorClaim | None = None,
        input_id: str = "",
        sub: str = "",
        scopes: list[str] = [],
    ):
        """Get a token from Keycloak for the given client.
        Args:
            client_id: The client identifier
            client_secret: The client secret
            realm: The realm name
            tools: List of requested tools
            act: Requested action
            input_id: Requested input identifier
            sub: Subject claim
            scopes: List of requested scopes

        Returns:
            Token response from Keycloak
        """

        # Assign client scopes to client
        client_db_id = self._get_keycloak_admin(realm).get_client_id(client_id)
        for scope in scopes:
            scope_obj = self._get_keycloak_admin(realm).get_client_scope_by_name(scope)
            self._get_keycloak_admin(realm).add_client_optional_client_scope(client_db_id, scope_obj["id"], {})

        act_string = json.dumps(act.model_dump(exclude_none=True)) if act else "{}"
        input_id_string = input_id

        keycloak_openid = KeycloakOpenID(
            server_url=self.server_url,
            client_id=client_id,
            realm_name=realm,
            client_secret_key=client_secret,
            custom_headers={
                "X-Requested-Act": act_string,
                "X-Requested-Input-Id": input_id_string,
                "X-Requested-Sub": sub,
            },
        )

        return {
            "token": keycloak_openid.token(grant_type="client_credentials", scope=" ".join(scopes)),
            "act": act,
            "input_id": input_id,
            "sub": sub,
            "scopes": scopes,
        }

    def _get_keycloak_admin(self, realm: str = "master") -> KeycloakAdmin:
        """Get the Keycloak admin instance.

        Returns:
            KeycloakAdmin instance
        """
        # Connect to Keycloak Admin API
        return KeycloakAdmin(
            server_url=self.server_url,
            username=self.username,
            password=self.password,
            realm_name=realm,
        )
