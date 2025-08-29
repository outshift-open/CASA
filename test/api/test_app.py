"""Tests for identity_auth_server.api.app module."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from mcp import types as mcp_types

from identity_auth_server.api.app import app
from identity_auth_server.api.types import (
    IntentMcpBadgeToolMatchRequest,
    IntentMcpToolMatchRequest,
)
from identity_auth_server.pipelines.exceptions import PipelineValidationError
from identity_auth_server.pipelines.task_tool_matcher.types import (
    TaskToolMatcherType,
    TaskToolMatchOutput,
    TaskToolMatchReason,
)


def serialize_mcp_tool_request(request: IntentMcpToolMatchRequest) -> dict:
    """Helper function to serialize MCP tool request for JSON transmission."""
    request_data = request.model_dump()
    request_data["mcp_tools"] = [
        {"name": tool.name, "description": tool.description, "inputSchema": tool.inputSchema}
        for tool in request.mcp_tools
    ]
    return request_data


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def sample_mcp_badge_request():
    """Sample MCP badge request data."""
    # load badge from file
    badge_file_path = "test/api/data/jira_mcp_badge.txt"
    with open(badge_file_path, "r") as f:
        badge_token = f.read().strip()

    return IntentMcpBadgeToolMatchRequest(
        task="analyze user input",
        requested_tool="text_analyzer",
        available_tools=["text_analyzer", "file_reader", "web_scraper"],
        mcp_badge=badge_token,
    )


@pytest.fixture
def sample_mcp_tool_request():
    """Sample MCP tool request data."""
    # Create actual MCP Tool object
    mock_tool = mcp_types.Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={"type": "object", "properties": {"param": {"type": "string"}}},
    )
    return IntentMcpToolMatchRequest(
        task="analyze user input",
        requested_tool="test_tool",
        available_tools=["test_tool", "other_tool"],
        mcp_tools=[mock_tool],
    )


@pytest.fixture
def successful_match_result():
    """Sample successful match result."""
    return TaskToolMatchOutput(task_tool_match=True, reason=None)


@pytest.fixture
def failed_match_result():
    """Sample failed match result."""
    return TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.RANDOM_NO_MATCH)


class TestMcpBadgeToolMatchEndpoint:
    """Tests for /task/intent/mcp/badge/tool-match endpoint."""

    @patch("identity_auth_server.api.app.TaskToolMatcherFactory.create")
    def test_successful_badge_tool_match(self, mock_factory, client, sample_mcp_badge_request, successful_match_result):
        """Test successful MCP badge tool match."""
        # Setup mock
        mock_matcher = MagicMock()
        mock_matcher.match.return_value = successful_match_result
        mock_factory.return_value = mock_matcher

        # Make request
        response = client.post("/task/intent/mcp/badge/tool-match", json=sample_mcp_badge_request.model_dump())

        # Assertions
        assert response.status_code == 200
        assert response.json() == {"task_tool_match": True, "reason": None}

        # Verify factory was called with default matcher type
        mock_factory.assert_called_once_with(TaskToolMatcherType.RANDOM)

        # Verify matcher was called
        mock_matcher.match.assert_called_once()

    @patch("identity_auth_server.api.app.TaskToolMatcherFactory.create")
    def test_failed_badge_tool_match(self, mock_factory, client, sample_mcp_badge_request, failed_match_result):
        """Test failed MCP badge tool match."""
        # Setup mock
        mock_matcher = MagicMock()
        mock_matcher.match.return_value = failed_match_result
        mock_factory.return_value = mock_matcher

        # Make request
        response = client.post("/task/intent/mcp/badge/tool-match", json=sample_mcp_badge_request.model_dump())

        # Assertions
        assert response.status_code == 200
        assert response.json() == {
            "task_tool_match": False,
            "reason": "Random matcher decided this tool doesn't match the task",
        }

    @patch("identity_auth_server.api.app.TaskToolMatcherFactory.create")
    def test_badge_tool_match_with_custom_matcher_type(
        self, mock_factory, client, sample_mcp_badge_request, successful_match_result
    ):
        """Test MCP badge tool match with custom matcher type."""
        # Setup mock
        mock_matcher = MagicMock()
        mock_matcher.match.return_value = successful_match_result
        mock_factory.return_value = mock_matcher

        # Make request with custom matcher type
        response = client.post(
            "/task/intent/mcp/badge/tool-match",
            json=sample_mcp_badge_request.model_dump(),
            params={"task_tool_matcher": "random"},
        )

        # Assertions
        assert response.status_code == 200
        mock_factory.assert_called_once_with(TaskToolMatcherType.RANDOM)

    @patch("identity_auth_server.api.app.TaskToolMatcherFactory.create")
    def test_badge_tool_match_validation_error(self, mock_factory, client, sample_mcp_badge_request):
        """Test MCP badge tool match with validation error."""
        # Setup mock to raise validation error
        mock_matcher = MagicMock()
        mock_matcher.match.side_effect = PipelineValidationError("Tool not available")
        mock_factory.return_value = mock_matcher

        # Make request
        response = client.post("/task/intent/mcp/badge/tool-match", json=sample_mcp_badge_request.model_dump())

        # Assertions
        assert response.status_code == 400
        assert response.json() == {"detail": "Tool not available"}

    def test_badge_tool_match_invalid_request(self, client):
        """Test MCP badge tool match with invalid request data."""
        invalid_request = {
            "task": "",  # Invalid empty task
            "requested_tool": "test_tool",
            # Missing required fields
        }

        response = client.post("/task/intent/mcp/badge/tool-match", json=invalid_request)

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_badge_tool_match_missing_fields(self, client):
        """Test MCP badge tool match with missing required fields."""
        incomplete_request = {
            "task": "analyze data"
            # Missing other required fields
        }

        response = client.post("/task/intent/mcp/badge/tool-match", json=incomplete_request)

        assert response.status_code == 422
        error_detail = response.json()
        assert "detail" in error_detail


class TestMcpToolMatchEndpoint:
    """Tests for /task/intent/mcp/tool-match endpoint."""

    @patch("identity_auth_server.api.app.TaskToolMatcherFactory.create")
    def test_successful_tool_match(self, mock_factory, client, sample_mcp_tool_request, successful_match_result):
        """Test successful MCP tool match."""
        # Setup mock
        mock_matcher = MagicMock()
        mock_matcher.match.return_value = successful_match_result
        mock_factory.return_value = mock_matcher

        # Make request
        response = client.post("/task/intent/mcp/tool-match", json=serialize_mcp_tool_request(sample_mcp_tool_request))

        # Assertions
        assert response.status_code == 200
        assert response.json() == {"task_tool_match": True, "reason": None}

    @patch("identity_auth_server.api.app.TaskToolMatcherFactory.create")
    def test_failed_tool_match(self, mock_factory, client, sample_mcp_tool_request, failed_match_result):
        """Test failed MCP tool match."""
        # Setup mock
        mock_matcher = MagicMock()
        mock_matcher.match.return_value = failed_match_result
        mock_factory.return_value = mock_matcher

        # Make request
        response = client.post("/task/intent/mcp/tool-match", json=serialize_mcp_tool_request(sample_mcp_tool_request))

        # Assertions
        assert response.status_code == 200
        assert response.json() == {
            "task_tool_match": False,
            "reason": "Random matcher decided this tool doesn't match the task",
        }

    @patch("identity_auth_server.api.app.TaskToolMatcherFactory.create")
    def test_tool_match_with_custom_matcher_type(
        self, mock_factory, client, sample_mcp_tool_request, successful_match_result
    ):
        """Test MCP tool match with custom matcher type."""
        # Setup mock
        mock_matcher = MagicMock()
        mock_matcher.match.return_value = successful_match_result
        mock_factory.return_value = mock_matcher

        # Make request with custom matcher type
        response = client.post(
            "/task/intent/mcp/tool-match",
            json=serialize_mcp_tool_request(sample_mcp_tool_request),
            params={"task_tool_matcher": "random"},
        )

        # Assertions
        assert response.status_code == 200
        mock_factory.assert_called_once_with(TaskToolMatcherType.RANDOM)

    @patch("identity_auth_server.api.app.TaskToolMatcherFactory.create")
    def test_tool_match_validation_error(self, mock_factory, client, sample_mcp_tool_request):
        """Test MCP tool match with validation error."""
        # Setup mock to raise validation error
        mock_matcher = MagicMock()
        mock_matcher.match.side_effect = PipelineValidationError("No available tools")
        mock_factory.return_value = mock_matcher

        # Make request
        response = client.post("/task/intent/mcp/tool-match", json=serialize_mcp_tool_request(sample_mcp_tool_request))

        # Assertions
        assert response.status_code == 400
        assert response.json() == {"detail": "No available tools"}

    def test_tool_match_invalid_request(self, client):
        """Test MCP tool match with invalid request data."""
        invalid_request = {
            "task": "",  # Invalid empty task
            "requested_tool": "",
            "available_tools": [],
            "mcp_tools": "invalid_mcp_tools",  # Should be a list
        }

        response = client.post("/task/intent/mcp/tool-match", json=invalid_request)

        # Should return 422 for validation error
        assert response.status_code == 422


class TestEndpointEdgeCases:
    """Test edge cases and error conditions."""

    def test_invalid_http_method_badge_endpoint(self, client):
        """Test invalid HTTP method on badge endpoint."""
        response = client.get("/task/intent/mcp/badge/tool-match")
        assert response.status_code == 405  # Method Not Allowed

    def test_invalid_http_method_tool_endpoint(self, client):
        """Test invalid HTTP method on tool endpoint."""
        response = client.get("/task/intent/mcp/tool-match")
        assert response.status_code == 405  # Method Not Allowed

    def test_nonexistent_endpoint(self, client):
        """Test request to nonexistent endpoint."""
        response = client.post("/nonexistent-endpoint", json={})
        assert response.status_code == 404  # Not Found

    @patch("identity_auth_server.api.app.TaskToolMatcherFactory.create")
    def test_different_validation_error_messages(self, mock_factory, client, sample_mcp_badge_request):
        """Test different validation error messages."""
        # Setup mock to raise different validation errors
        validation_errors = [
            "Task cannot be empty",
            "Tool not available in the provided list",
            "No available tools provided",
            "Invalid MCP badge format",
        ]

        for error_message in validation_errors:
            mock_matcher = MagicMock()
            mock_matcher.match.side_effect = PipelineValidationError(error_message)
            mock_factory.return_value = mock_matcher

            response = client.post("/task/intent/mcp/badge/tool-match", json=sample_mcp_badge_request.model_dump())

            assert response.status_code == 400
            assert response.json() == {"detail": error_message}


class TestResponseFormat:
    """Test response format and serialization."""

    @patch("identity_auth_server.api.app.TaskToolMatcherFactory.create")
    def test_response_content_type(self, mock_factory, client, sample_mcp_badge_request, successful_match_result):
        """Test that response has correct content type."""
        mock_matcher = MagicMock()
        mock_matcher.match.return_value = successful_match_result
        mock_factory.return_value = mock_matcher

        response = client.post("/task/intent/mcp/badge/tool-match", json=sample_mcp_badge_request.model_dump())

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @patch("identity_auth_server.api.app.TaskToolMatcherFactory.create")
    def test_response_structure_consistency(self, mock_factory, client, sample_mcp_badge_request):
        """Test that response structure is consistent."""
        # Test with different result types
        test_results = [
            TaskToolMatchOutput(task_tool_match=True, reason=None),
            TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.TOOL_NOT_AVAILABLE),
            TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.TASK_EMPTY),
            TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.NO_AVAILABLE_TOOLS),
        ]

        for result in test_results:
            mock_matcher = MagicMock()
            mock_matcher.match.return_value = result
            mock_factory.return_value = mock_matcher

            response = client.post("/task/intent/mcp/badge/tool-match", json=sample_mcp_badge_request.model_dump())

            assert response.status_code == 200
            json_response = response.json()

            # Check required fields are always present
            assert "task_tool_match" in json_response
            assert "reason" in json_response

            # Check types
            assert isinstance(json_response["task_tool_match"], bool)
            # reason can be None or string
            assert json_response["reason"] is None or isinstance(json_response["reason"], str)
