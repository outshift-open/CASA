"""Utility functions for the Identity Auth Server API."""

import json
import os

import identityservice.badge.mcp as sdk
import jwt
from mcp import types as mcp_types

from identity_auth_server.types import McpResources, McpServer, McpTools


def decode_badge_jwt(badge_token: str) -> dict:
    """Decode JWT badge token without verification.

    Args:
        badge_token: The JWT badge token to decode

    Returns:
        Decoded JWT payload as dictionary

    Raises:
        jwt.DecodeError: If JWT token is invalid
    """
    return jwt.decode(badge_token, options={"verify_signature": False})


def validate_badge_payload(decoded_badge: dict) -> None:
    """Validate the decoded badge payload.

    Args:
        decoded_badge: The decoded JWT payload

    Raises:
        ValueError: If validation fails for any reason
    """
    # verify that type is ['BADGE_TYPE_MCP_BADGE']
    if decoded_badge.get("type") != ["BADGE_TYPE_MCP_BADGE"]:
        raise ValueError(f"Unexpected badge type: {decoded_badge.get('type')}")

    # verify that credentialSubject exists and has required fields
    if "credentialSubject" not in decoded_badge:
        raise ValueError("Missing or invalid credentialSubject")

    credential_subject = decoded_badge["credentialSubject"]
    if not isinstance(credential_subject, dict):
        raise ValueError("Missing or invalid credentialSubject")

    # verify that credentialSubject.id is a non-empty string
    badge_id = credential_subject.get("id", "")
    if not isinstance(badge_id, str) or not badge_id:
        raise ValueError(f"Unexpected credential subject id: {badge_id}")

    # verify that credentialSubject.badge field exists
    if "badge" not in credential_subject:
        raise ValueError("Missing badge field in credentialSubject")


def parse_badge_json_to_mcp_server(badge_json_str: str) -> sdk.McpServer:
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
    return sdk.McpServer(
        name=badge_json["name"],
        url=badge_json["url"],
        tools=[sdk.McpTool(**tool) for tool in badge_json.get("tools", [])],
        resources=[sdk.McpResource(**res) for res in badge_json.get("resources", [])],
    )


def convert_mcp_server(mcp_server: sdk.McpServer) -> McpServer:
    """Converts Identity SDK types.

    Args:
        mcp_server: sdk.McpServer object containing name, tools and resources

    Returns:
        McpServer
    """
    mcp_tools: McpTools = []
    for tool in mcp_server.tools:
        mcp_tool = mcp_types.Tool(
            name=tool.name,
            description=tool.description,
            inputSchema=tool.parameters,
        )
        mcp_tools.append(mcp_tool)

    mcp_resources: McpResources = []
    for resource in mcp_server.resources:
        mcp_resource = mcp_types.Resource(name=resource.name, description=resource.description, uri=resource.uri)
        mcp_resources.append(mcp_resource)

    converted_mcp_server = McpServer(name=mcp_server.name, tools=mcp_tools, resources=mcp_resources)

    return converted_mcp_server


def decode_badge_extract_mcp_server(badge_token: str) -> McpServer:
    """Decode the badge token directly and extract the MCP tools.

    Args:
        badge_token: The JWT badge token to decode

    Returns:
        McpServer

    Raises:
        ValueError: If badge validation fails
        jwt.DecodeError: If JWT token is invalid
        json.JSONDecodeError: If badge JSON is invalid
        KeyError: If required fields are missing from badge JSON
    """
    # Decode JWT badge token without verification
    decoded_badge = decode_badge_jwt(badge_token)

    # Validate the decoded badge payload
    validate_badge_payload(decoded_badge)

    # Extract badge JSON from credentialSubject
    credential_subject = decoded_badge["credentialSubject"]
    badge_json_str = credential_subject["badge"]

    # Parse badge JSON to MCP server object
    mcp_server = parse_badge_json_to_mcp_server(badge_json_str)

    # Convert MCP tools to mcp.types.Tool objects
    return convert_mcp_server(mcp_server)


if __name__ == "__main__":
    # open file: test/api/data/jira_mcp_badge.txt

    # Get the project root (go up from src/identity_auth_server/api/ to project root)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    badge_file_path = os.path.join(project_root, "test", "api", "data", "jira_mcp_badge.txt")

    with open(badge_file_path, "r") as f:
        test_badge_token = f.read().strip()

    result = decode_badge_extract_mcp_server(test_badge_token)
    print("Extracted MCP Server:")
    print(" - Name: " + result.name)

    print(" - Tools:")
    for tool in result.tools:
        print(f"- {tool.name}: {tool.description} (Input Schema: {tool.inputSchema})")

    print(" - Resources:")
    for resource in result.resources:
        print(f"- {resource.name}: {resource.description} (URI: {resource.uri})")
