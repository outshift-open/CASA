"""Tests for identity_auth_server.pipelines.task_tool_matcher.types module."""

import pytest
from mcp import types as mcp_types
from pydantic import ValidationError

from identity_auth_server.pipelines.task_tool_matcher.types import (
    TaskToolMatcherType,
    TaskToolMatchInput,
    TaskToolMatchOutput,
    TaskToolMatchReason,
)


class TestTaskToolMatcherType:
    """Tests for TaskToolMatcherType enum."""

    def test_enum_values(self):
        """Test that TaskToolMatcherType has correct enum values."""
        assert TaskToolMatcherType.RANDOM == "random"

    def test_enum_inheritance(self):
        """Test that TaskToolMatcherType inherits from str and Enum."""
        assert isinstance(TaskToolMatcherType.RANDOM, str)
        assert issubclass(TaskToolMatcherType, str)

    def test_string_comparison(self):
        """Test that enum values can be compared with strings."""
        assert TaskToolMatcherType.RANDOM == "random"
        assert TaskToolMatcherType.RANDOM != "other"

    def test_enum_iteration(self):
        """Test that enum can be iterated."""
        values = list(TaskToolMatcherType)
        assert len(values) == 3
        assert TaskToolMatcherType.RANDOM in values
        assert TaskToolMatcherType.EMBEDDINGS in values
        assert TaskToolMatcherType.HYBRID in values

    def test_enum_membership(self):
        """Test enum membership checks."""
        assert "random" in [item.value for item in TaskToolMatcherType]
        assert "embeddings" in [item.value for item in TaskToolMatcherType]

    def test_enum_repr(self):
        """Test enum string representation."""
        assert TaskToolMatcherType.RANDOM.value == "random"
        assert str(TaskToolMatcherType.RANDOM) == "TaskToolMatcherType.RANDOM"
        assert repr(TaskToolMatcherType.RANDOM).startswith("<TaskToolMatcherType")


class TestTaskToolMatchReason:
    """Tests for TaskToolMatchReason enum."""

    def test_enum_values(self):
        """Test that TaskToolMatchReason has correct enum values."""
        assert TaskToolMatchReason.TOOL_NOT_AVAILABLE == "tool_not_available"
        assert TaskToolMatchReason.TASK_EMPTY == "task_empty"
        assert TaskToolMatchReason.NO_AVAILABLE_TOOLS == "no_available_tools"
        assert TaskToolMatchReason.RANDOM_NO_MATCH == "Random matcher decided this tool doesn't match the task"

    def test_enum_inheritance(self):
        """Test that TaskToolMatchReason inherits from str and Enum."""
        for reason in TaskToolMatchReason:
            assert isinstance(reason, str)
        assert issubclass(TaskToolMatchReason, str)

    def test_validation_error_reasons(self):
        """Test validation error reason constants."""
        validation_reasons = [
            TaskToolMatchReason.TOOL_NOT_AVAILABLE,
            TaskToolMatchReason.TASK_EMPTY,
            TaskToolMatchReason.NO_AVAILABLE_TOOLS,
        ]

        for reason in validation_reasons:
            assert isinstance(reason, str)
            assert len(reason) > 0

    def test_matcher_specific_reasons(self):
        """Test matcher-specific reason constants."""
        matcher_reasons = [
            TaskToolMatchReason.RANDOM_NO_MATCH,
        ]

        for reason in matcher_reasons:
            assert isinstance(reason, str)
            assert len(reason) > 0

    def test_enum_iteration(self):
        """Test that enum can be iterated."""
        values = list(TaskToolMatchReason)
        assert len(values) == 6
        assert TaskToolMatchReason.TOOL_NOT_AVAILABLE in values
        assert TaskToolMatchReason.TASK_EMPTY in values
        assert TaskToolMatchReason.NO_AVAILABLE_TOOLS in values
        assert TaskToolMatchReason.RANDOM_NO_MATCH in values
        assert TaskToolMatchReason.EMBEDDINGS_NO_MATCH in values
        assert TaskToolMatchReason.HYBRID_NO_MATCH in values

    def test_string_comparison(self):
        """Test that enum values can be compared with strings."""
        assert TaskToolMatchReason.TOOL_NOT_AVAILABLE == "tool_not_available"
        assert TaskToolMatchReason.RANDOM_NO_MATCH == "Random matcher decided this tool doesn't match the task"

    def test_reason_descriptions_are_meaningful(self):
        """Test that reason descriptions are meaningful and descriptive."""
        # Validation error reasons should be concise identifiers
        assert TaskToolMatchReason.TOOL_NOT_AVAILABLE.replace("_", " ").lower() == "tool not available"
        assert TaskToolMatchReason.TASK_EMPTY.replace("_", " ").lower() == "task empty"
        assert TaskToolMatchReason.NO_AVAILABLE_TOOLS.replace("_", " ").lower() == "no available tools"

        # Matcher-specific reasons should be descriptive sentences
        assert len(TaskToolMatchReason.RANDOM_NO_MATCH) > 20
        assert "matcher" in TaskToolMatchReason.RANDOM_NO_MATCH.lower()


class TestTaskToolMatchInput:
    """Tests for TaskToolMatchInput Pydantic model."""

    @pytest.fixture
    def sample_mcp_tool(self):
        """Fixture for sample MCP tool."""
        return mcp_types.Tool(
            name="test_tool",
            description="A test tool for unit testing",
            inputSchema={
                "type": "object",
                "properties": {"param": {"type": "string", "description": "Test parameter"}},
                "required": ["param"],
            },
        )

    @pytest.fixture
    def valid_input_data(self, sample_mcp_tool):
        """Fixture for valid input data."""
        return {
            "task": "Process user input",
            "requested_tool": "test_tool",
            "available_tools": ["test_tool", "other_tool"],
            "mcp_tools": [sample_mcp_tool],
        }

    def test_valid_model_creation(self, valid_input_data):
        """Test creating TaskToolMatchInput with valid data."""
        input_model = TaskToolMatchInput(**valid_input_data)

        assert input_model.task == "Process user input"
        assert input_model.requested_tool == "test_tool"
        assert input_model.available_tools == ["test_tool", "other_tool"]
        assert len(input_model.mcp_tools) == 1
        assert input_model.mcp_tools[0].name == "test_tool"

    def test_model_validation_with_empty_task(self, valid_input_data):
        """Test model validation with empty task."""
        valid_input_data["task"] = ""
        # Note: The model itself doesn't validate empty strings, this is done in validators
        input_model = TaskToolMatchInput(**valid_input_data)
        assert input_model.task == ""

    def test_model_validation_with_empty_tools_list(self, valid_input_data):
        """Test model validation with empty available tools list."""
        valid_input_data["available_tools"] = []
        input_model = TaskToolMatchInput(**valid_input_data)
        assert input_model.available_tools == []

    def test_model_validation_with_empty_mcp_tools(self, valid_input_data):
        """Test model validation with empty MCP tools list."""
        valid_input_data["mcp_tools"] = []
        input_model = TaskToolMatchInput(**valid_input_data)
        assert input_model.mcp_tools == []

    def test_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        # Test missing task
        with pytest.raises(ValidationError) as exc_info:
            TaskToolMatchInput(requested_tool="test_tool", available_tools=["test_tool"], mcp_tools=[])
        assert "task" in str(exc_info.value)

        # Test missing requested_tool
        with pytest.raises(ValidationError) as exc_info:
            TaskToolMatchInput(task="test task", available_tools=["test_tool"], mcp_tools=[])
        assert "requested_tool" in str(exc_info.value)

        # Test missing available_tools
        with pytest.raises(ValidationError) as exc_info:
            TaskToolMatchInput(task="test task", requested_tool="test_tool", mcp_tools=[])
        assert "available_tools" in str(exc_info.value)

        # Test missing mcp_tools
        with pytest.raises(ValidationError) as exc_info:
            TaskToolMatchInput(task="test task", requested_tool="test_tool", available_tools=["test_tool"])
        assert "mcp_tools" in str(exc_info.value)

    def test_field_types(self, valid_input_data):
        """Test that fields have correct types."""
        input_model = TaskToolMatchInput(**valid_input_data)

        assert isinstance(input_model.task, str)
        assert isinstance(input_model.requested_tool, str)
        assert isinstance(input_model.available_tools, list)
        assert isinstance(input_model.mcp_tools, list)
        assert all(isinstance(tool, str) for tool in input_model.available_tools)
        assert all(isinstance(tool, mcp_types.Tool) for tool in input_model.mcp_tools)

    def test_model_serialization(self, valid_input_data):
        """Test model can be serialized to dict."""
        input_model = TaskToolMatchInput(**valid_input_data)
        model_dict = input_model.model_dump()

        assert "task" in model_dict
        assert "requested_tool" in model_dict
        assert "available_tools" in model_dict
        assert "mcp_tools" in model_dict
        assert model_dict["task"] == "Process user input"
        assert model_dict["requested_tool"] == "test_tool"

    def test_model_with_multiple_mcp_tools(self, sample_mcp_tool):
        """Test model with multiple MCP tools."""
        tool2 = mcp_types.Tool(
            name="second_tool", description="Another test tool", inputSchema={"type": "object", "properties": {}}
        )

        input_model = TaskToolMatchInput(
            task="Multi-tool task",
            requested_tool="test_tool",
            available_tools=["test_tool", "second_tool"],
            mcp_tools=[sample_mcp_tool, tool2],
        )

        assert len(input_model.mcp_tools) == 2
        assert input_model.mcp_tools[0].name == "test_tool"
        assert input_model.mcp_tools[1].name == "second_tool"

    def test_model_with_special_characters(self, sample_mcp_tool):
        """Test model with special characters in strings."""
        input_model = TaskToolMatchInput(
            task="Task with special chars: !@#$%^&*()",
            requested_tool="tool_with-special.chars",
            available_tools=["tool_with-special.chars", "another-tool_name"],
            mcp_tools=[sample_mcp_tool],
        )

        assert "!@#$%^&*()" in input_model.task
        assert "-" in input_model.requested_tool
        assert "." in input_model.requested_tool

    def test_model_immutability_after_creation(self, valid_input_data):
        """Test that model fields can be accessed but model is designed for immutability."""
        input_model = TaskToolMatchInput(**valid_input_data)

        # Test that we can access fields
        assert input_model.task == "Process user input"
        assert len(input_model.available_tools) == 2

        # Test that the model has the expected structure
        assert hasattr(input_model, "task")
        assert hasattr(input_model, "requested_tool")
        assert hasattr(input_model, "available_tools")
        assert hasattr(input_model, "mcp_tools")


class TestTaskToolMatchOutput:
    """Tests for TaskToolMatchOutput Pydantic model."""

    def test_valid_model_creation_with_match_true(self):
        """Test creating TaskToolMatchOutput with successful match."""
        output_model = TaskToolMatchOutput(task_tool_match=True)

        assert output_model.task_tool_match is True
        assert output_model.reason is None

    def test_valid_model_creation_with_match_false(self):
        """Test creating TaskToolMatchOutput with failed match."""
        output_model = TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.TOOL_NOT_AVAILABLE)

        assert output_model.task_tool_match is False
        assert output_model.reason == TaskToolMatchReason.TOOL_NOT_AVAILABLE

    def test_model_creation_with_explicit_none_reason(self):
        """Test creating model with explicit None reason."""
        output_model = TaskToolMatchOutput(task_tool_match=True, reason=None)

        assert output_model.task_tool_match is True
        assert output_model.reason is None

    def test_model_creation_without_reason(self):
        """Test creating model without providing reason (should default to None)."""
        output_model = TaskToolMatchOutput(task_tool_match=False)

        assert output_model.task_tool_match is False
        assert output_model.reason is None

    def test_all_reason_enum_values(self):
        """Test model with all possible reason enum values."""
        reasons = [
            TaskToolMatchReason.TOOL_NOT_AVAILABLE,
            TaskToolMatchReason.TASK_EMPTY,
            TaskToolMatchReason.NO_AVAILABLE_TOOLS,
            TaskToolMatchReason.RANDOM_NO_MATCH,
        ]

        for reason in reasons:
            output_model = TaskToolMatchOutput(task_tool_match=False, reason=reason)
            assert output_model.reason == reason

    def test_missing_required_field(self):
        """Test validation error when required field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            TaskToolMatchOutput()

        assert "task_tool_match" in str(exc_info.value)

    def test_field_types(self):
        """Test that fields have correct types."""
        output_model = TaskToolMatchOutput(task_tool_match=True, reason=TaskToolMatchReason.RANDOM_NO_MATCH)

        assert isinstance(output_model.task_tool_match, bool)
        assert isinstance(output_model.reason, (TaskToolMatchReason, type(None)))

    def test_model_serialization_with_reason(self):
        """Test model serialization with reason."""
        output_model = TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.TOOL_NOT_AVAILABLE)
        model_dict = output_model.model_dump()

        assert "task_tool_match" in model_dict
        assert "reason" in model_dict
        assert model_dict["task_tool_match"] is False
        assert model_dict["reason"] == "tool_not_available"

    def test_model_serialization_without_reason(self):
        """Test model serialization without reason."""
        output_model = TaskToolMatchOutput(task_tool_match=True)
        model_dict = output_model.model_dump()

        assert "task_tool_match" in model_dict
        assert "reason" in model_dict
        assert model_dict["task_tool_match"] is True
        assert model_dict["reason"] is None

    def test_boolean_validation(self):
        """Test that task_tool_match properly validates boolean values."""
        # Test with actual boolean values
        true_model = TaskToolMatchOutput(task_tool_match=True)
        false_model = TaskToolMatchOutput(task_tool_match=False)

        assert true_model.task_tool_match is True
        assert false_model.task_tool_match is False

    def test_reason_optional_type_annotation(self):
        """Test that reason field properly handles Optional type."""
        # Test with None
        output_none = TaskToolMatchOutput(task_tool_match=True, reason=None)
        assert output_none.reason is None

        # Test with actual reason
        output_with_reason = TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.TASK_EMPTY)
        assert output_with_reason.reason == TaskToolMatchReason.TASK_EMPTY

    def test_model_equality(self):
        """Test model equality comparison."""
        model1 = TaskToolMatchOutput(task_tool_match=True, reason=None)
        model2 = TaskToolMatchOutput(task_tool_match=True, reason=None)
        model3 = TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.TASK_EMPTY)

        assert model1 == model2
        assert model1 != model3

    def test_model_repr_and_str(self):
        """Test model string representations."""
        output_model = TaskToolMatchOutput(task_tool_match=True, reason=TaskToolMatchReason.RANDOM_NO_MATCH)

        repr_str = repr(output_model)

        assert "TaskToolMatchOutput" in repr_str
        assert "task_tool_match" in repr_str
        assert "reason" in repr_str


class TestTypeIntegration:
    """Tests for integration between different types."""

    def test_input_and_output_types_work_together(self):
        """Test that input and output types can be used together."""
        # Create input
        mcp_tool = mcp_types.Tool(
            name="integration_tool",
            description="Integration test tool",
            inputSchema={"type": "object", "properties": {}},
        )

        input_model = TaskToolMatchInput(
            task="Integration test task",
            requested_tool="integration_tool",
            available_tools=["integration_tool"],
            mcp_tools=[mcp_tool],
        )

        # Create output (simulating successful processing)
        output_model = TaskToolMatchOutput(task_tool_match=True)

        # Verify they work together
        assert input_model.requested_tool == "integration_tool"
        assert output_model.task_tool_match is True
        assert output_model.reason is None

    def test_enum_types_in_model_context(self):
        """Test enum types work correctly within model context."""
        # Test TaskToolMatcherType usage
        matcher_type = TaskToolMatcherType.RANDOM
        assert isinstance(matcher_type, str)
        assert matcher_type == "random"

        # Test TaskToolMatchReason usage in output
        output_model = TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.NO_AVAILABLE_TOOLS)
        assert output_model.reason.value == "no_available_tools"

    def test_serialization_roundtrip(self):
        """Test that models can be serialized and deserialized."""
        # Test TaskToolMatchOutput roundtrip
        output_original = TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.RANDOM_NO_MATCH)

        output_dict = output_original.model_dump()
        output_reconstructed = TaskToolMatchOutput(**output_dict)

        assert output_reconstructed == output_original
        assert output_reconstructed.task_tool_match == output_original.task_tool_match
        assert output_reconstructed.reason == output_original.reason
