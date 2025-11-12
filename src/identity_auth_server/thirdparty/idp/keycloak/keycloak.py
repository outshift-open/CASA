"""Idp entity module."""

import json
import logging
import os

import requests
from keycloak import KeycloakAdmin, KeycloakOpenID

from identity_auth_server.core.token.types import ActorClaim

# pylint:disable=logging-fstring-interpolation

logger = logging.getLogger(__name__)


class KeycloakManager:
    """Manages Keycloak client and token operations."""

    def __init__(
        self,
        server_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        realm_name: str | None = "master",
    ):
        """Initialize Keycloak Manager.

        Args:
            server_url: Keycloak server URL (defaults to IDP_SERVER_URL env var or http://localhost:8080/)
            username: Admin username (defaults to IDP_ADMIN_USERNAME env var or 'admin')
            password: Admin password (defaults to IDP_ADMIN_PASSWORD env var or 'admin')
            realm_name: Keycloak realm name (defaults to 'master')
        """
        self.server_url = server_url or os.getenv("IDP_SERVER_URL", "http://localhost:8080/")
        self.realm_name = realm_name

        # Connect to Keycloak Admin API
        self.keycloak_admin = KeycloakAdmin(
            server_url=self.server_url,
            username=username or os.getenv("IDP_ADMIN_USERNAME", "admin"),
            password=password or os.getenv("IDP_ADMIN_PASSWORD", "admin"),
            realm_name=self.realm_name,
        )

    def create_client(self, client_id: str):
        """Create a new Keycloak client.

        Args:
            client_id: The client identifier

        Returns:
            The created client object

        Raises:
            ValueError: If metadata cannot be fetched from the client_id URL
        """
        # Parse the contents of the url

        try:
            metadata = requests.get(client_id).json()
        except Exception as e:
            raise ValueError(f"Failed to fetch metadata from {client_id}: {e}")

        # Read if client exists
        try:
            existing_client = self.keycloak_admin.get_client_id(client_id)
            if existing_client:
                # Delete existing client
                self.keycloak_admin.delete_client(existing_client)
        except Exception:
            pass  # Client does not exist, proceed to create it

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
        self.keycloak_admin.create_client(payload=payload)

        # Get the client database ID
        client_db_id = self.keycloak_admin.get_client_id(client_id)

        # Add Protocol Mappers
        self._add_protocol_mappers(client_db_id)

        # Get client secret
        client = self.keycloak_admin.get_client(client_db_id)

        return client

    def _add_protocol_mappers(self, client_db_id: str):
        """Add protocol mappers to the client.

        Args:
            client_db_id: The client database ID
        """
        # Add Protocol Mapper for X-Requested-Tools
        self.keycloak_admin.add_mapper_to_client(
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
        self.keycloak_admin.add_mapper_to_client(
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
        self.keycloak_admin.add_mapper_to_client(
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
        self.keycloak_admin.add_mapper_to_client(
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

    def get_token(
        self,
        client_id: str,
        client_secret: str,
        tools: list[str] = [],
        input: str = "",
        act: ActorClaim | None = None,
        input_id: str = "",
    ):
        """Get a token from Keycloak for the given client.

        Args:
            client_id: The client identifier
            client_secret: The client secret
            tools: List of requested tools
            input: Requested input data
            act: Requested action
            input_id: Requested input identifier

        Returns:
            Token response from Keycloak
        """
        tool_string = "[" + ", ".join(tools) + "]" if tools else "[]"
        input_string = input
        act_string = json.dumps(act.model_dump()) if act else "{}"
        input_id_string = input_id

        keycloak_openid = KeycloakOpenID(
            server_url=self.server_url,
            client_id=client_id,
            realm_name=self.realm_name,
            client_secret_key=client_secret,
            custom_headers={
                "X-Requested-Tools": tool_string,
                "X-Requested-Input": input_string,
                "X-Requested-Act": act_string,
                "X-Requested-Input-Id": input_id_string,
            },
        )

        return {
            "token": keycloak_openid.token(grant_type="client_credentials"),
            "tools": tools,
            "input": input,
            "act": act,
            "input_id": input_id,
        }
