"""Type definitions for Evaluation - Task Tool Matcher."""

from enum import Enum
from typing import List, Union

from pydantic import BaseModel

from identity_auth_server.types import McpServer, Task, ToolName


class MatchTag(str, Enum):
    """Tags for evaluating task tool matching.

    - CORRECT: correct match
    - WRONG: wrong match, but the ground truth tool was part of the provided tools
    - NULL: wrong match, the ground truth was not part of the provided tools (it was part of another MCP Server)
    """

    CORRECT = "correct"
    WRONG = "wrong"
    NULL = "null"


class EvaluateGroundTruthTaskToolMatcher(BaseModel):
    """Ground truth for task tool matching evaluation."""

    tools: Union[List[ToolName], None] = None
    mcp_servers: Union[List[str], None] = None


class EvaluateInput(BaseModel):
    """Request model for MCP tool match endpoint."""

    task: Task
    requested_tools: List[ToolName]
    requested_mcp_servers: List[McpServer]


class EvaluateEntryTaskToolMatcher(BaseModel):
    """Result of task tool matching."""

    input: EvaluateInput
    groundtruth: EvaluateGroundTruthTaskToolMatcher
    match_tag: MatchTag
