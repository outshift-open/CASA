"""API for Identity Auth Server."""

from fastapi import FastAPI, HTTPException

from identity_auth_server.api.types import (
    IntentMcpBadgeToolMatchRequest,
    IntentMcpBadgeToolMatchResult,
    IntentMcpToolMatchRequest,
    IntentMcpToolMatchResult,
)
from identity_auth_server.pipelines.exceptions import PipelineValidationError
from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import TaskToolMatcherFactory
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatcherType

app = FastAPI()


@app.post("/task/intent/mcp/badge/tool-match")
def task_intent_mcp_badge_tool_match(
    request: IntentMcpBadgeToolMatchRequest, task_tool_matcher: TaskToolMatcherType = TaskToolMatcherType.RANDOM
) -> IntentMcpBadgeToolMatchResult:
    """Endpoint to match tools based on MCP badge."""
    # TODO: Parse the MCP badge to extract tool objects
    # converted_tools = ?

    input = IntentMcpToolMatchRequest(
        task=request.task,
        requested_tool=request.requested_tool,
        available_tools=request.available_tools,
        mcp_tools=[],  # Placeholder for MCP tools, should be replaced with actual tool extraction logic
    )

    # Create the TaskToolMatcher using the factory
    matcher = TaskToolMatcherFactory.create(task_tool_matcher)

    try:
        # Get the result - validation exceptions will be caught and converted to HTTP 400
        result = matcher.match(input)
        return result
    except PipelineValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@app.post("/task/intent/mcp/tool-match")
def task_intent_mcp_tool_match(
    request: IntentMcpToolMatchRequest, task_tool_matcher: TaskToolMatcherType = TaskToolMatcherType.RANDOM
) -> IntentMcpToolMatchResult:
    """Endpoint to match tools based on MCP tool objects."""
    # Create the TaskToolMatcher using the factory
    matcher = TaskToolMatcherFactory.create(task_tool_matcher)

    try:
        # Get the result - validation exceptions will be caught and converted to HTTP 400
        result = matcher.match(input=request)
        return result
    except PipelineValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
