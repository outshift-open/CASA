"""Unit tests for identity_auth_server.api.utils module."""

import json
import os
from unittest.mock import Mock

import identityservice.badge.mcp as sdk
import jwt
import pytest
from mcp import types as mcp_types

from identity_auth_server.api.utils import (
    convert_mcp_server,
    decode_badge_extract_mcp_server,
    decode_badge_jwt,
    parse_badge_json_to_mcp_server,
    validate_badge_payload,
)
from identity_auth_server.types import McpServer


class TestDecodeBadgeJwt:
    """Tests for decode_badge_jwt function."""

    def test_decode_valid_jwt_token(self):
        """Test decoding a valid JWT token without verification."""
        # Use the test badge token from the test data
        test_data_path = os.path.join(os.path.dirname(__file__), "data", "jira_mcp_badge.txt")
        with open(test_data_path, "r") as f:
            test_badge_token = f.read().strip()

        result = decode_badge_jwt(test_badge_token)

        assert isinstance(result, dict)
        assert "type" in result
        assert "credentialSubject" in result
        assert result["type"] == ["BADGE_TYPE_MCP_BADGE"]

    @pytest.mark.parametrize("invalid_token", ["invalid.jwt.token", "not-a-jwt-token-at-all", ""])
    def test_decode_invalid_jwt_token(self, invalid_token):
        """Test that invalid JWT tokens raise DecodeError."""
        with pytest.raises(jwt.DecodeError):
            decode_badge_jwt(invalid_token)


class TestValidateBadgePayload:
    """Tests for validate_badge_payload function."""

    def test_validate_valid_badge_payload(self):
        """Test validation of a valid badge payload."""
        valid_payload = {
            "type": ["BADGE_TYPE_MCP_BADGE"],
            "credentialSubject": {
                "id": "AGNTCY-21c8e890-226c-4c3e-b601-ab05188ac426",
                "badge": '{"name": "Test Server"}',
            },
        }

        # Should not raise any exception
        validate_badge_payload(valid_payload)

    def test_validate_invalid_badge_type(self):
        """Test that invalid badge type raises ValueError."""
        invalid_payload = {
            "type": ["INVALID_BADGE_TYPE"],
            "credentialSubject": {"id": "test-id", "badge": '{"name": "Test Server"}'},
        }

        with pytest.raises(ValueError, match="Unexpected badge type"):
            validate_badge_payload(invalid_payload)

    def test_validate_missing_credential_subject(self):
        """Test that missing credentialSubject raises ValueError."""
        invalid_payload = {"type": ["BADGE_TYPE_MCP_BADGE"]}

        with pytest.raises(ValueError, match="Missing or invalid credentialSubject"):
            validate_badge_payload(invalid_payload)

    def test_validate_invalid_credential_subject_type(self):
        """Test that invalid credentialSubject type raises ValueError."""
        invalid_payload = {"type": ["BADGE_TYPE_MCP_BADGE"], "credentialSubject": "not a dict"}

        with pytest.raises(ValueError, match="Missing or invalid credentialSubject"):
            validate_badge_payload(invalid_payload)

    @pytest.mark.parametrize(
        "invalid_id,description", [("", "empty string"), (123, "non-string type"), (None, "None value")]
    )
    def test_validate_invalid_credential_id(self, invalid_id, description):
        """Test that invalid credential subject ids raise ValueError."""
        invalid_payload = {
            "type": ["BADGE_TYPE_MCP_BADGE"],
            "credentialSubject": {"id": invalid_id, "badge": '{"name": "Test Server"}'},
        }

        with pytest.raises(ValueError, match="Unexpected credential subject id"):
            validate_badge_payload(invalid_payload)

    def test_validate_missing_badge_field(self):
        """Test that missing badge field raises ValueError."""
        invalid_payload = {"type": ["BADGE_TYPE_MCP_BADGE"], "credentialSubject": {"id": "test-id"}}

        with pytest.raises(ValueError, match="Missing badge field in credentialSubject"):
            validate_badge_payload(invalid_payload)


class TestParseBadgeJsonToMcpServer:
    """Tests for parse_badge_json_to_mcp_server function."""

    def test_parse_valid_badge_json(self):
        """Test parsing valid badge JSON to McpServer."""
        badge_json = json.dumps(
            {
                "name": "Test Server",
                "url": "http://localhost:9000/mcp",
                "tools": [
                    {
                        "name": "test_tool",
                        "description": "A test tool",
                        "parameters": {"type": "object", "properties": {}},
                    }
                ],
                "resources": [{"name": "test_resource", "description": "A test resource", "uri": "test://resource"}],
            }
        )

        result = parse_badge_json_to_mcp_server(badge_json)

        assert isinstance(result, sdk.McpServer)
        assert result.name == "Test Server"
        assert result.url == "http://localhost:9000/mcp"
        assert len(result.tools) == 1
        assert len(result.resources) == 1
        assert result.tools[0].name == "test_tool"
        assert result.resources[0].name == "test_resource"

    def test_parse_badge_json_with_empty_tools_resources(self):
        """Test parsing badge JSON with empty tools and resources."""
        badge_json = json.dumps({"name": "Test Server", "url": "http://localhost:9000/mcp"})

        result = parse_badge_json_to_mcp_server(badge_json)

        assert isinstance(result, sdk.McpServer)
        assert result.name == "Test Server"
        assert len(result.tools) == 0
        assert len(result.resources) == 0

    def test_parse_invalid_json(self):
        """Test that invalid JSON raises JSONDecodeError."""
        invalid_json = "not valid json {"

        with pytest.raises(json.JSONDecodeError):
            parse_badge_json_to_mcp_server(invalid_json)

    def test_parse_missing_required_fields(self):
        """Test that missing required fields raises KeyError."""
        badge_json = json.dumps({"tools": [], "resources": []})

        with pytest.raises(KeyError):
            parse_badge_json_to_mcp_server(badge_json)


class TestConvertMcpServer:
    """Tests for convert_mcp_server function."""

    @pytest.mark.parametrize("has_tools_resources", [True, False])
    def test_convert_mcp_server(self, has_tools_resources):
        """Test converting McpServer with and without tools and resources."""
        # Create mock SDK objects conditionally
        mock_mcp_server = Mock(spec=sdk.McpServer)

        if has_tools_resources:
            mock_tool = Mock()
            mock_tool.name = "test_tool"
            mock_tool.description = "A test tool"
            mock_tool.parameters = {"type": "object", "properties": {}}

            mock_resource = Mock()
            mock_resource.name = "test_resource"
            mock_resource.description = "A test resource"
            mock_resource.uri = "test://resource"

            mock_mcp_server.name = "Test Server"
            mock_mcp_server.tools = [mock_tool]
            mock_mcp_server.resources = [mock_resource]

            expected_tool_count = 1
            expected_resource_count = 1
        else:
            mock_mcp_server.name = "Empty Server"
            mock_mcp_server.tools = []
            mock_mcp_server.resources = []

            expected_tool_count = 0
            expected_resource_count = 0

        result = convert_mcp_server(mock_mcp_server)

        assert isinstance(result, McpServer)
        assert len(result.tools) == expected_tool_count
        assert len(result.resources) == expected_resource_count

        if has_tools_resources:
            assert isinstance(result.tools[0], mcp_types.Tool)
            assert isinstance(result.resources[0], mcp_types.Resource)
            assert result.tools[0].name == "test_tool"
            assert result.resources[0].name == "test_resource"


class TestDecodeBadgeExtractMcpServer:
    """Tests for decode_badge_extract_mcp_server function."""

    def test_end_to_end_happy_path(self):
        """Test end-to-end processing of a valid badge token."""
        # Use the test badge token from the test data
        test_data_path = os.path.join(os.path.dirname(__file__), "data", "jira_mcp_badge.txt")
        with open(test_data_path, "r") as f:
            test_badge_token = f.read().strip()

        result = decode_badge_extract_mcp_server(test_badge_token)

        assert isinstance(result, McpServer)
        assert result.name == "Jira MCP Server"
        assert len(result.tools) > 0  # Should have Jira tools
        assert isinstance(result.tools[0], mcp_types.Tool)
        # Check for some expected Jira tools
        tool_names = [tool.name for tool in result.tools]
        assert "jira_get_user_profile" in tool_names
        assert "jira_get_issue" in tool_names

    def test_with_invalid_jwt_token(self):
        """Test that invalid JWT token propagates DecodeError."""
        invalid_token = "invalid.jwt.token"

        with pytest.raises(jwt.DecodeError):
            decode_badge_extract_mcp_server(invalid_token)
