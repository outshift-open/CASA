# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Type definitions for Identity Auth Server - Pipelines - Task Tool Matcher."""

from enum import Enum
from typing import Any

from pydantic import BaseModel

from casa_auth_server.types import McpServer, Task, ToolName


class TaskToolMatcherType(str, Enum):
    """Available task-tool matcher types."""

    RANDOM = "random"
    EMBEDDINGS = "embeddings"


class TaskToolMatchReason(str, Enum):
    """Common reasons for task tool match results."""

    # Validation errors
    TOOL_NOT_AVAILABLE = "tool_not_available"
    TASK_EMPTY = "task_empty"

    # Matcher-specific reasons
    RANDOM_NO_MATCH = "Random matcher decided this tool doesn't match the task"
    EMBEDDINGS_NO_MATCH_THRESHOLD = "Requested tool and Matched tool similarity does not meet threshold"
    EMBEDDINGS_NO_MATCH_WITH_SELECTED = "Requested tool and Matched tool are not the same"
    EMBEDDINGS_NO_MATCH_WITH_ALL = (
        "Requested tool and Matched tool are not the same AND their similarity does not meet threshold"
    )


class TaskToolMatchInput(BaseModel):
    """Request model for MCP tool match endpoint."""

    task: Task
    requested_tool: ToolName
    mcp_server: McpServer


class TaskToolMatchOutput(BaseModel):
    """Result of task tool matching."""

    task_tool_match: bool
    reason: TaskToolMatchReason | None = None
    debug: dict[str, Any] | None = None
