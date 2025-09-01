"""Utility functions for the Identity Auth Server API."""

import json
import os

import jwt
from identityservice.badge.mcp import McpResource, McpServer, McpTool
from mcp import types as mcp_types

from identity_auth_server.types import McpTools


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


def decode_badge_extract_tools(badge_token: str) -> McpTools:
    """Decode the badge token directly and extract the MCP tools.

    Args:
        badge_token: The JWT badge token to decode

    Returns:
        List of mcp.types.Tool objects extracted from the badge

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
    return convert_mcp_tools_to_mcp_types(mcp_server)


if __name__ == "__main__":
    # open file: test/api/data/jira_mcp_badge.txt

    # Get the project root (go up from src/identity_auth_server/api/ to project root)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    badge_file_path = os.path.join(project_root, "test", "api", "data", "jira_mcp_badge.txt")

    with open(badge_file_path, "r") as f:
        test_badge_token = f.read().strip()

    result = decode_badge_extract_tools(test_badge_token)
    print("Extracted MCP Tools:")
    for tool in result:
        print(f"- {tool.name}: {tool.description} (Input Schema: {tool.inputSchema})")
