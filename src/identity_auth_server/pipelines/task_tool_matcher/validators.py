"""Common validation logic for TaskToolMatchers."""

from identity_auth_server.pipelines.exceptions import PipelineValidationError
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchInput


class TaskToolValidator:
    """Common validation logic for TaskToolMatchers."""

    @staticmethod
    def validate_tool_availability(input: TaskToolMatchInput) -> None:
        """Validate that the requested tool is available.

        Args:
            input: The task tool match input to validate

        Raises:
            PipelineValidationError: If the requested tool is not available
        """
        if input.requested_tool not in input.available_tools:
            raise PipelineValidationError("Requested tool is not available in the provided tools list")

    @staticmethod
    def validate_task_not_empty(input: TaskToolMatchInput) -> None:
        """Validate that the task description is not empty.

        Args:
            input: The task tool match input to validate

        Raises:
            PipelineValidationError: If the task is empty
        """
        if not input.task or not input.task.strip():
            raise PipelineValidationError("Task description cannot be empty")

    @staticmethod
    def validate_available_tools_not_empty(input: TaskToolMatchInput) -> None:
        """Validate that there are available tools to choose from.

        Args:
            input: The task tool match input to validate

        Raises:
            PipelineValidationError: If no tools are available
        """
        if not input.available_tools:
            raise PipelineValidationError("No available tools provided")

    @staticmethod
    def validate_available_tools_subset_mcp_tools(input: TaskToolMatchInput) -> None:
        """Validate that the available tools are a subset of the MCP tools.

        Args:
            input: The task tool match input to validate

        Raises:
            PipelineValidationError: If available tools are not a subset of MCP tools
        """
        if not set(input.available_tools).issubset({tool.name for tool in input.mcp_tools}):
            raise PipelineValidationError("Available tools must be a subset of the provided MCP tools")

    @classmethod
    def run_common_validations(cls, input: TaskToolMatchInput) -> None:
        """Run all common validations in sequence.

        Args:
            input: The task tool match input to validate

        Raises:
            PipelineValidationError: If any validation fails
        """
        cls.validate_task_not_empty(input)
        cls.validate_available_tools_not_empty(input)
        cls.validate_tool_availability(input)
        cls.validate_available_tools_subset_mcp_tools(input)
