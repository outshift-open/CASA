"""Type definitions for Evaluation - Task Tool Matcher."""

from typing import Union

from pydantic import BaseModel

from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchInput
from identity_auth_server.types import ToolName


class EvaluateEntryTaskToolMatcher(BaseModel):
    """Result of task tool matching."""

    input: TaskToolMatchInput
    correct_choice: Union[ToolName, None] = None
    match: bool
