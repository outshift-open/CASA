# Copyright 2026 Google LLC
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

"""Common validation logic for TaskToolMatchers."""

from casa_auth_server.pipelines.exceptions import PipelineValidationError
from casa_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchInput


class TaskToolValidator:
    """Common validation logic for TaskToolMatchers."""

    @staticmethod
    def validate_task_not_empty(input: TaskToolMatchInput) -> None:
        """Validate that the task description is not empty.

        Args:
            input: The task tool match input to validate

        Raises:
            PipelineValidationError: If the task is empty
        """
        if not input.task or not input.task.strip():
            raise PipelineValidationError("Task description cannot be empty")

    @staticmethod
    def validate_requested_tool_not_empty(input: TaskToolMatchInput) -> None:
        """Validate that the requested tool is not empty.

        Args:
            input: The task tool match input to validate

        Raises:
            PipelineValidationError: If the requested tool is empty
        """
        if not input.requested_tool or not input.requested_tool.strip():
            raise PipelineValidationError("Requested tool cannot be empty")

    @staticmethod
    def validate_requested_tool_within_mcp_tools(input: TaskToolMatchInput) -> None:
        """Validate that the requested tool is part of the MCP Server tools.

        Args:
            input: The task tool match input to validate

        Raises:
            PipelineValidationError: If requested tool is not in MCP Server tools
        """
        if input.requested_tool not in {tool.name for tool in input.mcp_server.tools}:
            raise PipelineValidationError("Requested tool must be one of the provided MCP tools")

    @classmethod
    def run_common_validations(cls, input: TaskToolMatchInput) -> None:
        """Run all common validations in sequence.

        Args:
            input: The task tool match input to validate

        Raises:
            PipelineValidationError: If any validation fails
        """
        cls.validate_task_not_empty(input)
        cls.validate_requested_tool_not_empty(input)
        cls.validate_requested_tool_within_mcp_tools(input)
