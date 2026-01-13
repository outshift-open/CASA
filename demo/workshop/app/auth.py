# pylint: disable=too-few-public-methods
# Copyright 2025 Cisco Systems, Inc. and its affiliates
# SPDX-License-Identifier: Apache-2.0
"""Httpx Auth module for the Identity Service Python SDK."""


import json
from typing import Optional
from urllib import parse
import httpx
import os

import identity_auth_sdk

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
        self.mcp_app_id = os.getenv("MCP_APP_ID", "")
        self.mcp_app_client_id = os.getenv("MCP_CLIENT_ID", "")
        self.mcp_app_client_secret = os.getenv("MCP_CLIENT_SECRET", "")
        self.sdk_config = identity_auth_sdk.Configuration(
            host = self.auth_server_url
        )

    async def async_auth_flow(self, request):
        """Add the Authorization header to the request (async version)."""
        with identity_auth_sdk.ApiClient(self.sdk_config) as api_client:
            api_instance = identity_auth_sdk.DefaultApi(api_client)
            tools: Optional[list[str]] = None

            body = json.loads(request.read().decode("utf-8"))
            if "method" in body and body["method"] == "tools/call":
                tools = [body["params"]["name"]]

            mcp_token = api_instance.token_exchange(
                app_id=self.mcp_app_id,
                client_id=self.mcp_app_client_id,
                client_secret=self.mcp_app_client_secret,
                subject_token=self.llm_app_token,
                subject_token_type="urn:ietf:params:oauth:token-type:access_token",
                mcp_server_url=self.mcp_server_url_for_auth,
                tools=tools,
            )

        request.headers["Authorization"] = f"Bearer {mcp_token.access_token}"
        yield request
