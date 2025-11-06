"""Idp entity module."""

import json
import logging
import os

import requests
from keycloak import KeycloakAdmin, KeycloakOpenID

# pylint:disable=logging-fstring-interpolation

logger = logging.getLogger(__name__)

# Connect to Keycloak Admin API
keycloak_admin = KeycloakAdmin(
    server_url=os.getenv("IDP_SERVER_URL", "http://localhost:8080/"),
    username=os.getenv("IDP_ADMIN_USERNAME", "admin"),
    password=os.getenv("IDP_ADMIN_PASSWORD", "admin"),
    realm_name="master",
)


def create_keycloak_client(client_id: str):
    """Create a new Keycloak client."""

    # Parse the contents of the url
    try:
        metadata = requests.get(client_id).json()
    except Exception as e:
        raise ValueError(f"Failed to fetch metadata from {client_id}: {e}")

    # Read if client exists
    try:
        existing_client = keycloak_admin.get_client_id(client_id)
        if existing_client:
            # Delete existing client
            keycloak_admin.delete_client(existing_client)
    except Exception:
        pass  # Client does not exist, proceed to create it

    # Define new client data
    payload = {
        "clientId": client_id,
        "name": metadata.get("client_name", "Unnamed Client"),
        "enabled": True,
        "publicClient": metadata.get("token_endpoint_auth_method", "")
        == "none",
        "serviceAccountsEnabled": metadata.get("grant_types", [])
        == ["client_credentials"],
        "redirectUris": metadata.get("redirect_uris", []),
        "protocol": "openid-connect",
    }

    # Create the client
    keycloak_admin.create_client(payload=payload)

    # Get the client database ID
    client_db_id = keycloak_admin.get_client_id(client_id)

    # Add Protocol Mapper
    keycloak_admin.add_mapper_to_client(
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

    keycloak_admin.add_mapper_to_client(
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

    keycloak_admin.add_mapper_to_client(
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

    # Get client secret
    client = keycloak_admin.get_client(client_db_id)

    return client


def get_keycloak_token(
    client_id: str, client_secret: str, tools: list, input: str, act: str
):
    """Get a token from Keycloak for the given client."""
    keycloak_openid = KeycloakOpenID(
        server_url="http://localhost:8080/",
        client_id=client_id,
        realm_name="master",
        client_secret_key=client_secret,
        custom_headers={
            "X-Requested-Tools": " ".join(tools),
            "X-Requested-Input": input,
            "X-Requested-Act": json.dumps(act),
        },
    )

    return keycloak_openid.token(grant_type="client_credentials")
