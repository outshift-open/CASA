"""Tests for identity_auth_server.types module."""

from mcp import types as mcp_types

from identity_auth_server.types import (
    AvailableTools,
    McpBadge,
    McpTools,
    Task,
    ToolName,
)


class TestTypeAliases:
    """Test type aliases defined in types.py."""

    def test_task_type_alias(self):
        """Test Task type alias is equivalent to str."""
        # Test that Task accepts string values
        task: Task = "example task description"
        assert isinstance(task, str)
        assert task == "example task description"

        # Test empty string
        empty_task: Task = ""
        assert isinstance(empty_task, str)
        assert empty_task == ""

        # Test multiline string
        multiline_task: Task = "line 1\nline 2"
        assert isinstance(multiline_task, str)
        assert "\n" in multiline_task

    def test_tool_name_type_alias(self):
        """Test ToolName type alias is equivalent to str."""
        # Test that ToolName accepts string values
        tool_name: ToolName = "example_tool"
        assert isinstance(tool_name, str)
        assert tool_name == "example_tool"

        # Test with special characters
        special_tool_name: ToolName = "tool-with_special.chars"
        assert isinstance(special_tool_name, str)
        assert special_tool_name == "tool-with_special.chars"

    def test_mcp_badge_type_alias(self):
        """Test McpBadge type alias is equivalent to str."""
        # Test that McpBadge accepts string values
        badge: McpBadge = "identity_badge_token"
        assert isinstance(badge, str)
        assert badge == "identity_badge_token"

        # Test with JSON-like string (common for badges)
        json_badge: McpBadge = '{"tools": ["tool1", "tool2"]}'
        assert isinstance(json_badge, str)
        assert json_badge.startswith("{")

    def test_available_tools_type_alias(self):
        """Test AvailableTools type alias is equivalent to List[ToolName]."""
        # Test empty list
        empty_tools: AvailableTools = []
        assert isinstance(empty_tools, list)
        assert len(empty_tools) == 0

        # Test list with tool names
        tools: AvailableTools = ["tool1", "tool2", "tool3"]
        assert isinstance(tools, list)
        assert len(tools) == 3
        assert all(isinstance(tool, str) for tool in tools)
        assert "tool1" in tools

        # Test list operations
        tools.append("tool4")
        assert len(tools) == 4
        assert tools[-1] == "tool4"

    def test_mcp_tools_type_alias(self):
        """Test McpTools type alias is equivalent to List[mcp_types.Tool]."""
        # Test empty list
        empty_mcp_tools: McpTools = []
        assert isinstance(empty_mcp_tools, list)
        assert len(empty_mcp_tools) == 0

        # Test with mock MCP tool objects
        mock_tool = mcp_types.Tool(
            name="test_tool",
            description="A test tool",
            inputSchema={"type": "object", "properties": {"param": {"type": "string"}}},
        )

        mcp_tools: McpTools = [mock_tool]
        assert isinstance(mcp_tools, list)
        assert len(mcp_tools) == 1
        assert isinstance(mcp_tools[0], mcp_types.Tool)
        assert mcp_tools[0].name == "test_tool"
        assert mcp_tools[0].description == "A test tool"


class TestTypeUsage:
    """Test practical usage of the type aliases."""

    def test_task_assignment_and_usage(self):
        """Test Task type can be used in typical scenarios."""

        def process_task(task: Task) -> str:
            return f"Processing: {task}"

        result = process_task("analyze user input")
        assert result == "Processing: analyze user input"

    def test_tool_name_in_collections(self):
        """Test ToolName type works in collections."""
        tool_names: AvailableTools = ["file_reader", "web_scraper", "calculator"]

        def find_tool(tools: AvailableTools, name: ToolName) -> bool:
            return name in tools

        assert find_tool(tool_names, "file_reader") is True
        assert find_tool(tool_names, "nonexistent") is False

    def test_badge_validation(self):
        """Test McpBadge type in validation scenarios."""

        def validate_badge(badge: McpBadge) -> bool:
            return isinstance(badge, str) and len(badge) > 0

        valid_badge: McpBadge = "valid_badge_123"
        invalid_badge: McpBadge = ""

        assert validate_badge(valid_badge) is True
        assert validate_badge(invalid_badge) is False

    def test_tools_list_manipulation(self):
        """Test AvailableTools list operations."""
        tools: AvailableTools = ["tool1", "tool2"]

        # Test addition
        tools.extend(["tool3", "tool4"])
        assert len(tools) == 4

        # Test removal
        tools.remove("tool2")
        assert "tool2" not in tools
        assert len(tools) == 3

        # Test filtering
        filtered_tools = [tool for tool in tools if tool.startswith("tool")]
        assert len(filtered_tools) == 3

    def test_mcp_tools_operations(self):
        """Test McpTools list operations with actual MCP Tool objects."""
        # Create multiple tools
        tool1 = mcp_types.Tool(
            name="search", description="Search tool", inputSchema={"type": "object", "properties": {}}
        )
        tool2 = mcp_types.Tool(
            name="analyze", description="Analysis tool", inputSchema={"type": "object", "properties": {}}
        )

        mcp_tools: McpTools = [tool1, tool2]

        # Test finding tools by name
        search_tool = next((tool for tool in mcp_tools if tool.name == "search"), None)
        assert search_tool is not None
        assert search_tool.description == "Search tool"

        # Test adding tools
        tool3 = mcp_types.Tool(
            name="process", description="Processing tool", inputSchema={"type": "object", "properties": {}}
        )
        mcp_tools.append(tool3)
        assert len(mcp_tools) == 3

        # Test tool names extraction
        tool_names = [tool.name for tool in mcp_tools]
        assert "search" in tool_names
        assert "analyze" in tool_names
        assert "process" in tool_names


class TestTypeCompatibility:
    """Test type compatibility and interoperability."""

    def test_string_compatibility(self):
        """Test that string type aliases are compatible with str operations."""
        task: Task = "example task"
        tool_name: ToolName = "example_tool"
        badge: McpBadge = "example_badge"

        # Test string methods work
        assert task.upper() == "EXAMPLE TASK"
        assert tool_name.replace("_", "-") == "example-tool"
        assert badge.startswith("example")

        # Test string concatenation
        combined = f"{task} using {tool_name} with {badge}"
        assert "example task using example_tool with example_badge" == combined

    def test_list_compatibility(self):
        """Test that list type aliases are compatible with list operations."""
        available_tools: AvailableTools = ["tool1", "tool2"]

        # Test list methods
        available_tools.sort()
        assert available_tools == ["tool1", "tool2"]

        available_tools.reverse()
        assert available_tools == ["tool2", "tool1"]

        # Test list comprehensions
        upper_tools = [tool.upper() for tool in available_tools]
        assert upper_tools == ["TOOL2", "TOOL1"]

    def test_type_annotations_work(self):
        """Test that type annotations work correctly with the aliases."""

        def process_request(task: Task, available_tools: AvailableTools, badge: McpBadge) -> dict:
            return {"task": task, "tool_count": len(available_tools), "badge_length": len(badge)}

        result = process_request(task="test task", available_tools=["tool1", "tool2"], badge="test_badge")

        assert result["task"] == "test task"
        assert result["tool_count"] == 2
        assert result["badge_length"] == 10
