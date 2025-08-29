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


def create_identity_service_client() -> sdk.IdentityServiceSdk:
    """Create and return an IdentityServiceSdk client."""
    return sdk.IdentityServiceSdk(
        api_key=os.getenv("IDENTITY_SERVICE_API_KEY"),
    )


def verify_badge_with_identity_service(badge_token: str, sdk_client: sdk.IdentityServiceSdk) -> VerificationResult:
    """Verify the badge token using the identity service client."""
    return sdk_client.verify_badge(badge_token)


def validate_verification_result(verified_result: VerificationResult) -> None:
    """Validate the verification result from the identity service.

    Args:
        verified_result: The verification result to validate

    Raises:
        ValueError: If validation fails for any reason
    """
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


def parse_badge_json_to_mcp_server(badge_json_str: str) -> McpServer:
    """Parse badge JSON string to McpServer object.

    Args:
        badge_json_str: JSON string containing badge data

    Returns:
        McpServer object with parsed tools and resources

    Raises:
        json.JSONDecodeError: If badge JSON is invalid
        KeyError: If required fields are missing
    """
    # first convert the badge field to a JSON object
    badge_json = json.loads(badge_json_str)

    # convert the badge_json to a McpServer object
    return McpServer(
        name=badge_json["name"],
        url=badge_json["url"],
        tools=[McpTool(**tool) for tool in badge_json.get("tools", [])],
        resources=[McpResource(**res) for res in badge_json.get("resources", [])],
    )


def convert_mcp_tools_to_mcp_types(mcp_server: McpServer) -> list[mcp_types.Tool]:
    """Convert McpTool objects to mcp.types.Tool objects.

    Args:
        mcp_server: McpServer object containing tools

    Returns:
        List of mcp.types.Tool objects
    """
    mcp_tools: list[mcp_types.Tool] = []
    for tool in mcp_server.tools:
        mcp_tool = mcp_types.Tool(
            name=tool.name,
            description=tool.description,
            inputSchema=tool.parameters,
        )
        mcp_tools.append(mcp_tool)
    return mcp_tools


def verify_identity_service_badge_extract_tools(badge_token: str) -> McpTools:
    """Verify the badge token using the identity-service-sdk and extract the MCP tools.

    Args:
        badge_token: The badge token to verify

    Returns:
        List of mcp.types.Tool objects extracted from the badge

    Raises:
        ValueError: If badge verification fails or validation fails
        json.JSONDecodeError: If badge JSON is invalid
        KeyError: If required fields are missing from badge JSON
    """
    # Create identity service client
    sdk_client = create_identity_service_client()

    # Verify badge with identity service
    verified_result = verify_badge_with_identity_service(badge_token, sdk_client)

    # Validate the verification result
    validate_verification_result(verified_result)

    # Parse badge JSON to MCP server object
    mcp_server = parse_badge_json_to_mcp_server(verified_result.document.credential_subject.badge)

    # Convert MCP tools to mcp.types.Tool objects
    return convert_mcp_tools_to_mcp_types(mcp_server)


if __name__ == "__main__":
    # open file: src/identity_auth_server/api/jira_mcp_badge.txt

    badge_file_path = os.path.join(os.path.dirname(__file__), "jira_mcp_badge.txt")

    with open(badge_file_path, "r") as f:
        test_badge_token = f.read().strip()

    result = verify_identity_service_badge_extract_tools(test_badge_token)
    print("Extracted MCP Tools:")
    for tool in result:
        print(f"- {tool.name}: {tool.description} (Input Schema: {tool.inputSchema})")
