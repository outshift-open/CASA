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
        # Remove all existing mappers
        existing_scopes = self.keycloak_admin.get_client_scopes()
        for scope in existing_scopes:
            mappers = self.keycloak_admin.get_mappers_from_client_scope(scope["id"])
            for mapper in mappers:
                self.keycloak_admin.delete_mapper_from_client_scope(scope["id"], mapper["id"])

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

        # Add Protocol Mapper for X-Requested-Sub
        self.keycloak_admin.add_mapper_to_client(
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
        tools: list[str] = [],
        act: ActorClaim | None = None,
        input_id: str = "",
        sub: str = "",
        scopes: list[str] = [],
        type: str = "source",
    ):
        """Get a token from Keycloak for the given client.

        Args:
            client_id: The client identifier
            client_secret: The client secret
            tools: List of requested tools
            act: Requested action
            input_id: Requested input identifier
            sub: Subject claim
            scopes: List of requested scopes
            type: Type of token requested (source, llm, mcp)

        Returns:
            Token response from Keycloak
        """
        if type == "llm":
            scopes.append("call-llm")

        elif type == "mcp":
            # append default scopes
            scopes.append("list-tools")
            scopes.append("list-resources")

            if tools:
                scopes.append("call-tools")

        else:
            scopes.append("call-agent")

        # Create scopes
        for scope in scopes:
            logger.info(f"Creating scope: {scope}")
            self.keycloak_admin.create_client_scope({"name": scope, "protocol": "openid-connect"}, True)

        # Assign client scopes to client
        client_db_id = self.keycloak_admin.get_client_id(client_id)
        for scope in scopes:
            scope_obj = self.keycloak_admin.get_client_scope_by_name(scope)
            self.keycloak_admin.add_client_optional_client_scope(client_db_id, scope_obj["id"], {})

        tool_string = "[" + ", ".join(tools) + "]" if tools else "[]"
        act_string = json.dumps(act.model_dump(exclude_none=True)) if act else "{}"
        input_id_string = input_id

        keycloak_openid = KeycloakOpenID(
            server_url=self.server_url,
            client_id=client_id,
            realm_name=self.realm_name,
            client_secret_key=client_secret,
            custom_headers={
                "X-Requested-Tools": tool_string,
                "X-Requested-Act": act_string,
                "X-Requested-Input-Id": input_id_string,
                "X-Requested-Sub": sub,
            },
        )

        return {
            "token": keycloak_openid.token(grant_type="client_credentials", scope=" ".join(scopes)),
            "tools": tools,
            "act": act,
            "input_id": input_id,
            "sub": sub,
            "scope": scope,
        }
