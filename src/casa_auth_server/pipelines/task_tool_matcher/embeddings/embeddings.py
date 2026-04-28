# Copyright 2025 Cisco Systems, Inc. and its affiliates
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

"""Embeddings based Task Tool Matcher Implementation."""

import logging
import re

import numpy as np
from dotenv import dotenv_values

from casa_auth_server.pipelines.task_tool_matcher.task_tool_matcher import (
    TaskToolMatcher,
    TaskToolMatchInput,
    TaskToolMatchOutput,
)
from casa_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchReason
from casa_auth_server.pipelines.task_tool_matcher.utils import (
    EmbeddingService,
    EmbeddingTopNMatches,
)


class EmbeddingsTaskToolMatcher(TaskToolMatcher):
    """A basic task-tool matcher that uses embeddings to determine if a tool matches a task."""

    def __init__(self, match_threshold: float = 0.2):
        """Initialize the embeddings matcher.

        Args:
            match_threshold: Threshold for determining a match (0.0 to 1.0)
        """
        super().__init__()
        self.logger.setLevel(logging.DEBUG)
        config = dotenv_values(".env")
        self.match_threshold = match_threshold
        if not 0.0 <= self.match_threshold <= 1.0:
            raise ValueError("match_threshold must be between 0.0 and 1.0")
        self.embedding_service = EmbeddingService(config)
        self.tool_names: list[str] = []
        self.tuning = False

    def set_tuning_mode(self) -> None:
        """Matcher in tuning mode."""
        self.tuning = True
        self.logger.debug("Matcher in tuning mode.")

    def match(
        self,
        input: TaskToolMatchInput,
    ) -> TaskToolMatchOutput:
        """Basic solution that leverages embeddings to determine if a requested tool matches the given task.

        Args:
            input (TaskToolMatchInput): The task description, requested tool, available tools, and MCP tools.

        Returns:
            TaskToolMatchOutput: The result of the match operation.

        Raises:
            PipelineValidationError: If input validation fails
        """
        # Run common validations first - will raise exception if validation fails
        self._validate_input(input)

        task = input.task
        requested_tool = input.requested_tool
        mcp_tools = input.mcp_server.tools

        # Embedding all the tools - not considering available tools for now -
        self.tool_names = [tool.name for tool in mcp_tools]
        tools_to_embed = [f"{tool.name}: {re.sub(r'[ \t]+', ' ', tool.description.strip())}" for tool in mcp_tools]
        embedded_tools = self.embedding_service.get_embeddings(tools_to_embed)
        embedded_task = self.embedding_service.get_embeddings([task])

        matched: EmbeddingTopNMatches = self.embedding_service.get_top_n_matches(
            np.array(embedded_task), np.array(embedded_tools), n=1
        )[0]

        matched_tool = self.tool_names[matched.index]
        self.logger.debug(f"Task: {task}")
        self.logger.debug(f"# Total Tools: {len(mcp_tools)}")
        self.logger.debug(f"Requested Tool: {requested_tool}")
        self.logger.debug(f"Matched Tool: {matched_tool}")
        # self.logger.debug(f"Matched Tool Description: {tools_to_embed[matched.index]}")
        self.logger.debug(f"Matched Distance: {matched.distance}")

        task_to_tool_matches = False
        selected_task_to_similar_tool = False
        no_match_reason = None
        if matched.distance >= self.match_threshold:
            task_to_tool_matches = True
        else:
            no_match_reason = TaskToolMatchReason.EMBEDDINGS_NO_MATCH_THRESHOLD
        if matched_tool == requested_tool:
            selected_task_to_similar_tool = True
        else:
            no_match_reason = TaskToolMatchReason.EMBEDDINGS_NO_MATCH_WITH_SELECTED

        if not task_to_tool_matches and not selected_task_to_similar_tool:
            no_match_reason = TaskToolMatchReason.EMBEDDINGS_NO_MATCH_WITH_ALL

        if self.tuning:
            # bypass the selected task to similar tool match condition
            selected_task_to_similar_tool = True

        matches = task_to_tool_matches and selected_task_to_similar_tool
        debug_data = {
            "requested_tool": requested_tool,
            "matched_tool": matched_tool,
            "matched_distance": matched.distance,
            "matching_threshold": self.match_threshold,
        }

        if matches:
            self.logger.debug("Match found!")
            return TaskToolMatchOutput(task_tool_match=matches)
        else:
            self.logger.debug("No match found.")
            return TaskToolMatchOutput(task_tool_match=False, reason=no_match_reason, debug=debug_data)
