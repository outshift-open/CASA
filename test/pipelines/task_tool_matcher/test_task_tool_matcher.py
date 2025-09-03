"""Tests for identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher module."""

from unittest.mock import Mock, patch

import pytest

from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import (
    TaskToolMatcher,
    TaskToolMatcherFactory,
)
from identity_auth_server.pipelines.task_tool_matcher.types import (
    TaskToolMatcherType,
    TaskToolMatchInput,
    TaskToolMatchOutput,
)


class ConcreteTaskToolMatcher(TaskToolMatcher):
    """Concrete implementation for testing abstract base class."""

    def match(self, input: TaskToolMatchInput) -> TaskToolMatchOutput:
        """Simple implementation to always return True."""
        return TaskToolMatchOutput(task_tool_match=True)


class TestTaskToolMatcher:
    """Tests for TaskToolMatcher abstract base class."""

    @patch("identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher.TaskToolValidator")
    def test_validate_input_calls_validator(self, mock_validator):
        """Test that _validate_input calls TaskToolValidator.run_common_validations."""
        matcher = ConcreteTaskToolMatcher()
        mock_input = Mock(spec=TaskToolMatchInput)

        matcher._validate_input(mock_input)

        mock_validator.run_common_validations.assert_called_once_with(mock_input)


class TestTaskToolMatcherFactory:
    """Tests for TaskToolMatcherFactory."""

    @pytest.mark.parametrize(
        "matcher_type,mock_path,mock_class",
        [
            (
                TaskToolMatcherType.RANDOM,
                "identity_auth_server.pipelines.task_tool_matcher.random.random.RandomTaskToolMatcher",
                "RandomTaskToolMatcher",
            ),
            (
                TaskToolMatcherType.EMBEDDINGS,
                "identity_auth_server.pipelines.task_tool_matcher.embeddings.embeddings.EmbeddingsTaskToolMatcher",
                "EmbeddingsTaskToolMatcher",
            ),
            (
                TaskToolMatcherType.HYBRID,
                "identity_auth_server.pipelines.task_tool_matcher.hybrid.hybrid.HybridTaskToolMatcher",
                "HybridTaskToolMatcher",
            ),
        ],
    )
    def test_create_matcher(self, matcher_type, mock_path, mock_class):
        """Test creating different types of matchers."""
        with patch(mock_path) as mock_matcher:
            mock_instance = Mock()
            mock_matcher.return_value = mock_instance

            result = TaskToolMatcherFactory.create(matcher_type)

            assert result == mock_instance
            mock_matcher.assert_called_once()

    def test_create_invalid_matcher_raises_error(self):
        """Test that invalid matcher type raises ValueError."""
        invalid_type = "INVALID_TYPE"

        with pytest.raises(ValueError, match=f"Unsupported task tool matcher type: {invalid_type}"):
            TaskToolMatcherFactory.create(invalid_type)
