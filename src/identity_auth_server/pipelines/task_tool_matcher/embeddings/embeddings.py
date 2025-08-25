"""Embeddings based Task Tool Matcher Implementation."""

import logging
import re
from typing import List, Tuple

import numpy as np
from dotenv import dotenv_values
from openai import OpenAI

from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import (
    TaskToolMatcher,
    TaskToolMatchInput,
    TaskToolMatchOutput,
)
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchReason


class EmbeddingsTaskToolMatcher(TaskToolMatcher):
    """A basic task-tool matcher that uses embeddings to determine if a tool matches a task."""

    def __init__(self, match_threshold: float = 0.3):
        """Initialize the embeddings matcher.

        Args:
            match_threshold: Threshold for determining a match (0.0 to 1.0)
        """
        super().__init__()
        self.logger.setLevel(logging.DEBUG)
        config = dotenv_values(".env")
        if not 0.0 <= match_threshold <= 1.0:
            raise ValueError("match_threshold must be between 0.0 and 1.0")
        self.match_threshold = match_threshold
        self.embedding_client = OpenAI(
            api_key=config.get("OPENAI_TXT_EMB_3_LARGE_API_JWT_TOKEN"),
            base_url=config.get("OPENAI_TXT_EMB_3_LARGE_API_BASE_URL"),
        )
        self.embedding_model_id = config.get("OPENAI_TXT_EMB_3_LARGE_MODEL_ID")
        self.tool_names: List[str] = []

    def _get_embeddings(self, input: List[str]) -> List[np.ndarray]:
        """Get embeddings for a list of input texts.

        Args:
            input: A list of input texts to embed

        Returns:
            List[np.ndarray]: A list of embeddings for the input texts
        """
        response = self.embedding_client.embeddings.create(input=input, model=self.embedding_model_id).data
        return [np.array(data.embedding) for data in response]

    def _get_top_n_matches(self, task: np.ndarray, tools: np.ndarray, n: int = 1) -> List[Tuple[str, float, int]]:
        """Get the top N matches from the distance array.

        Args:
            task: The embedded task vector
            tools: The embedded tools matrix
            n: The number of top matches to return

        Returns:
            List[Tuple[str, float, int]]: A list of tuples containing the tool name, distance, and index for the top N matches.
        """
        distances = np.dot(task, tools.T).flatten()
        top_n_indices = distances.argsort()[-n:][::-1]
        return [(self.tool_names[i], distances[i], i) for i in top_n_indices]

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
        available_tools = input.available_tools
        mcp_tools = input.mcp_tools

        # Embedding all the tools - not considering available tools for now -
        self.tool_names = [tool.name for tool in mcp_tools]
        tools_to_embed = [f"{tool.name}: {re.sub(r'[ \t]+', ' ', tool.description.strip())}" for tool in mcp_tools]
        embedded_tools = self._get_embeddings(tools_to_embed)

        embedded_task = self._get_embeddings([task])

        matched_tool, matched_distance, matched_index = self._get_top_n_matches(
            np.array(embedded_task), np.array(embedded_tools), n=1
        )[0]

        self.logger.debug(f"Task: {task}")
        self.logger.debug(f"Requested Tool: {requested_tool}")
        self.logger.debug(f"Matched Tool: {matched_tool}")
        self.logger.debug(f"Number of Available Tools: {len(available_tools)}")
        self.logger.debug(f"Matched Tool Description: {tools_to_embed[matched_index]}")
        self.logger.debug(f"Matched Distance: {matched_distance}")

        matches = matched_tool == requested_tool and matched_distance >= self.match_threshold

        if matches:
            self.logger.debug("Match found!")
            return TaskToolMatchOutput(task_tool_match=matches)
        else:
            self.logger.debug("No match found.")
            return TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.EMBEDDINGS_NO_MATCH)
