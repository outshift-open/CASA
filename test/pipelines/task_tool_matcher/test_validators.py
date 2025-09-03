"""Tests for identity_auth_server.pipelines.task_tool_matcher.validators module."""

import pytest
from mcp.types import Tool

from identity_auth_server.pipelines.exceptions import PipelineValidationError
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchInput
from identity_auth_server.pipelines.task_tool_matcher.validators import TaskToolValidator
from identity_auth_server.types import McpServer


class TestTaskToolValidator:
    """Tests for TaskToolValidator class."""

    def _create_input(self, task="Valid task", requested_tool="test_tool", available_tools=None):
        """Create a TaskToolMatchInput for testing."""
        if available_tools is None:
            available_tools = [requested_tool]

        tools = [
            Tool(
                name=tool_name, description=f"{tool_name} description", inputSchema={"type": "object", "properties": {}}
            )
            for tool_name in available_tools
        ]
        mcp_server = McpServer(name="test_server", tools=tools, resources=[])
        return TaskToolMatchInput(task=task, requested_tool=requested_tool, mcp_server=mcp_server)

    def test_all_validations_pass_with_valid_input(self):
        """Valid input passes all validations."""
        input_data = self._create_input()
        # Should not raise
        TaskToolValidator.run_common_validations(input_data)

    @pytest.mark.parametrize("task", ["", "   "])
    def test_empty_task_validation_fails(self, task):
        """Empty or whitespace-only tasks fail validation."""
        input_data = self._create_input(task=task)
        with pytest.raises(PipelineValidationError, match="Task description cannot be empty"):
            TaskToolValidator.validate_task_not_empty(input_data)

    @pytest.mark.parametrize("requested_tool", ["", "   "])
    def test_empty_requested_tool_validation_fails(self, requested_tool):
        """Empty or whitespace-only requested tools fail validation."""
        input_data = self._create_input(requested_tool=requested_tool, available_tools=["any_tool"])
        with pytest.raises(PipelineValidationError, match="Requested tool cannot be empty"):
            TaskToolValidator.validate_requested_tool_not_empty(input_data)

    def test_requested_tool_not_in_mcp_tools_fails(self):
        """Tool not in MCP server tools fails validation."""
        input_data = self._create_input(requested_tool="nonexistent_tool", available_tools=["different_tool"])
        with pytest.raises(PipelineValidationError, match="Requested tool must be one of the provided MCP tools"):
            TaskToolValidator.validate_requested_tool_within_mcp_tools(input_data)

    def test_validation_stops_at_first_failure(self):
        """Validation stops at first failure."""
        input_data = self._create_input(task="")  # This will fail first
        with pytest.raises(PipelineValidationError, match="Task description cannot be empty"):
            TaskToolValidator.run_common_validations(input_data)
