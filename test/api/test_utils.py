"""Unit tests for identity_auth_server.api.utils module."""

import json
import os
from unittest.mock import Mock, patch

import pytest
from identityservice.badge.mcp import McpServer
from mcp import types as mcp_types
from outshift.identity.service.v1alpha1.badge_pb2 import VerificationResult

from identity_auth_server.api.utils import (
    convert_mcp_tools_to_mcp_types,
    create_identity_service_client,
    parse_badge_json_to_mcp_server,
    validate_verification_result,
    verify_badge_with_identity_service,
    verify_identity_service_badge_extract_tools,
)


class TestCreateIdentityServiceClient:
    """Test cases for create_identity_service_client function."""

    @patch.dict(os.environ, {"IDENTITY_SERVICE_API_KEY": "test-api-key"})
    @patch("identity_auth_server.api.utils.sdk.IdentityServiceSdk")
    def test_create_client_with_api_key(self, mock_sdk):
        """Test creating client with API key from environment."""
        mock_client = Mock()
        mock_sdk.return_value = mock_client

        result = create_identity_service_client()

        mock_sdk.assert_called_once_with(api_key="test-api-key")
        assert result == mock_client

    @patch.dict(os.environ, {}, clear=True)
    @patch("identity_auth_server.api.utils.sdk.IdentityServiceSdk")
    def test_create_client_without_api_key(self, mock_sdk):
        """Test creating client without API key."""
        mock_client = Mock()
        mock_sdk.return_value = mock_client

        result = create_identity_service_client()

        mock_sdk.assert_called_once_with(api_key=None)
        assert result == mock_client


class TestVerifyBadgeWithIdentityService:
    """Test cases for verify_badge_with_identity_service function."""

    def test_verify_badge_success(self):
        """Test successful badge verification."""
        mock_client = Mock()
        mock_result = Mock()
        mock_client.verify_badge.return_value = mock_result

        result = verify_badge_with_identity_service("test-token", mock_client)

        mock_client.verify_badge.assert_called_once_with("test-token")
        assert result == mock_result

    def test_verify_badge_client_raises_exception(self):
        """Test badge verification when client raises an exception."""
        mock_client = Mock()
        mock_client.verify_badge.side_effect = Exception("Service unavailable")

        with pytest.raises(Exception, match="Service unavailable"):
            verify_badge_with_identity_service("test-token", mock_client)


class TestValidateVerificationResult:
    """Test cases for validate_verification_result function."""

    def test_validate_success(self):
        """Test successful validation of verification result."""
        # Create a mock verification result
        mock_result = Mock(spec=VerificationResult)
        mock_result.status = True

        # Create nested mock structure
        mock_credential_subject = Mock()
        mock_credential_subject.id = "test-user-id"
        mock_document = Mock()
        mock_document.credential_subject = mock_credential_subject
        mock_document.type = ["BADGE_TYPE_MCP_BADGE"]
        mock_result.document = mock_document

        # Should not raise any exception
        validate_verification_result(mock_result)

    def test_validate_wrong_type(self):
        """Test validation fails with wrong result type."""
        mock_result = Mock()  # Not a VerificationResult

        with pytest.raises(ValueError, match="Unexpected result type"):
            validate_verification_result(mock_result)

    def test_validate_status_false(self):
        """Test validation fails when status is False."""
        mock_result = Mock(spec=VerificationResult)
        mock_result.status = False

        with pytest.raises(ValueError, match="Badge verification failed"):
            validate_verification_result(mock_result)

    def test_validate_empty_credential_subject_id(self):
        """Test validation fails with empty credential subject id."""
        mock_result = Mock(spec=VerificationResult)
        mock_result.status = True

        # Create nested mock structure
        mock_credential_subject = Mock()
        mock_credential_subject.id = ""
        mock_document = Mock()
        mock_document.credential_subject = mock_credential_subject
        mock_result.document = mock_document

        with pytest.raises(ValueError, match="Unexpected credential subject id"):
            validate_verification_result(mock_result)

    def test_validate_non_string_credential_subject_id(self):
        """Test validation fails with non-string credential subject id."""
        mock_result = Mock(spec=VerificationResult)
        mock_result.status = True

        # Create nested mock structure
        mock_credential_subject = Mock()
        mock_credential_subject.id = 123
        mock_document = Mock()
        mock_document.credential_subject = mock_credential_subject
        mock_result.document = mock_document

        with pytest.raises(ValueError, match="Unexpected credential subject id"):
            validate_verification_result(mock_result)

    def test_validate_wrong_document_type(self):
        """Test validation fails with wrong document type."""
        mock_result = Mock(spec=VerificationResult)
        mock_result.status = True

        # Create nested mock structure
        mock_credential_subject = Mock()
        mock_credential_subject.id = "test-user-id"
        mock_document = Mock()
        mock_document.credential_subject = mock_credential_subject
        mock_document.type = ["BADGE_TYPE_OTHER"]
        mock_result.document = mock_document

        with pytest.raises(ValueError, match="Unexpected document type"):
            validate_verification_result(mock_result)


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


class TestVerifyIdentityServiceBadgeExtractTools:
    """Test cases for the main verify_identity_service_badge_extract_tools function."""

    @patch("identity_auth_server.api.utils.create_identity_service_client")
    @patch("identity_auth_server.api.utils.verify_badge_with_identity_service")
    @patch("identity_auth_server.api.utils.validate_verification_result")
    @patch("identity_auth_server.api.utils.parse_badge_json_to_mcp_server")
    @patch("identity_auth_server.api.utils.convert_mcp_tools_to_mcp_types")
    def test_successful_badge_verification_and_extraction(
        self, mock_convert_tools, mock_parse_badge, mock_validate, mock_verify_badge, mock_create_client
    ):
        """Test successful end-to-end badge verification and tool extraction."""
        # Setup mocks
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        mock_verified_result = Mock()
        mock_verified_result.document.credential_subject.badge = '{"name": "test", "url": "http://test.com"}'
        mock_verify_badge.return_value = mock_verified_result

        mock_server = Mock()
        mock_parse_badge.return_value = mock_server

        expected_tools = [Mock(spec=mcp_types.Tool)]
        mock_convert_tools.return_value = expected_tools

        # Call the function
        result = verify_identity_service_badge_extract_tools("test-token")

        # Verify the calls
        mock_create_client.assert_called_once()
        mock_verify_badge.assert_called_once_with("test-token", mock_client)
        mock_validate.assert_called_once_with(mock_verified_result)
        mock_parse_badge.assert_called_once_with(mock_verified_result.document.credential_subject.badge)
        mock_convert_tools.assert_called_once_with(mock_server)

        assert result == expected_tools

    @patch("identity_auth_server.api.utils.create_identity_service_client")
    @patch("identity_auth_server.api.utils.verify_badge_with_identity_service")
    def test_badge_verification_failure(self, mock_verify_badge, mock_create_client):
        """Test when badge verification fails."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        mock_verify_badge.side_effect = Exception("Verification failed")

        with pytest.raises(Exception, match="Verification failed"):
            verify_identity_service_badge_extract_tools("invalid-token")

    @patch("identity_auth_server.api.utils.create_identity_service_client")
    @patch("identity_auth_server.api.utils.verify_badge_with_identity_service")
    @patch("identity_auth_server.api.utils.validate_verification_result")
    def test_validation_failure(self, mock_validate, mock_verify_badge, mock_create_client):
        """Test when verification result validation fails."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        mock_verified_result = Mock()
        mock_verify_badge.return_value = mock_verified_result
        mock_validate.side_effect = ValueError("Validation failed")

        with pytest.raises(ValueError, match="Validation failed"):
            verify_identity_service_badge_extract_tools("test-token")

    @patch("identity_auth_server.api.utils.create_identity_service_client")
    @patch("identity_auth_server.api.utils.verify_badge_with_identity_service")
    @patch("identity_auth_server.api.utils.validate_verification_result")
    @patch("identity_auth_server.api.utils.parse_badge_json_to_mcp_server")
    def test_json_parsing_failure(self, mock_parse_badge, mock_validate, mock_verify_badge, mock_create_client):
        """Test when badge JSON parsing fails."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        mock_verified_result = Mock()
        mock_verify_badge.return_value = mock_verified_result
        mock_parse_badge.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        with pytest.raises(json.JSONDecodeError):
            verify_identity_service_badge_extract_tools("test-token")


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

    @patch.dict(os.environ, {"IDENTITY_SERVICE_API_KEY": "test-api-key"})
    @patch("identity_auth_server.api.utils.sdk.IdentityServiceSdk")
    def test_end_to_end_with_real_badge_file(self, mock_sdk):
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

        # Mock the SDK response with realistic data
        mock_verification_result = Mock(spec=VerificationResult)
        mock_verification_result.status = True

        # Create the nested structure
        mock_credential_subject = Mock()
        mock_credential_subject.id = "test-user-id"
        mock_credential_subject.badge = json.dumps(
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
        )

        mock_document = Mock()
        mock_document.credential_subject = mock_credential_subject
        mock_document.type = ["BADGE_TYPE_MCP_BADGE"]
        mock_verification_result.document = mock_document

        mock_client = Mock()
        mock_client.verify_badge.return_value = mock_verification_result
        mock_sdk.return_value = mock_client

        # Call the main function
        result = verify_identity_service_badge_extract_tools(badge_content)

        # Verify results
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], mcp_types.Tool)
        assert result[0].name == "jira_get_user_profile"
        assert "user_identifier" in result[0].inputSchema["properties"]
