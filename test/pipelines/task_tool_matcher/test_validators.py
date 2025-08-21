"""Tests for identity_auth_server.pipelines.task_tool_matcher.validators module."""

import pytest
from mcp import types as mcp_types

from identity_auth_server.pipelines.exceptions import PipelineValidationError
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchInput
from identity_auth_server.pipelines.task_tool_matcher.validators import TaskToolValidator


class TestTaskToolValidator:
    """Tests for TaskToolValidator class."""

    @pytest.fixture
    def sample_mcp_tools(self):
        """Fixture for sample MCP tools."""
        return [
            mcp_types.Tool(
                name="text_analyzer",
                description="Analyzes text content",
                inputSchema={
                    "type": "object",
                    "properties": {"text": {"type": "string", "description": "Text to analyze"}},
                    "required": ["text"],
                },
            ),
            mcp_types.Tool(
                name="file_reader",
                description="Reads file content",
                inputSchema={
                    "type": "object",
                    "properties": {"path": {"type": "string", "description": "File path"}},
                    "required": ["path"],
                },
            ),
            mcp_types.Tool(
                name="web_scraper",
                description="Scrapes web content",
                inputSchema={
                    "type": "object",
                    "properties": {"url": {"type": "string", "description": "URL to scrape"}},
                    "required": ["url"],
                },
            ),
        ]

    @pytest.fixture
    def valid_input(self, sample_mcp_tools):
        """Fixture for valid TaskToolMatchInput."""
        return TaskToolMatchInput(
            task="Analyze user feedback from the latest survey",
            requested_tool="text_analyzer",
            available_tools=["text_analyzer", "file_reader"],
            mcp_tools=sample_mcp_tools,
        )

    def test_validator_class_exists(self):
        """Test that TaskToolValidator class exists and is properly structured."""
        assert TaskToolValidator is not None
        assert hasattr(TaskToolValidator, "validate_tool_availability")
        assert hasattr(TaskToolValidator, "validate_task_not_empty")
        assert hasattr(TaskToolValidator, "validate_available_tools_not_empty")
        assert hasattr(TaskToolValidator, "validate_available_tools_subset_mcp_tools")
        assert hasattr(TaskToolValidator, "run_common_validations")

    def test_validator_methods_are_static(self):
        """Test that validator methods are static methods."""
        # Test that methods can be called without instantiating the class
        # This is the practical test for static methods
        import inspect

        assert inspect.isfunction(TaskToolValidator.validate_tool_availability)
        assert inspect.isfunction(TaskToolValidator.validate_task_not_empty)
        assert inspect.isfunction(TaskToolValidator.validate_available_tools_not_empty)
        assert inspect.isfunction(TaskToolValidator.validate_available_tools_subset_mcp_tools)

        # Test that run_common_validations is a class method (uses cls)
        assert inspect.ismethod(TaskToolValidator.run_common_validations)


class TestValidateToolAvailability:
    """Tests for validate_tool_availability method."""

    @pytest.fixture
    def sample_mcp_tools(self):
        """Fixture for sample MCP tools."""
        return [
            mcp_types.Tool(name="tool1", description="First tool", inputSchema={"type": "object", "properties": {}}),
            mcp_types.Tool(name="tool2", description="Second tool", inputSchema={"type": "object", "properties": {}}),
        ]

    def test_valid_tool_availability(self, sample_mcp_tools):
        """Test validation passes when requested tool is in available tools."""
        input_data = TaskToolMatchInput(
            task="Test task", requested_tool="tool1", available_tools=["tool1", "tool2"], mcp_tools=sample_mcp_tools
        )

        # Should not raise any exception
        TaskToolValidator.validate_tool_availability(input_data)

    def test_invalid_tool_availability(self, sample_mcp_tools):
        """Test validation fails when requested tool is not in available tools."""
        input_data = TaskToolMatchInput(
            task="Test task",
            requested_tool="nonexistent_tool",
            available_tools=["tool1", "tool2"],
            mcp_tools=sample_mcp_tools,
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.validate_tool_availability(input_data)

        assert "Requested tool is not available in the provided tools list" in str(exc_info.value)
        assert exc_info.value.message == "Requested tool is not available in the provided tools list"

    def test_empty_available_tools_list(self, sample_mcp_tools):
        """Test validation fails when available tools list is empty."""
        input_data = TaskToolMatchInput(
            task="Test task", requested_tool="tool1", available_tools=[], mcp_tools=sample_mcp_tools
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.validate_tool_availability(input_data)

        assert "Requested tool is not available in the provided tools list" in str(exc_info.value)

    def test_case_sensitive_tool_matching(self, sample_mcp_tools):
        """Test that tool matching is case sensitive."""
        input_data = TaskToolMatchInput(
            task="Test task",
            requested_tool="Tool1",  # Different case
            available_tools=["tool1", "tool2"],
            mcp_tools=sample_mcp_tools,
        )

        with pytest.raises(PipelineValidationError):
            TaskToolValidator.validate_tool_availability(input_data)

    def test_single_tool_in_available_tools(self, sample_mcp_tools):
        """Test validation with single tool in available tools."""
        input_data = TaskToolMatchInput(
            task="Test task", requested_tool="tool1", available_tools=["tool1"], mcp_tools=sample_mcp_tools
        )

        # Should not raise any exception
        TaskToolValidator.validate_tool_availability(input_data)

    def test_multiple_matching_tools(self, sample_mcp_tools):
        """Test validation when requested tool appears multiple times in available tools."""
        input_data = TaskToolMatchInput(
            task="Test task",
            requested_tool="tool1",
            available_tools=["tool1", "tool2", "tool1", "tool3"],  # Duplicate tool1
            mcp_tools=sample_mcp_tools,
        )

        # Should not raise any exception - duplicates should not affect validation
        TaskToolValidator.validate_tool_availability(input_data)


class TestValidateTaskNotEmpty:
    """Tests for validate_task_not_empty method."""

    @pytest.fixture
    def sample_mcp_tools(self):
        """Fixture for sample MCP tools."""
        return [
            mcp_types.Tool(name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}})
        ]

    def test_valid_task_description(self, sample_mcp_tools):
        """Test validation passes with valid task description."""
        input_data = TaskToolMatchInput(
            task="Analyze the user data for patterns",
            requested_tool="test_tool",
            available_tools=["test_tool"],
            mcp_tools=sample_mcp_tools,
        )

        # Should not raise any exception
        TaskToolValidator.validate_task_not_empty(input_data)

    def test_empty_string_task(self, sample_mcp_tools):
        """Test validation fails with empty string task."""
        input_data = TaskToolMatchInput(
            task="", requested_tool="test_tool", available_tools=["test_tool"], mcp_tools=sample_mcp_tools
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.validate_task_not_empty(input_data)

        assert "Task description cannot be empty" in str(exc_info.value)
        assert exc_info.value.message == "Task description cannot be empty"

    def test_whitespace_only_task(self, sample_mcp_tools):
        """Test validation fails with whitespace-only task."""
        input_data = TaskToolMatchInput(
            task="   \t  \n  ",  # Only whitespace
            requested_tool="test_tool",
            available_tools=["test_tool"],
            mcp_tools=sample_mcp_tools,
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.validate_task_not_empty(input_data)

        assert "Task description cannot be empty" in str(exc_info.value)

    def test_task_with_leading_trailing_whitespace(self, sample_mcp_tools):
        """Test validation passes with task having leading/trailing whitespace."""
        input_data = TaskToolMatchInput(
            task="  Process the data  ",  # Valid content with whitespace
            requested_tool="test_tool",
            available_tools=["test_tool"],
            mcp_tools=sample_mcp_tools,
        )

        # Should not raise any exception
        TaskToolValidator.validate_task_not_empty(input_data)

    def test_single_character_task(self, sample_mcp_tools):
        """Test validation passes with single character task."""
        input_data = TaskToolMatchInput(
            task="a", requested_tool="test_tool", available_tools=["test_tool"], mcp_tools=sample_mcp_tools
        )

        # Should not raise any exception
        TaskToolValidator.validate_task_not_empty(input_data)

    def test_multiline_task(self, sample_mcp_tools):
        """Test validation passes with multiline task."""
        input_data = TaskToolMatchInput(
            task="Process the data\nand generate a report\nwith detailed analysis",
            requested_tool="test_tool",
            available_tools=["test_tool"],
            mcp_tools=sample_mcp_tools,
        )

        # Should not raise any exception
        TaskToolValidator.validate_task_not_empty(input_data)


class TestValidateAvailableToolsNotEmpty:
    """Tests for validate_available_tools_not_empty method."""

    @pytest.fixture
    def sample_mcp_tools(self):
        """Fixture for sample MCP tools."""
        return [
            mcp_types.Tool(name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}})
        ]

    def test_valid_available_tools(self, sample_mcp_tools):
        """Test validation passes with non-empty available tools."""
        input_data = TaskToolMatchInput(
            task="Test task",
            requested_tool="test_tool",
            available_tools=["test_tool", "other_tool"],
            mcp_tools=sample_mcp_tools,
        )

        # Should not raise any exception
        TaskToolValidator.validate_available_tools_not_empty(input_data)

    def test_empty_available_tools(self, sample_mcp_tools):
        """Test validation fails with empty available tools list."""
        input_data = TaskToolMatchInput(
            task="Test task", requested_tool="test_tool", available_tools=[], mcp_tools=sample_mcp_tools
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.validate_available_tools_not_empty(input_data)

        assert "No available tools provided" in str(exc_info.value)
        assert exc_info.value.message == "No available tools provided"

    def test_single_available_tool(self, sample_mcp_tools):
        """Test validation passes with single available tool."""
        input_data = TaskToolMatchInput(
            task="Test task", requested_tool="test_tool", available_tools=["test_tool"], mcp_tools=sample_mcp_tools
        )

        # Should not raise any exception
        TaskToolValidator.validate_available_tools_not_empty(input_data)

    def test_multiple_available_tools(self, sample_mcp_tools):
        """Test validation passes with multiple available tools."""
        input_data = TaskToolMatchInput(
            task="Test task",
            requested_tool="test_tool",
            available_tools=["tool1", "tool2", "tool3", "test_tool"],
            mcp_tools=sample_mcp_tools,
        )

        # Should not raise any exception
        TaskToolValidator.validate_available_tools_not_empty(input_data)


class TestValidateAvailableToolsSubsetMcpTools:
    """Tests for validate_available_tools_subset_mcp_tools method."""

    @pytest.fixture
    def sample_mcp_tools(self):
        """Fixture for sample MCP tools."""
        return [
            mcp_types.Tool(
                name="analyzer", description="Analyzer tool", inputSchema={"type": "object", "properties": {}}
            ),
            mcp_types.Tool(
                name="processor", description="Processor tool", inputSchema={"type": "object", "properties": {}}
            ),
            mcp_types.Tool(
                name="formatter", description="Formatter tool", inputSchema={"type": "object", "properties": {}}
            ),
        ]

    def test_valid_subset(self, sample_mcp_tools):
        """Test validation passes when available tools are subset of MCP tools."""
        input_data = TaskToolMatchInput(
            task="Test task",
            requested_tool="analyzer",
            available_tools=["analyzer", "processor"],
            mcp_tools=sample_mcp_tools,
        )

        # Should not raise any exception
        TaskToolValidator.validate_available_tools_subset_mcp_tools(input_data)

    def test_exact_match_all_tools(self, sample_mcp_tools):
        """Test validation passes when available tools exactly match all MCP tools."""
        input_data = TaskToolMatchInput(
            task="Test task",
            requested_tool="analyzer",
            available_tools=["analyzer", "processor", "formatter"],
            mcp_tools=sample_mcp_tools,
        )

        # Should not raise any exception
        TaskToolValidator.validate_available_tools_subset_mcp_tools(input_data)

    def test_single_tool_subset(self, sample_mcp_tools):
        """Test validation passes with single tool subset."""
        input_data = TaskToolMatchInput(
            task="Test task", requested_tool="analyzer", available_tools=["analyzer"], mcp_tools=sample_mcp_tools
        )

        # Should not raise any exception
        TaskToolValidator.validate_available_tools_subset_mcp_tools(input_data)

    def test_invalid_subset_extra_tool(self, sample_mcp_tools):
        """Test validation fails when available tools contain tool not in MCP tools."""
        input_data = TaskToolMatchInput(
            task="Test task",
            requested_tool="analyzer",
            available_tools=["analyzer", "processor", "nonexistent_tool"],
            mcp_tools=sample_mcp_tools,
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.validate_available_tools_subset_mcp_tools(input_data)

        assert "Available tools must be a subset of the provided MCP tools" in str(exc_info.value)
        assert exc_info.value.message == "Available tools must be a subset of the provided MCP tools"

    def test_empty_mcp_tools_with_available_tools(self):
        """Test validation fails when MCP tools is empty but available tools is not."""
        input_data = TaskToolMatchInput(
            task="Test task", requested_tool="analyzer", available_tools=["analyzer"], mcp_tools=[]
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.validate_available_tools_subset_mcp_tools(input_data)

        assert "Available tools must be a subset of the provided MCP tools" in str(exc_info.value)

    def test_empty_both_lists(self):
        """Test validation passes when both available tools and MCP tools are empty."""
        input_data = TaskToolMatchInput(task="Test task", requested_tool="analyzer", available_tools=[], mcp_tools=[])

        # Should not raise any exception - empty set is subset of empty set
        TaskToolValidator.validate_available_tools_subset_mcp_tools(input_data)

    def test_case_sensitive_tool_names(self):
        """Test validation is case sensitive for tool names."""
        mcp_tools = [
            mcp_types.Tool(
                name="Analyzer",  # Capital A
                description="Analyzer tool",
                inputSchema={"type": "object", "properties": {}},
            )
        ]

        input_data = TaskToolMatchInput(
            task="Test task",
            requested_tool="analyzer",
            available_tools=["analyzer"],  # lowercase a
            mcp_tools=mcp_tools,
        )

        with pytest.raises(PipelineValidationError):
            TaskToolValidator.validate_available_tools_subset_mcp_tools(input_data)

    def test_duplicate_tools_in_available_tools(self, sample_mcp_tools):
        """Test validation handles duplicate tools in available tools."""
        input_data = TaskToolMatchInput(
            task="Test task",
            requested_tool="analyzer",
            available_tools=["analyzer", "processor", "analyzer"],  # Duplicate analyzer
            mcp_tools=sample_mcp_tools,
        )

        # Should not raise any exception - duplicates should not affect subset validation
        TaskToolValidator.validate_available_tools_subset_mcp_tools(input_data)


class TestRunCommonValidations:
    """Tests for run_common_validations method."""

    @pytest.fixture
    def sample_mcp_tools(self):
        """Fixture for sample MCP tools."""
        return [
            mcp_types.Tool(
                name="valid_tool", description="Valid tool", inputSchema={"type": "object", "properties": {}}
            ),
            mcp_types.Tool(
                name="another_tool", description="Another tool", inputSchema={"type": "object", "properties": {}}
            ),
        ]

    def test_all_validations_pass(self, sample_mcp_tools):
        """Test that run_common_validations passes when all individual validations pass."""
        input_data = TaskToolMatchInput(
            task="Process the user data",
            requested_tool="valid_tool",
            available_tools=["valid_tool", "another_tool"],
            mcp_tools=sample_mcp_tools,
        )

        # Should not raise any exception
        TaskToolValidator.run_common_validations(input_data)

    def test_fails_on_empty_task(self, sample_mcp_tools):
        """Test that run_common_validations fails on empty task."""
        input_data = TaskToolMatchInput(
            task="", requested_tool="valid_tool", available_tools=["valid_tool"], mcp_tools=sample_mcp_tools
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.run_common_validations(input_data)

        assert "Task description cannot be empty" in str(exc_info.value)

    def test_fails_on_empty_available_tools(self, sample_mcp_tools):
        """Test that run_common_validations fails on empty available tools."""
        input_data = TaskToolMatchInput(
            task="Process the data", requested_tool="valid_tool", available_tools=[], mcp_tools=sample_mcp_tools
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.run_common_validations(input_data)

        assert "No available tools provided" in str(exc_info.value)

    def test_fails_on_tool_not_available(self, sample_mcp_tools):
        """Test that run_common_validations fails when requested tool is not available."""
        input_data = TaskToolMatchInput(
            task="Process the data",
            requested_tool="nonexistent_tool",
            available_tools=["valid_tool"],
            mcp_tools=sample_mcp_tools,
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.run_common_validations(input_data)

        assert "Requested tool is not available in the provided tools list" in str(exc_info.value)

    def test_fails_on_tools_not_subset(self, sample_mcp_tools):
        """Test that run_common_validations fails when available tools are not subset of MCP tools."""
        input_data = TaskToolMatchInput(
            task="Process the data",
            requested_tool="invalid_tool",
            available_tools=["invalid_tool"],
            mcp_tools=sample_mcp_tools,
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.run_common_validations(input_data)

        # Should fail on the first validation that doesn't pass
        # In this case, it will fail on available_tools_subset_mcp_tools before tool_availability
        assert "Available tools must be a subset of the provided MCP tools" in str(exc_info.value)

    def test_validation_order(self, sample_mcp_tools):
        """Test that validations are run in the expected order."""
        # Create input that will fail multiple validations
        input_data = TaskToolMatchInput(
            task="",  # Will fail task_not_empty
            requested_tool="nonexistent_tool",  # Will fail tool_availability
            available_tools=[],  # Will fail available_tools_not_empty
            mcp_tools=sample_mcp_tools,
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.run_common_validations(input_data)

        # Should fail on the first validation (task_not_empty)
        assert "Task description cannot be empty" in str(exc_info.value)

    def test_stops_on_first_failure(self, sample_mcp_tools):
        """Test that validation stops on first failure and doesn't continue."""
        input_data = TaskToolMatchInput(
            task="Valid task",
            requested_tool="nonexistent_tool",
            available_tools=["nonexistent_tool"],
            mcp_tools=sample_mcp_tools,
        )

        with pytest.raises(PipelineValidationError) as exc_info:
            TaskToolValidator.run_common_validations(input_data)

        # Should fail on available_tools_subset_mcp_tools (third in order)
        # before getting to tool_availability (fourth in order)
        assert "Available tools must be a subset of the provided MCP tools" in str(exc_info.value)

    def test_minimal_valid_input(self, sample_mcp_tools):
        """Test run_common_validations with minimal valid input."""
        input_data = TaskToolMatchInput(
            task="a",  # Minimal valid task
            requested_tool="valid_tool",
            available_tools=["valid_tool"],  # Minimal valid available tools
            mcp_tools=[sample_mcp_tools[0]],  # Single MCP tool
        )

        # Should not raise any exception
        TaskToolValidator.run_common_validations(input_data)


class TestValidatorIntegration:
    """Integration tests for validator methods working together."""

    @pytest.fixture
    def complex_mcp_tools(self):
        """Fixture for complex MCP tools setup."""
        return [
            mcp_types.Tool(
                name="data_analyzer",
                description="Analyzes various types of data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "Data to analyze"},
                        "format": {"type": "string", "enum": ["json", "csv", "xml"]},
                    },
                    "required": ["data"],
                },
            ),
            mcp_types.Tool(
                name="report_generator",
                description="Generates reports from processed data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "template": {"type": "string", "description": "Report template"},
                        "data": {"type": "object", "description": "Processed data"},
                    },
                    "required": ["template", "data"],
                },
            ),
            mcp_types.Tool(
                name="data_transformer",
                description="Transforms data between formats",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "input_format": {"type": "string"},
                        "output_format": {"type": "string"},
                        "data": {"type": "string"},
                    },
                    "required": ["input_format", "output_format", "data"],
                },
            ),
        ]

    def test_complex_valid_scenario(self, complex_mcp_tools):
        """Test complex valid scenario with multiple tools and validations."""
        input_data = TaskToolMatchInput(
            task="Analyze the customer survey data and generate a comprehensive report with insights",
            requested_tool="data_analyzer",
            available_tools=["data_analyzer", "report_generator"],
            mcp_tools=complex_mcp_tools,
        )

        # Test each validation individually
        TaskToolValidator.validate_task_not_empty(input_data)
        TaskToolValidator.validate_available_tools_not_empty(input_data)
        TaskToolValidator.validate_tool_availability(input_data)
        TaskToolValidator.validate_available_tools_subset_mcp_tools(input_data)

        # Test all validations together
        TaskToolValidator.run_common_validations(input_data)

    def test_realistic_edge_case_scenarios(self, complex_mcp_tools):
        """Test realistic edge case scenarios."""
        # Scenario 1: Tool available but not in MCP tools
        input_data1 = TaskToolMatchInput(
            task="Transform data format",
            requested_tool="legacy_transformer",
            available_tools=["legacy_transformer", "data_analyzer"],
            mcp_tools=complex_mcp_tools,
        )

        with pytest.raises(PipelineValidationError):
            TaskToolValidator.run_common_validations(input_data1)

        # Scenario 2: All tools are available and valid
        input_data2 = TaskToolMatchInput(
            task="Complete data processing pipeline",
            requested_tool="data_transformer",
            available_tools=["data_analyzer", "data_transformer", "report_generator"],
            mcp_tools=complex_mcp_tools,
        )

        # Should pass all validations
        TaskToolValidator.run_common_validations(input_data2)

    def test_validator_error_messages_are_descriptive(self):
        """Test that validator error messages are descriptive and helpful."""
        mcp_tools = [
            mcp_types.Tool(name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}})
        ]

        # Test each error message
        error_scenarios = [
            (
                TaskToolMatchInput(
                    task="", requested_tool="test_tool", available_tools=["test_tool"], mcp_tools=mcp_tools
                ),
                "Task description cannot be empty",
            ),
            (
                TaskToolMatchInput(
                    task="Valid task", requested_tool="test_tool", available_tools=[], mcp_tools=mcp_tools
                ),
                "No available tools provided",
            ),
            (
                TaskToolMatchInput(
                    task="Valid task", requested_tool="missing_tool", available_tools=["test_tool"], mcp_tools=mcp_tools
                ),
                "Requested tool is not available in the provided tools list",
            ),
            (
                TaskToolMatchInput(
                    task="Valid task", requested_tool="extra_tool", available_tools=["extra_tool"], mcp_tools=mcp_tools
                ),
                "Available tools must be a subset of the provided MCP tools",
            ),
        ]

        for input_data, expected_message in error_scenarios:
            with pytest.raises(PipelineValidationError) as exc_info:
                if expected_message == "Task description cannot be empty":
                    TaskToolValidator.validate_task_not_empty(input_data)
                elif expected_message == "No available tools provided":
                    TaskToolValidator.validate_available_tools_not_empty(input_data)
                elif expected_message == "Requested tool is not available in the provided tools list":
                    TaskToolValidator.validate_tool_availability(input_data)
                elif expected_message == "Available tools must be a subset of the provided MCP tools":
                    TaskToolValidator.validate_available_tools_subset_mcp_tools(input_data)

            assert expected_message in str(exc_info.value)
            assert exc_info.value.message == expected_message
