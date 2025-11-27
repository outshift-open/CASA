# pylint: disable=too-few-public-methods
# Copyright 2025 Cisco Systems, Inc. and its affiliates
# SPDX-License-Identifier: Apache-2.0
"""Httpx Auth module for the Identity Service Python SDK."""


# from identityservice.auth.common import get_mcp_request_tool_name
# from identityservice.sdk import IdentityServiceSdk as Sdk
# from identityservice.auth.context import source_access_token_var

import httpx
import os

from identity_auth_server import sdk

# logger = logging.getLogger("identityservice.auth.httpx")


class CustomAuth(httpx.Auth):
    """Httpx authentication class for the Identity Service SDK."""

    requires_response_body = True

    def __init__(
        self,
        source_app_call_token: str | None = None,
        llm_app_token: str | None = None,
        mcp_server_url: str | None = None,
        auth_server_url: str | None = None,
    ):
        """Initialize the IdentityServiceAuth class."""
        self.source_app_call_token = source_app_call_token
        self.llm_app_token = llm_app_token
        self.mcp_server_url = mcp_server_url
        self.auth_server_url = auth_server_url or os.getenv("AUTH_SERVER_URL", "http://localhost:8000")
        self.mcp_server_url_for_auth = os.getenv("MCP_SERVER_URL_FOR_AUTH", self.mcp_server_url)

    async def async_auth_flow(self, request):
        """Add the Authorization header to the request (async version)."""
        async with sdk.AsyncIdentityAuthClient(self.auth_server_url) as auth_client:
            mcp_token = await auth_client.get_mcp_app_call_token(
                grant_type="client_credentials",
                client_id="http://localhost:8082/oauth/client-metadata.json",
                client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                client_assertion="eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1In0.eyJpc3MiOiJ5b3VyLWNsaWVudC1pZCIsInN1YiI6InlvdXItY2xpZW50LWlkIiwiYXVkIjoiaHR0cHM6Ly9hdXRoLmV4YW1wbGUuY29tL29hdXRoMi90b2tlbiIsImlhdCI6MTcyNjUxMzkyNywiZXhwIjoxNzI2NTE0MjI3LCJqdGkiOiIxNzI2NTEzOTI3OTYxMDAwMCJ9",
                llm_app_call_token=self.llm_app_token,
                source_app_call_token=self.source_app_call_token,
                mcp_server_url=self.mcp_server_url_for_auth,
            )

        request.headers["Authorization"] = f"Bearer {mcp_token}"
        yield request
