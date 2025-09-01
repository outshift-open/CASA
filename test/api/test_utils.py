"""Unit tests for identity_auth_server.api.utils module."""

import json
import os
from unittest.mock import Mock, patch

import jwt
import pytest
from identityservice.badge.mcp import McpServer
from mcp import types as mcp_types

from identity_auth_server.api.utils import (
    convert_mcp_tools_to_mcp_types,
    decode_badge_extract_tools,
    decode_badge_jwt,
    parse_badge_json_to_mcp_server,
    validate_badge_payload,
)


class TestDecodeBadgeJwt:
    """Test cases for decode_badge_jwt function."""

    @patch("identity_auth_server.api.utils.jwt.decode")
    def test_decode_jwt_success(self, mock_jwt_decode):
        """Test successful JWT decoding."""
        expected_payload = {
            "type": ["BADGE_TYPE_MCP_BADGE"],
            "credentialSubject": {"id": "test-user-id", "badge": '{"name": "test", "url": "http://test.com"}'},
        }
        mock_jwt_decode.return_value = expected_payload

        result = decode_badge_jwt("test-jwt-token")

        mock_jwt_decode.assert_called_once_with("test-jwt-token", options={"verify_signature": False})
        assert result == expected_payload

    @patch("identity_auth_server.api.utils.jwt.decode")
    def test_decode_jwt_invalid_token(self, mock_jwt_decode):
        """Test JWT decoding with invalid token."""
        mock_jwt_decode.side_effect = jwt.DecodeError("Invalid token")

        with pytest.raises(jwt.DecodeError, match="Invalid token"):
            decode_badge_jwt("invalid-token")


class TestValidateBadgePayload:
    """Test cases for validate_badge_payload function."""

    def test_validate_success(self):
        """Test successful validation of badge payload."""
        payload = {
            "type": ["BADGE_TYPE_MCP_BADGE"],
            "credentialSubject": {"id": "test-user-id", "badge": '{"name": "test", "url": "http://test.com"}'},
        }

        # Should not raise any exception
        validate_badge_payload(payload)

    def test_validate_wrong_type(self):
        """Test validation fails with wrong badge type."""
        payload = {
            "type": ["BADGE_TYPE_OTHER"],
            "credentialSubject": {"id": "test-user-id", "badge": '{"name": "test", "url": "http://test.com"}'},
        }

        with pytest.raises(ValueError, match="Unexpected badge type"):
            validate_badge_payload(payload)

    def test_validate_missing_credential_subject(self):
        """Test validation fails with missing credentialSubject."""
        payload = {"type": ["BADGE_TYPE_MCP_BADGE"]}

        with pytest.raises(ValueError, match="Missing or invalid credentialSubject"):
            validate_badge_payload(payload)

    def test_validate_invalid_credential_subject(self):
        """Test validation fails with non-dict credentialSubject."""
        payload = {"type": ["BADGE_TYPE_MCP_BADGE"], "credentialSubject": "invalid"}

        with pytest.raises(ValueError, match="Missing or invalid credentialSubject"):
            validate_badge_payload(payload)

    def test_validate_empty_credential_subject_id(self):
        """Test validation fails with empty credential subject id."""
        payload = {
            "type": ["BADGE_TYPE_MCP_BADGE"],
            "credentialSubject": {"id": "", "badge": '{"name": "test", "url": "http://test.com"}'},
        }

        with pytest.raises(ValueError, match="Unexpected credential subject id"):
            validate_badge_payload(payload)

    def test_validate_non_string_credential_subject_id(self):
        """Test validation fails with non-string credential subject id."""
        payload = {
            "type": ["BADGE_TYPE_MCP_BADGE"],
            "credentialSubject": {"id": 123, "badge": '{"name": "test", "url": "http://test.com"}'},
        }

        with pytest.raises(ValueError, match="Unexpected credential subject id"):
            validate_badge_payload(payload)

    def test_validate_missing_badge_field(self):
        """Test validation fails with missing badge field."""
        payload = {"type": ["BADGE_TYPE_MCP_BADGE"], "credentialSubject": {"id": "test-user-id"}}

        with pytest.raises(ValueError, match="Missing badge field in credentialSubject"):
            validate_badge_payload(payload)


class TestParseBadgeJsonToMcpServer:
    """Test cases for parse_badge_json_to_mcp_server function."""

    def test_parse_valid_json(self):
        """Test parsing valid badge JSON."""
        badge_data = {
            "name": "test-server",
            "url": "https://example.com",
            "tools": [
                {"name": "test_tool", "description": "A test tool", "parameters": {"type": "object", "properties": {}}}
            ],
            "resources": [{"name": "test_resource", "description": "A test resource", "uri": "test://resource"}],
        }
        badge_json_str = json.dumps(badge_data)

        result = parse_badge_json_to_mcp_server(badge_json_str)

        assert isinstance(result, McpServer)
        assert result.name == "test-server"
        assert result.url == "https://example.com"
        assert len(result.tools) == 1
        assert result.tools[0].name == "test_tool"
        assert len(result.resources) == 1
        assert result.resources[0].name == "test_resource"

    def test_parse_json_without_tools_and_resources(self):
        """Test parsing JSON without tools and resources."""
        badge_data = {"name": "test-server", "url": "https://example.com"}
        badge_json_str = json.dumps(badge_data)

        result = parse_badge_json_to_mcp_server(badge_json_str)

        assert isinstance(result, McpServer)
        assert result.name == "test-server"
        assert result.url == "https://example.com"
        assert len(result.tools) == 0
        assert len(result.resources) == 0

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON raises JSONDecodeError."""
        invalid_json = "invalid json string"

        with pytest.raises(json.JSONDecodeError):
            parse_badge_json_to_mcp_server(invalid_json)

    def test_parse_json_missing_required_fields(self):
        """Test parsing JSON with missing required fields raises KeyError."""
        badge_data = {"url": "https://example.com"}  # Missing 'name'
        badge_json_str = json.dumps(badge_data)

        with pytest.raises(KeyError):
            parse_badge_json_to_mcp_server(badge_json_str)


class TestConvertMcpToolsToMcpTypes:
    """Test cases for convert_mcp_tools_to_mcp_types function."""

    def test_convert_tools(self):
        """Test converting MCP tools to mcp.types.Tool objects."""
        # Create mock MCP tools
        mock_tool1 = Mock()
        mock_tool1.name = "tool1"
        mock_tool1.description = "Description 1"
        mock_tool1.parameters = {"type": "object", "properties": {"param1": {"type": "string"}}}

        mock_tool2 = Mock()
        mock_tool2.name = "tool2"
        mock_tool2.description = "Description 2"
        mock_tool2.parameters = {"type": "object", "properties": {"param2": {"type": "number"}}}

        mock_server = Mock()
        mock_server.tools = [mock_tool1, mock_tool2]

        result = convert_mcp_tools_to_mcp_types(mock_server)

        assert len(result) == 2
        assert all(isinstance(tool, mcp_types.Tool) for tool in result)

        assert result[0].name == "tool1"
        assert result[0].description == "Description 1"
        assert result[0].inputSchema == {"type": "object", "properties": {"param1": {"type": "string"}}}

        assert result[1].name == "tool2"
        assert result[1].description == "Description 2"
        assert result[1].inputSchema == {"type": "object", "properties": {"param2": {"type": "number"}}}

    def test_convert_empty_tools(self):
        """Test converting empty tools list."""
        mock_server = Mock()
        mock_server.tools = []

        result = convert_mcp_tools_to_mcp_types(mock_server)

        assert result == []


class TestDecodeBadgeExtractTools:
    """Test cases for the main decode_badge_extract_tools function."""

    @patch("identity_auth_server.api.utils.decode_badge_jwt")
    @patch("identity_auth_server.api.utils.validate_badge_payload")
    @patch("identity_auth_server.api.utils.parse_badge_json_to_mcp_server")
    @patch("identity_auth_server.api.utils.convert_mcp_tools_to_mcp_types")
    def test_successful_badge_decoding_and_extraction(
        self, mock_convert_tools, mock_parse_badge, mock_validate, mock_decode_jwt
    ):
        """Test successful end-to-end badge decoding and tool extraction."""
        # Setup mocks
        mock_decoded_payload = {
            "type": ["BADGE_TYPE_MCP_BADGE"],
            "credentialSubject": {"id": "test-user-id", "badge": '{"name": "test", "url": "http://test.com"}'},
        }
        mock_decode_jwt.return_value = mock_decoded_payload

        mock_server = Mock()
        mock_parse_badge.return_value = mock_server

        expected_tools = [Mock(spec=mcp_types.Tool)]
        mock_convert_tools.return_value = expected_tools

        # Call the function
        result = decode_badge_extract_tools("test-jwt-token")

        # Verify the calls
        mock_decode_jwt.assert_called_once_with("test-jwt-token")
        mock_validate.assert_called_once_with(mock_decoded_payload)
        mock_parse_badge.assert_called_once_with(mock_decoded_payload["credentialSubject"]["badge"])
        mock_convert_tools.assert_called_once_with(mock_server)

        assert result == expected_tools

    @patch("identity_auth_server.api.utils.decode_badge_jwt")
    def test_jwt_decoding_failure(self, mock_decode_jwt):
        """Test when JWT decoding fails."""
        mock_decode_jwt.side_effect = jwt.DecodeError("Invalid JWT")

        with pytest.raises(jwt.DecodeError, match="Invalid JWT"):
            decode_badge_extract_tools("invalid-token")

    @patch("identity_auth_server.api.utils.decode_badge_jwt")
    @patch("identity_auth_server.api.utils.validate_badge_payload")
    def test_validation_failure(self, mock_validate, mock_decode_jwt):
        """Test when badge payload validation fails."""
        mock_decoded_payload = {"type": ["BADGE_TYPE_OTHER"]}
        mock_decode_jwt.return_value = mock_decoded_payload
        mock_validate.side_effect = ValueError("Validation failed")

        with pytest.raises(ValueError, match="Validation failed"):
            decode_badge_extract_tools("test-token")

    @patch("identity_auth_server.api.utils.decode_badge_jwt")
    @patch("identity_auth_server.api.utils.validate_badge_payload")
    @patch("identity_auth_server.api.utils.parse_badge_json_to_mcp_server")
    def test_json_parsing_failure(self, mock_parse_badge, mock_validate, mock_decode_jwt):
        """Test when badge JSON parsing fails."""
        mock_decoded_payload = {
            "type": ["BADGE_TYPE_MCP_BADGE"],
            "credentialSubject": {"id": "test-user-id", "badge": "invalid json"},
        }
        mock_decode_jwt.return_value = mock_decoded_payload
        mock_parse_badge.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        with pytest.raises(json.JSONDecodeError):
            decode_badge_extract_tools("test-token")


class TestIntegrationWithRealData:
    """Integration tests using more realistic data structures."""

    def test_integration_with_jira_like_data(self):
        """Test with Jira MCP server-like data structure."""
        badge_data = {
            "name": "jira-mcp-server",
            "url": "https://jira.example.com",
            "tools": [
                {
                    "name": "jira_get_issue",
                    "description": "Get details of a specific Jira issue",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Jira issue key (e.g., 'PROJ-123')"}
                        },
                        "required": ["issue_key"],
                    },
                },
                {
                    "name": "jira_search",
                    "description": "Search Jira issues using JQL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "jql": {"type": "string", "description": "JQL query string"},
                            "limit": {"type": "integer", "description": "Maximum number of results", "default": 10},
                        },
                        "required": ["jql"],
                    },
                },
            ],
            "resources": [],
        }

        badge_json_str = json.dumps(badge_data)

        # Test parsing
        mcp_server = parse_badge_json_to_mcp_server(badge_json_str)
        assert mcp_server.name == "jira-mcp-server"
        assert len(mcp_server.tools) == 2

        # Test conversion
        mcp_tools = convert_mcp_tools_to_mcp_types(mcp_server)
        assert len(mcp_tools) == 2
        assert mcp_tools[0].name == "jira_get_issue"
        assert mcp_tools[1].name == "jira_search"
        assert "issue_key" in mcp_tools[0].inputSchema["properties"]
        assert "jql" in mcp_tools[1].inputSchema["properties"]

    @patch("identity_auth_server.api.utils.jwt.decode")
    def test_end_to_end_with_real_badge_file(self, mock_jwt_decode):
        """Test end-to-end flow using the real badge token file (if available)."""
        # Check if the badge file exists and has content
        badge_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test", "api", "data", "jira_mcp_badge.txt"
        )

        if not os.path.exists(badge_file_path):
            pytest.skip("Badge file not available for testing")

        with open(badge_file_path, "r") as f:
            badge_content = f.read().strip()

        if not badge_content:
            pytest.skip("Badge file is empty")

        # Mock the JWT decode response with realistic data
        mock_decoded_payload = {
            "type": ["BADGE_TYPE_MCP_BADGE"],
            "credentialSubject": {
                "id": "test-user-id",
                "badge": json.dumps(
                    {
                        "name": "atlassian-mcp-server",
                        "url": "https://atlassian.example.com",
                        "tools": [
                            {
                                "name": "jira_get_user_profile",
                                "description": "Retrieve profile information for a specific Jira user",
                                "parameters": {
                                    "properties": {
                                        "user_identifier": {
                                            "description": "User identifier (email, username, key, or account ID)",
                                            "title": "User Identifier",
                                            "type": "string",
                                        }
                                    },
                                    "required": ["user_identifier"],
                                    "type": "object",
                                },
                            }
                        ],
                        "resources": [],
                    }
                ),
            },
        }

        mock_jwt_decode.return_value = mock_decoded_payload

        # Call the main function
        result = decode_badge_extract_tools(badge_content)

        # Verify results
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], mcp_types.Tool)
        assert result[0].name == "jira_get_user_profile"
        assert "user_identifier" in result[0].inputSchema["properties"]
