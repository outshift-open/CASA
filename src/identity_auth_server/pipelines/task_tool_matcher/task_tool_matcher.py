"""Task Tool Matcher Interface and Factory."""

import logging
from abc import ABC, abstractmethod

from identity_auth_server.pipelines.task_tool_matcher.types import (
    TaskToolMatcherType,
    TaskToolMatchInput,
    TaskToolMatchOutput,
)
from identity_auth_server.pipelines.task_tool_matcher.validators import TaskToolValidator


class TaskToolMatcher(ABC):
    """Abstract base class for task-tool matchers."""

    def __init__(self):
        """Initialize the task-tool matcher."""
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

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
            input (TaskToolMatchInput): The task description, requested tool, and MCP Server details

        Returns:
            TaskToolMatchResult with match boolean and optional reason
        """
        pass

    def set_tuning_mode(self) -> None:
        """Matcher in tuning mode."""
        self.tuning = True


class TaskToolMatcherFactory:
    """Factory for creating TaskToolMatcher instances."""

    @staticmethod
    def create(matcher_type: TaskToolMatcherType, **matcher_kwargs) -> TaskToolMatcher:
        """Create a TaskToolMatcher instance based on the specified type.

        Args:
            matcher_type: The type of TaskToolMatcher to create
            matcher_kwargs: Additional keyword arguments for the matcher

        Returns:
            TaskToolMatcher: An instance of the requested matcher type

        Raises:
            ValueError: If the matcher type is not supported
        """
        logging.getLogger(__name__).info(f"Creating TaskToolMatcher of type: {matcher_type}")
        if matcher_type == TaskToolMatcherType.RANDOM:
            from identity_auth_server.pipelines.task_tool_matcher.random.random import RandomTaskToolMatcher

            return RandomTaskToolMatcher()
        if matcher_type == TaskToolMatcherType.EMBEDDINGS:
            from identity_auth_server.pipelines.task_tool_matcher.embeddings.embeddings import EmbeddingsTaskToolMatcher

            return EmbeddingsTaskToolMatcher(**matcher_kwargs)

        if matcher_type == TaskToolMatcherType.HYBRID:
            from identity_auth_server.pipelines.task_tool_matcher.hybrid.hybrid import HybridTaskToolMatcher

            return HybridTaskToolMatcher(**matcher_kwargs)

        if matcher_type == TaskToolMatcherType.LLM_VERIFIER:
            from identity_auth_server.pipelines.task_tool_matcher.llm_verifier.llm_verifier import (
                LlmVerifierTaskToolMatcher,
            )

            return LlmVerifierTaskToolMatcher(**matcher_kwargs)

        else:
            logging.getLogger(__name__).error(f"Unsupported task tool matcher type: {matcher_type}")
            raise ValueError(f"Unsupported task tool matcher type: {matcher_type}")
