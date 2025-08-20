"""Task Tool Matcher Interface and Factory."""

from abc import ABC, abstractmethod

from identity_auth_server.pipelines.task_tool_matcher.types import (
    TaskToolMatcherType,
    TaskToolMatchInput,
    TaskToolMatchOutput,
)
from identity_auth_server.pipelines.task_tool_matcher.validators import TaskToolValidator


class TaskToolMatcher(ABC):
    """Abstract base class for task-tool matchers."""

    def _validate_input(self, input: TaskToolMatchInput) -> None:
        """Run common validations on the input.

        Args:
            input: The task tool match input to validate

        Raises:
            PipelineValidationError: If validation fails
        """
        TaskToolValidator.run_common_validations(input)

    @abstractmethod
    def match(
        self,
        input: TaskToolMatchInput,
    ) -> TaskToolMatchOutput:
        """Determine if a requested tool matches the given task.

        Args:
            input (TaskToolMatchInput): The task description, requested tool, available tools, and MCP tools.

        Returns:
            TaskToolMatchResult with match boolean and optional reason
        """
        pass


class TaskToolMatcherFactory:
    """Factory for creating TaskToolMatcher instances."""

    @staticmethod
    def create(matcher_type: TaskToolMatcherType) -> TaskToolMatcher:
        """Create a TaskToolMatcher instance based on the specified type.

        Args:
            matcher_type: The type of TaskToolMatcher to create

        Returns:
            TaskToolMatcher: An instance of the requested matcher type

        Raises:
            ValueError: If the matcher type is not supported
        """
        if matcher_type == TaskToolMatcherType.RANDOM:
            from identity_auth_server.pipelines.task_tool_matcher.random.random import RandomTaskToolMatcher

            return RandomTaskToolMatcher()
        else:
            raise ValueError(f"Unsupported task tool matcher type: {matcher_type}")
