"""Tests for identity_auth_server.pipelines.task_tool_matcher.random.random module."""

import hashlib
import random

import pytest
from mcp import types as mcp_types

from identity_auth_server.pipelines.exceptions import PipelineValidationError
from identity_auth_server.pipelines.task_tool_matcher.random.random import RandomTaskToolMatcher
from identity_auth_server.pipelines.task_tool_matcher.types import (
    TaskToolMatchInput,
    TaskToolMatchOutput,
    TaskToolMatchReason,
)


class TestRandomTaskToolMatcherInitialization:
    """Tests for RandomTaskToolMatcher initialization."""

    def test_default_initialization(self):
        """Test RandomTaskToolMatcher initializes with default probability."""
        matcher = RandomTaskToolMatcher()

        assert matcher.match_probability == 0.5
        assert isinstance(matcher, RandomTaskToolMatcher)

    def test_custom_probability_initialization(self):
        """Test RandomTaskToolMatcher initializes with custom probability."""
        test_probabilities = [0.0, 0.25, 0.5, 0.75, 1.0]

        for prob in test_probabilities:
            matcher = RandomTaskToolMatcher(match_probability=prob)
            assert matcher.match_probability == prob

    def test_invalid_probability_too_low(self):
        """Test initialization fails with probability below 0.0."""
        invalid_probabilities = [-0.1, -1.0, -0.001]

        for prob in invalid_probabilities:
            with pytest.raises(ValueError) as exc_info:
                RandomTaskToolMatcher(match_probability=prob)

            assert "match_probability must be between 0.0 and 1.0" in str(exc_info.value)

    def test_invalid_probability_too_high(self):
        """Test initialization fails with probability above 1.0."""
        invalid_probabilities = [1.1, 2.0, 1.001]

        for prob in invalid_probabilities:
            with pytest.raises(ValueError) as exc_info:
                RandomTaskToolMatcher(match_probability=prob)

            assert "match_probability must be between 0.0 and 1.0" in str(exc_info.value)

    def test_boundary_probabilities(self):
        """Test initialization with exact boundary values."""
        # Should work exactly at boundaries
        matcher_zero = RandomTaskToolMatcher(match_probability=0.0)
        matcher_one = RandomTaskToolMatcher(match_probability=1.0)

        assert matcher_zero.match_probability == 0.0
        assert matcher_one.match_probability == 1.0

    def test_floating_point_precision(self):
        """Test initialization handles floating point precision correctly."""
        precise_prob = 0.123456789
        matcher = RandomTaskToolMatcher(match_probability=precise_prob)

        assert matcher.match_probability == precise_prob


class TestRandomTaskToolMatcherMatch:
    """Tests for RandomTaskToolMatcher match method."""

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
            task="Analyze user data for patterns and insights",
            requested_tool="analyzer",
            available_tools=["analyzer", "processor"],
            mcp_tools=sample_mcp_tools,
        )

    def test_match_returns_valid_output(self, valid_input):
        """Test that match method returns valid TaskToolMatchOutput."""
        matcher = RandomTaskToolMatcher()
        result = matcher.match(valid_input)

        assert isinstance(result, TaskToolMatchOutput)
        assert isinstance(result.task_tool_match, bool)

        # If match is False, should have RANDOM_NO_MATCH reason
        if not result.task_tool_match:
            assert result.reason == TaskToolMatchReason.RANDOM_NO_MATCH
        else:
            assert result.reason is None

    def test_deterministic_behavior(self, valid_input):
        """Test that same input produces same result (deterministic randomness)."""
        matcher1 = RandomTaskToolMatcher(match_probability=0.5)
        matcher2 = RandomTaskToolMatcher(match_probability=0.5)

        # Same input should produce same results across different instances
        result1 = matcher1.match(valid_input)
        result2 = matcher2.match(valid_input)

        assert result1.task_tool_match == result2.task_tool_match
        assert result1.reason == result2.reason

        # Multiple calls on same instance should also be consistent
        result3 = matcher1.match(valid_input)
        assert result1.task_tool_match == result3.task_tool_match
        assert result1.reason == result3.reason

    def test_probability_zero_always_returns_false(self, valid_input):
        """Test that probability 0.0 always returns False."""
        matcher = RandomTaskToolMatcher(match_probability=0.0)

        # Test multiple times to ensure consistency
        for _ in range(10):
            result = matcher.match(valid_input)
            assert result.task_tool_match is False
            assert result.reason == TaskToolMatchReason.RANDOM_NO_MATCH

    def test_probability_one_always_returns_true(self, valid_input):
        """Test that probability 1.0 always returns True."""
        matcher = RandomTaskToolMatcher(match_probability=1.0)

        # Test multiple times to ensure consistency
        for _ in range(10):
            result = matcher.match(valid_input)
            assert result.task_tool_match is True
            assert result.reason is None

    def test_different_inputs_produce_different_results(self, sample_mcp_tools):
        """Test that different inputs can produce different results."""
        matcher = RandomTaskToolMatcher(match_probability=0.5)

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
                task="Transform user input completely different task",
                requested_tool="analyzer",
                available_tools=["analyzer", "processor"],
                mcp_tools=sample_mcp_tools,
            ),
        ]

        results = [matcher.match(input_data) for input_data in inputs]

        # Each result should be valid
        for result in results:
            assert isinstance(result, TaskToolMatchOutput)
            assert isinstance(result.task_tool_match, bool)

    def test_input_validation_is_called(self, sample_mcp_tools):
        """Test that input validation is called and errors propagated."""
        matcher = RandomTaskToolMatcher()

        # Create invalid input (empty task)
        invalid_input = TaskToolMatchInput(
            task="",  # Empty task will fail validation
            requested_tool="analyzer",
            available_tools=["analyzer"],
            mcp_tools=sample_mcp_tools,
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            matcher.match(invalid_input)

        assert "Task description cannot be empty" in str(exc_info.value)

    def test_various_validation_errors_propagated(self, sample_mcp_tools):
        """Test that various validation errors are properly propagated."""
        matcher = RandomTaskToolMatcher()

        validation_test_cases = [
            # Empty task
            (
                TaskToolMatchInput(
                    task="", requested_tool="analyzer", available_tools=["analyzer"], mcp_tools=sample_mcp_tools
                ),
                "Task description cannot be empty",
            ),
            # Empty available tools
            (
                TaskToolMatchInput(
                    task="Valid task", requested_tool="analyzer", available_tools=[], mcp_tools=sample_mcp_tools
                ),
                "No available tools provided",
            ),
            # Tool not available
            (
                TaskToolMatchInput(
                    task="Valid task",
                    requested_tool="nonexistent_tool",
                    available_tools=["analyzer"],
                    mcp_tools=sample_mcp_tools,
                ),
                "Requested tool is not available in the provided tools list",
            ),
            # Available tools not subset of MCP tools
            (
                TaskToolMatchInput(
                    task="Valid task",
                    requested_tool="extra_tool",
                    available_tools=["extra_tool"],
                    mcp_tools=sample_mcp_tools,
                ),
                "Available tools must be a subset of the provided MCP tools",
            ),
        ]

        for invalid_input, expected_error in validation_test_cases:
            with pytest.raises(PipelineValidationError) as exc_info:
                matcher.match(invalid_input)

            assert expected_error in str(exc_info.value)


class TestRandomTaskToolMatcherSeedGeneration:
    """Tests for seed generation and deterministic randomness."""

    @pytest.fixture
    def sample_mcp_tool(self):
        """Fixture for single MCP tool."""
        return mcp_types.Tool(
            name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}}
        )

    def test_seed_generation_consistency(self, sample_mcp_tool):
        """Test that same input generates same seed."""
        input_data = TaskToolMatchInput(
            task="Test task", requested_tool="test_tool", available_tools=["test_tool"], mcp_tools=[sample_mcp_tool]
        )

        # Manually create the expected seed string
        expected_seed_string = f"{input_data.task}|{input_data.requested_tool}|{','.join(input_data.available_tools)}"
        expected_hash = hashlib.sha256(expected_seed_string.encode("utf-8")).hexdigest()
        expected_seed = int(expected_hash[:8], 16)

        # Create a Random instance with the expected seed
        test_random = random.Random(expected_seed)

        # Test with probability 0.5
        matcher = RandomTaskToolMatcher(match_probability=0.5)
        result = matcher.match(input_data)

        # The result should match what we expect from the deterministic seed
        expected_match = test_random.random() < 0.5
        assert result.task_tool_match == expected_match

    def test_different_tasks_generate_different_seeds(self, sample_mcp_tool):
        """Test that different tasks generate different seeds and potentially different results."""
        base_input = {"requested_tool": "test_tool", "available_tools": ["test_tool"], "mcp_tools": [sample_mcp_tool]}

        tasks = ["Analyze data", "Process information", "Transform input", "Generate report"]

        results = []
        for task in tasks:
            input_data = TaskToolMatchInput(task=task, **base_input)
            matcher = RandomTaskToolMatcher(match_probability=0.5)
            result = matcher.match(input_data)
            results.append(result.task_tool_match)

        # Results should be deterministic for each specific task
        # Verify by running again
        for i, task in enumerate(tasks):
            input_data = TaskToolMatchInput(task=task, **base_input)
            matcher = RandomTaskToolMatcher(match_probability=0.5)
            result = matcher.match(input_data)
            assert result.task_tool_match == results[i]

    def test_different_tools_generate_different_seeds(self, sample_mcp_tool):
        """Test that different requested tools generate different seeds."""
        # Create additional MCP tool
        tool2 = mcp_types.Tool(
            name="second_tool", description="Second test tool", inputSchema={"type": "object", "properties": {}}
        )

        tools_configs = [
            {"requested_tool": "test_tool", "available_tools": ["test_tool"], "mcp_tools": [sample_mcp_tool]},
            {"requested_tool": "second_tool", "available_tools": ["second_tool"], "mcp_tools": [tool2]},
        ]

        results = []
        for config in tools_configs:
            input_data = TaskToolMatchInput(task="Same task", **config)
            matcher = RandomTaskToolMatcher(match_probability=0.5)
            result = matcher.match(input_data)
            results.append(result.task_tool_match)

        # Each should be deterministic for its specific configuration
        for i, config in enumerate(tools_configs):
            input_data = TaskToolMatchInput(task="Same task", **config)
            matcher = RandomTaskToolMatcher(match_probability=0.5)
            result = matcher.match(input_data)
            assert result.task_tool_match == results[i]

    def test_different_available_tools_generate_different_seeds(self, sample_mcp_tool):
        """Test that different available tools lists generate different seeds."""
        # Create additional MCP tools
        tools = [
            sample_mcp_tool,
            mcp_types.Tool(name="tool2", description="Tool 2", inputSchema={"type": "object", "properties": {}}),
            mcp_types.Tool(name="tool3", description="Tool 3", inputSchema={"type": "object", "properties": {}}),
        ]

        available_tools_configs = [["test_tool"], ["test_tool", "tool2"], ["test_tool", "tool2", "tool3"]]

        results = []
        for available_tools in available_tools_configs:
            input_data = TaskToolMatchInput(
                task="Same task", requested_tool="test_tool", available_tools=available_tools, mcp_tools=tools
            )
            matcher = RandomTaskToolMatcher(match_probability=0.5)
            result = matcher.match(input_data)
            results.append(result.task_tool_match)

        # Each should be deterministic for its specific configuration
        for i, available_tools in enumerate(available_tools_configs):
            input_data = TaskToolMatchInput(
                task="Same task", requested_tool="test_tool", available_tools=available_tools, mcp_tools=tools
            )
            matcher = RandomTaskToolMatcher(match_probability=0.5)
            result = matcher.match(input_data)
            assert result.task_tool_match == results[i]


class TestRandomTaskToolMatcherProbabilityDistribution:
    """Tests for probability distribution behavior."""

    @pytest.fixture
    def sample_inputs(self):
        """Fixture for multiple different inputs to test probability distribution."""
        mcp_tool = mcp_types.Tool(
            name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}}
        )

        # Generate many different inputs to test probability distribution
        inputs = []
        for i in range(100):  # Create 100 different inputs
            inputs.append(
                TaskToolMatchInput(
                    task=f"Task number {i} with unique content",
                    requested_tool="test_tool",
                    available_tools=["test_tool"],
                    mcp_tools=[mcp_tool],
                )
            )

        return inputs

    def test_probability_distribution_with_half_probability(self, sample_inputs):
        """Test that probability 0.5 produces roughly balanced results over many inputs."""
        matcher = RandomTaskToolMatcher(match_probability=0.5)

        results = [matcher.match(input_data) for input_data in sample_inputs]
        true_count = sum(1 for result in results if result.task_tool_match)
        false_count = len(results) - true_count

        # With 100 samples and 0.5 probability, we expect roughly 50/50 split
        # Allow for reasonable variance (e.g., 30-70 range)
        assert 30 <= true_count <= 70, f"Expected roughly balanced results, got {true_count} true, {false_count} false"

    def test_probability_distribution_with_low_probability(self, sample_inputs):
        """Test that low probability produces mostly false results."""
        matcher = RandomTaskToolMatcher(match_probability=0.1)

        results = [matcher.match(input_data) for input_data in sample_inputs]
        true_count = sum(1 for result in results if result.task_tool_match)

        # With 0.1 probability and 100 samples, expect around 10 true results
        # Allow for reasonable variance (e.g., 0-25 range)
        assert 0 <= true_count <= 25, f"Expected mostly false results, got {true_count} true out of {len(results)}"

    def test_probability_distribution_with_high_probability(self, sample_inputs):
        """Test that high probability produces mostly true results."""
        matcher = RandomTaskToolMatcher(match_probability=0.9)

        results = [matcher.match(input_data) for input_data in sample_inputs]
        true_count = sum(1 for result in results if result.task_tool_match)

        # With 0.9 probability and 100 samples, expect around 90 true results
        # Allow for reasonable variance (e.g., 75-100 range)
        assert 75 <= true_count <= 100, f"Expected mostly true results, got {true_count} true out of {len(results)}"


class TestRandomTaskToolMatcherInheritance:
    """Tests for inheritance from TaskToolMatcher base class."""

    @pytest.fixture
    def valid_input(self):
        """Fixture for valid input."""
        mcp_tool = mcp_types.Tool(
            name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}}
        )
        return TaskToolMatchInput(
            task="Test task", requested_tool="test_tool", available_tools=["test_tool"], mcp_tools=[mcp_tool]
        )

    def test_inherits_from_task_tool_matcher(self):
        """Test that RandomTaskToolMatcher inherits from TaskToolMatcher."""
        from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import TaskToolMatcher

        matcher = RandomTaskToolMatcher()
        assert isinstance(matcher, TaskToolMatcher)

    def test_implements_abstract_match_method(self, valid_input):
        """Test that RandomTaskToolMatcher implements the abstract match method."""
        matcher = RandomTaskToolMatcher()

        # Should not raise NotImplementedError
        result = matcher.match(valid_input)
        assert isinstance(result, TaskToolMatchOutput)

    def test_uses_inherited_validate_input_method(self, valid_input):
        """Test that RandomTaskToolMatcher uses inherited _validate_input method."""
        matcher = RandomTaskToolMatcher()

        # This should work without error (validation passes)
        result = matcher.match(valid_input)
        assert isinstance(result, TaskToolMatchOutput)

        # Create invalid input to test validation is called
        invalid_input = TaskToolMatchInput(
            task="",  # Empty task
            requested_tool="test_tool",
            available_tools=["test_tool"],
            mcp_tools=valid_input.mcp_tools,
        )

        with pytest.raises(PipelineValidationError):
            matcher.match(invalid_input)


class TestRandomTaskToolMatcherEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_unicode_task_description(self):
        """Test matcher handles Unicode characters in task description."""
        mcp_tool = mcp_types.Tool(
            name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}}
        )

        unicode_input = TaskToolMatchInput(
            task="Analyze data with émojis 🚀 and special chars: αβγδε",
            requested_tool="test_tool",
            available_tools=["test_tool"],
            mcp_tools=[mcp_tool],
        )

        matcher = RandomTaskToolMatcher()
        result = matcher.match(unicode_input)

        assert isinstance(result, TaskToolMatchOutput)
        assert isinstance(result.task_tool_match, bool)

    def test_very_long_task_description(self):
        """Test matcher handles very long task descriptions."""
        mcp_tool = mcp_types.Tool(
            name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}}
        )

        long_task = "Very long task description " * 1000  # Very long string
        long_input = TaskToolMatchInput(
            task=long_task, requested_tool="test_tool", available_tools=["test_tool"], mcp_tools=[mcp_tool]
        )

        matcher = RandomTaskToolMatcher()
        result = matcher.match(long_input)

        assert isinstance(result, TaskToolMatchOutput)
        assert isinstance(result.task_tool_match, bool)

    def test_many_available_tools(self):
        """Test matcher handles many available tools."""
        # Create many MCP tools
        mcp_tools = []
        available_tools = []
        for i in range(100):
            tool_name = f"tool_{i}"
            mcp_tools.append(
                mcp_types.Tool(
                    name=tool_name, description=f"Tool {i}", inputSchema={"type": "object", "properties": {}}
                )
            )
            available_tools.append(tool_name)

        many_tools_input = TaskToolMatchInput(
            task="Task with many tools", requested_tool="tool_0", available_tools=available_tools, mcp_tools=mcp_tools
        )

        matcher = RandomTaskToolMatcher()
        result = matcher.match(many_tools_input)

        assert isinstance(result, TaskToolMatchOutput)
        assert isinstance(result.task_tool_match, bool)

    def test_special_characters_in_tool_names(self):
        """Test matcher handles special characters in tool names."""
        mcp_tool = mcp_types.Tool(
            name="tool-with_special.chars@domain",
            description="Tool with special characters",
            inputSchema={"type": "object", "properties": {}},
        )

        special_input = TaskToolMatchInput(
            task="Task with special tool name",
            requested_tool="tool-with_special.chars@domain",
            available_tools=["tool-with_special.chars@domain"],
            mcp_tools=[mcp_tool],
        )

        matcher = RandomTaskToolMatcher()
        result = matcher.match(special_input)

        assert isinstance(result, TaskToolMatchOutput)
        assert isinstance(result.task_tool_match, bool)

    def test_multiline_task_description(self):
        """Test matcher handles multiline task descriptions."""
        mcp_tool = mcp_types.Tool(
            name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}}
        )

        multiline_input = TaskToolMatchInput(
            task="Line 1 of task\nLine 2 of task\nLine 3 of task\nWith multiple lines",
            requested_tool="test_tool",
            available_tools=["test_tool"],
            mcp_tools=[mcp_tool],
        )

        matcher = RandomTaskToolMatcher()
        result = matcher.match(multiline_input)

        assert isinstance(result, TaskToolMatchOutput)
        assert isinstance(result.task_tool_match, bool)
