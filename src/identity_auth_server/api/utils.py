"""Utility functions for the Identity Auth Server API."""

import json
import os

import dotenv

dotenv.load_dotenv()  # Load environment variables from a .env file if present

# this is a GRPC object, and loaded in memory by the identity-service-sdk
from identityservice import sdk
from identityservice.badge.mcp import McpResource, McpServer, McpTool
from mcp import types as mcp_types
from outshift.identity.service.v1alpha1.badge_pb2 import VerificationResult

from identity_auth_server.types import McpTools


def verify_identity_service_badge_extract_tools(badge_token: str) -> McpTools:
    """Verify the badge token using the identity-service-sdk and extract the MCP tools."""
    sdk_client = sdk.IdentityServiceSdk(
        api_key=os.getenv("IDENTITY_SERVICE_API_KEY"),
    )

    verified_result = sdk_client.verify_badge(badge_token)

    # confirm verified result is of type VerificationResult, this is loaded in memory by the identity-service-sdk
    if not isinstance(verified_result, VerificationResult):
        raise ValueError(f"Unexpected result type: {type(verified_result)}")

    # verify that verified_result.status is True
    if not verified_result.status:
        raise ValueError("Badge verification failed")

    # verify that verified_result.document.credential_subject.id is a non-empty string
    if (
        not isinstance(verified_result.document.credential_subject.id, str)
        or not verified_result.document.credential_subject.id
    ):
        raise ValueError(f"Unexpected credential subject id: {verified_result.document.credential_subject.id}")

    # verify that verified_result.document.type is ['BADGE_TYPE_MCP_BADGE']
    if verified_result.document.type != ["BADGE_TYPE_MCP_BADGE"]:
        raise ValueError(f"Unexpected document type: {verified_result.document.type}")

    # first convert the badge field to a JSON object
    badge_json = json.loads(verified_result.document.credential_subject.badge)

    # convert the badge_json to a McpServer object
    badge_json = McpServer(
        name=badge_json["name"],
        url=badge_json["url"],
        tools=[McpTool(**tool) for tool in badge_json.get("tools", [])],
        resources=[McpResource(**res) for res in badge_json.get("resources", [])],
    )

    # convert the McpTool objects to mcp.types.Tool objects
    mcp_tools: list[mcp_types.Tool] = []
    for tool in badge_json.tools:
        mcp_tool = mcp_types.Tool(
            name=tool.name,
            description=tool.description,
            inputSchema=tool.parameters,
        )
        mcp_tools.append(mcp_tool)

    return mcp_tools


if __name__ == "__main__":
    # open file: src/identity_auth_server/api/jira_mcp_badge.txt

    badge_file_path = os.path.join(os.path.dirname(__file__), "jira_mcp_badge.txt")

    with open(badge_file_path, "r") as f:
        test_badge_token = f.read().strip()

    result = verify_identity_service_badge_extract_tools(test_badge_token)
    print("Extracted MCP Tools:")
    for tool in result:
        print(f"- {tool.name}: {tool.description} (Input Schema: {tool.inputSchema})")
