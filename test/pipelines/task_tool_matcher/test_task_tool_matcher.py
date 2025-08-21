"""Tests for identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher module."""

from unittest.mock import patch

import pytest
from mcp import types as mcp_types

from identity_auth_server.pipelines.exceptions import PipelineValidationError
from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import (
    TaskToolMatcher,
    TaskToolMatcherFactory,
)
from identity_auth_server.pipelines.task_tool_matcher.types import (
    TaskToolMatcherType,
    TaskToolMatchInput,
    TaskToolMatchOutput,
    TaskToolMatchReason,
)


class TestTaskToolMatcher:
    """Tests for TaskToolMatcher abstract base class."""

    def test_is_abstract_base_class(self):
        """Test that TaskToolMatcher is an abstract base class."""
        from abc import ABC

        assert issubclass(TaskToolMatcher, ABC)

        # Should not be able to instantiate abstract class
        with pytest.raises(TypeError):
            TaskToolMatcher()

    def test_has_abstract_match_method(self):
        """Test that TaskToolMatcher has abstract match method."""

        # Create a concrete subclass that doesn't implement match
        class IncompleteTaskToolMatcher(TaskToolMatcher):
            pass

        # Should not be able to instantiate class without implementing match
        with pytest.raises(TypeError) as exc_info:
            IncompleteTaskToolMatcher()

        assert "match" in str(exc_info.value)

    def test_validate_input_method_exists(self):
        """Test that TaskToolMatcher has _validate_input method."""
        assert hasattr(TaskToolMatcher, "_validate_input")

    @pytest.fixture
    def concrete_matcher(self):
        """Fixture for concrete TaskToolMatcher implementation."""

        class ConcreteTaskToolMatcher(TaskToolMatcher):
            def match(self, input: TaskToolMatchInput) -> TaskToolMatchOutput:
                return TaskToolMatchOutput(task_tool_match=True)

        return ConcreteTaskToolMatcher()

    @pytest.fixture
    def valid_input(self):
        """Fixture for valid TaskToolMatchInput."""
        mcp_tool = mcp_types.Tool(
            name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}}
        )
        return TaskToolMatchInput(
            task="Test task", requested_tool="test_tool", available_tools=["test_tool"], mcp_tools=[mcp_tool]
        )

    def test_validate_input_calls_validator(self, concrete_matcher, valid_input):
        """Test that _validate_input calls TaskToolValidator.run_common_validations."""
        with patch(
            "identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher.TaskToolValidator.run_common_validations"
        ) as mock_validate:
            concrete_matcher._validate_input(valid_input)
            mock_validate.assert_called_once_with(valid_input)

    def test_validate_input_propagates_validation_error(self, concrete_matcher, valid_input):
        """Test that _validate_input propagates PipelineValidationError."""
        with patch(
            "identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher.TaskToolValidator.run_common_validations"
        ) as mock_validate:
            mock_validate.side_effect = PipelineValidationError("Test validation error")

            with pytest.raises(PipelineValidationError) as exc_info:
                concrete_matcher._validate_input(valid_input)

            assert str(exc_info.value) == "Test validation error"


class TestTaskToolMatcherFactory:
    """Tests for TaskToolMatcherFactory class."""

    def test_factory_class_exists(self):
        """Test that TaskToolMatcherFactory class exists."""
        assert TaskToolMatcherFactory is not None

    def test_create_method_is_static(self):
        """Test that create method is static."""
        import inspect

        assert inspect.isfunction(TaskToolMatcherFactory.create)

    def test_create_random_matcher(self):
        """Test creating a random matcher."""
        matcher = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)

        assert matcher is not None
        assert isinstance(matcher, TaskToolMatcher)

        # Test that it's specifically a RandomTaskToolMatcher
        from identity_auth_server.pipelines.task_tool_matcher.random.random import RandomTaskToolMatcher

        assert isinstance(matcher, RandomTaskToolMatcher)

    def test_create_unsupported_matcher_type(self):
        """Test creating unsupported matcher type raises ValueError."""
        # Create a fake matcher type
        fake_type = "unsupported_type"

        with pytest.raises(ValueError) as exc_info:
            TaskToolMatcherFactory.create(fake_type)

        assert "Unsupported task tool matcher type" in str(exc_info.value)
        assert fake_type in str(exc_info.value)

    def test_create_with_none_type(self):
        """Test creating matcher with None type."""
        with pytest.raises(ValueError):
            TaskToolMatcherFactory.create(None)

    def test_factory_returns_different_instances(self):
        """Test that factory returns different instances on multiple calls."""
        matcher1 = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)
        matcher2 = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)

        assert matcher1 is not matcher2
        assert type(matcher1) == type(matcher2)

    def test_lazy_import_pattern(self):
        """Test that factory uses lazy import pattern."""
        # This test verifies that the import happens inside the create method
        # rather than at module level, which is the lazy import pattern

        # First, verify the RandomTaskToolMatcher is not imported at module level
        import identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher as ttm_module

        # The RandomTaskToolMatcher should not be available at module level
        assert not hasattr(ttm_module, "RandomTaskToolMatcher")

        # But the factory should still be able to create it
        matcher = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)
        assert matcher is not None

        # This confirms the lazy import pattern is working


class TestTaskToolMatcherIntegration:
    """Integration tests for TaskToolMatcher with actual RandomTaskToolMatcher."""

    @pytest.fixture
    def sample_mcp_tools(self):
        """Fixture for sample MCP tools."""
        return [
            mcp_types.Tool(
                name="analyzer",
                description="Analyzer tool",
                inputSchema={
                    "type": "object",
                    "properties": {"data": {"type": "string", "description": "Data to analyze"}},
                    "required": ["data"],
                },
            ),
            mcp_types.Tool(
                name="processor",
                description="Processor tool",
                inputSchema={
                    "type": "object",
                    "properties": {"input": {"type": "string", "description": "Input to process"}},
                    "required": ["input"],
                },
            ),
        ]

    @pytest.fixture
    def valid_input(self, sample_mcp_tools):
        """Fixture for valid TaskToolMatchInput."""
        return TaskToolMatchInput(
            task="Analyze user data for insights",
            requested_tool="analyzer",
            available_tools=["analyzer", "processor"],
            mcp_tools=sample_mcp_tools,
        )

    def test_random_matcher_integration_success(self, valid_input):
        """Test successful integration with RandomTaskToolMatcher."""
        matcher = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)
        result = matcher.match(valid_input)

        assert isinstance(result, TaskToolMatchOutput)
        assert isinstance(result.task_tool_match, bool)

        # If match is False, should have a reason
        if not result.task_tool_match:
            assert result.reason == TaskToolMatchReason.RANDOM_NO_MATCH
        else:
            assert result.reason is None

    def test_random_matcher_deterministic_behavior(self, valid_input):
        """Test that RandomTaskToolMatcher produces deterministic results."""
        matcher1 = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)
        matcher2 = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)

        result1 = matcher1.match(valid_input)
        result2 = matcher2.match(valid_input)

        # Results should be identical for same input (deterministic randomness)
        assert result1.task_tool_match == result2.task_tool_match
        assert result1.reason == result2.reason

    def test_random_matcher_validation_failure(self, sample_mcp_tools):
        """Test that RandomTaskToolMatcher properly handles validation failures."""
        # Create input that will fail validation (empty task)
        invalid_input = TaskToolMatchInput(
            task="",  # Empty task will fail validation
            requested_tool="analyzer",
            available_tools=["analyzer"],
            mcp_tools=sample_mcp_tools,
        )

        matcher = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)

        with pytest.raises(PipelineValidationError) as exc_info:
            matcher.match(invalid_input)

        assert "Task description cannot be empty" in str(exc_info.value)

    def test_random_matcher_with_different_inputs(self, sample_mcp_tools):
        """Test RandomTaskToolMatcher with different inputs."""
        matcher = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)

        inputs = [
            TaskToolMatchInput(
                task="Analyze customer feedback",
                requested_tool="analyzer",
                available_tools=["analyzer"],
                mcp_tools=[sample_mcp_tools[0]],
            ),
            TaskToolMatchInput(
                task="Process transaction data",
                requested_tool="processor",
                available_tools=["processor"],
                mcp_tools=[sample_mcp_tools[1]],
            ),
            TaskToolMatchInput(
                task="Transform user input",
                requested_tool="analyzer",
                available_tools=["analyzer", "processor"],
                mcp_tools=sample_mcp_tools,
            ),
        ]

        results = []
        for input_data in inputs:
            result = matcher.match(input_data)
            results.append(result)

            # Each result should be valid
            assert isinstance(result, TaskToolMatchOutput)
            assert isinstance(result.task_tool_match, bool)

        # Results should be consistent for same inputs when called again
        for i, input_data in enumerate(inputs):
            repeat_result = matcher.match(input_data)
            assert repeat_result.task_tool_match == results[i].task_tool_match
            assert repeat_result.reason == results[i].reason

    def test_match_method_signature_compliance(self, valid_input):
        """Test that RandomTaskToolMatcher match method has correct signature."""
        matcher = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)

        # Should accept TaskToolMatchInput and return TaskToolMatchOutput
        result = matcher.match(valid_input)

        assert isinstance(result, TaskToolMatchOutput)

        # Test method signature using inspect
        import inspect

        sig = inspect.signature(matcher.match)
        params = list(sig.parameters.keys())

        assert "input" in params
        assert sig.return_annotation == TaskToolMatchOutput or sig.return_annotation == "TaskToolMatchOutput"


class TestTaskToolMatcherErrorHandling:
    """Tests for error handling in TaskToolMatcher implementations."""

    @pytest.fixture
    def invalid_inputs(self):
        """Fixture for various invalid inputs."""
        mcp_tool = mcp_types.Tool(
            name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}}
        )

        return [
            # Empty task
            TaskToolMatchInput(
                task="", requested_tool="test_tool", available_tools=["test_tool"], mcp_tools=[mcp_tool]
            ),
            # Empty available tools
            TaskToolMatchInput(task="Valid task", requested_tool="test_tool", available_tools=[], mcp_tools=[mcp_tool]),
            # Tool not available
            TaskToolMatchInput(
                task="Valid task",
                requested_tool="nonexistent_tool",
                available_tools=["test_tool"],
                mcp_tools=[mcp_tool],
            ),
            # Available tools not subset of MCP tools
            TaskToolMatchInput(
                task="Valid task", requested_tool="extra_tool", available_tools=["extra_tool"], mcp_tools=[mcp_tool]
            ),
        ]

    def test_validation_errors_propagated(self, invalid_inputs):
        """Test that validation errors are properly propagated."""
        matcher = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)

        for invalid_input in invalid_inputs:
            with pytest.raises(PipelineValidationError):
                matcher.match(invalid_input)

    def test_specific_validation_error_messages(self):
        """Test specific validation error messages."""
        matcher = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)
        mcp_tool = mcp_types.Tool(
            name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}}
        )

        # Test empty task error
        empty_task_input = TaskToolMatchInput(
            task="", requested_tool="test_tool", available_tools=["test_tool"], mcp_tools=[mcp_tool]
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            matcher.match(empty_task_input)

        assert "Task description cannot be empty" in str(exc_info.value)

    def test_error_handling_does_not_affect_valid_inputs(self, invalid_inputs):
        """Test that error handling doesn't affect processing of valid inputs."""
        matcher = TaskToolMatcherFactory.create(TaskToolMatcherType.RANDOM)

        # First try invalid inputs
        for invalid_input in invalid_inputs:
            with pytest.raises(PipelineValidationError):
                matcher.match(invalid_input)

        # Then try valid input - should work fine
        mcp_tool = mcp_types.Tool(
            name="valid_tool", description="Valid tool", inputSchema={"type": "object", "properties": {}}
        )

        valid_input = TaskToolMatchInput(
            task="Valid task description",
            requested_tool="valid_tool",
            available_tools=["valid_tool"],
            mcp_tools=[mcp_tool],
        )

        # Should not raise exception
        result = matcher.match(valid_input)
        assert isinstance(result, TaskToolMatchOutput)


class TestTaskToolMatcherDocumentation:
    """Tests for documentation and interface compliance."""

    def test_abstract_class_has_docstring(self):
        """Test that TaskToolMatcher has proper docstring."""
        assert TaskToolMatcher.__doc__ is not None
        assert len(TaskToolMatcher.__doc__.strip()) > 0
        assert "Abstract base class" in TaskToolMatcher.__doc__

    def test_match_method_has_docstring(self):
        """Test that match method has proper docstring."""
        # Get the abstract method directly
        match_method = getattr(TaskToolMatcher, "match")
        assert match_method.__doc__ is not None
        assert len(match_method.__doc__.strip()) > 0
        assert "Args:" in match_method.__doc__
        assert "Returns:" in match_method.__doc__

    def test_validate_input_has_docstring(self):
        """Test that _validate_input method has proper docstring."""
        validate_method = getattr(TaskToolMatcher, "_validate_input")
        assert validate_method.__doc__ is not None
        assert len(validate_method.__doc__.strip()) > 0
        assert "Args:" in validate_method.__doc__
        assert "Raises:" in validate_method.__doc__

    def test_factory_class_has_docstring(self):
        """Test that TaskToolMatcherFactory has proper docstring."""
        assert TaskToolMatcherFactory.__doc__ is not None
        assert len(TaskToolMatcherFactory.__doc__.strip()) > 0
        assert "Factory" in TaskToolMatcherFactory.__doc__

    def test_factory_create_method_has_docstring(self):
        """Test that factory create method has proper docstring."""
        create_method = getattr(TaskToolMatcherFactory, "create")
        # Access the docstring directly from the function
        assert create_method.__doc__ is not None
        assert len(create_method.__doc__.strip()) > 0
        assert "Args:" in create_method.__doc__
        assert "Returns:" in create_method.__doc__
        assert "Raises:" in create_method.__doc__


class TestTaskToolMatcherExtensibility:
    """Tests for extensibility and future matcher types."""

    def test_factory_extensible_for_new_matcher_types(self):
        """Test that factory can be extended for new matcher types."""
        # This test verifies the pattern supports extension
        # by testing the error message suggests adding new types

        fake_type = "future_matcher_type"

        with pytest.raises(ValueError) as exc_info:
            TaskToolMatcherFactory.create(fake_type)

        error_msg = str(exc_info.value)
        assert "Unsupported task tool matcher type" in error_msg
        assert fake_type in error_msg

    def test_abstract_interface_supports_extension(self):
        """Test that abstract interface supports extension with new matchers."""

        # Create a custom matcher implementation
        class CustomTaskToolMatcher(TaskToolMatcher):
            def match(self, input: TaskToolMatchInput) -> TaskToolMatchOutput:
                # Custom logic - always returns True
                self._validate_input(input)  # Use parent validation
                return TaskToolMatchOutput(task_tool_match=True)

        # Should be able to instantiate custom matcher
        custom_matcher = CustomTaskToolMatcher()
        assert isinstance(custom_matcher, TaskToolMatcher)

        # Should be able to use custom matcher
        mcp_tool = mcp_types.Tool(
            name="custom_tool", description="Custom tool", inputSchema={"type": "object", "properties": {}}
        )

        input_data = TaskToolMatchInput(
            task="Custom task", requested_tool="custom_tool", available_tools=["custom_tool"], mcp_tools=[mcp_tool]
        )

        result = custom_matcher.match(input_data)
        assert isinstance(result, TaskToolMatchOutput)
        assert result.task_tool_match is True

    def test_validation_inheritance_works(self):
        """Test that custom matchers inherit validation behavior."""

        class ValidationTestMatcher(TaskToolMatcher):
            def match(self, input: TaskToolMatchInput) -> TaskToolMatchOutput:
                self._validate_input(input)  # Should trigger validation
                return TaskToolMatchOutput(task_tool_match=True)

        matcher = ValidationTestMatcher()

        # Test with invalid input - should raise validation error
        mcp_tool = mcp_types.Tool(
            name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}}
        )

        invalid_input = TaskToolMatchInput(
            task="",  # Empty task
            requested_tool="test_tool",
            available_tools=["test_tool"],
            mcp_tools=[mcp_tool],
        )

        with pytest.raises(PipelineValidationError):
            matcher.match(invalid_input)
