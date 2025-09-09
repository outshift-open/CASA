"""Hybrid Task Tool Matcher implementation."""

import logging
import re
from typing import List

import numpy as np
from dotenv import dotenv_values
from openai import OpenAI

from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import (
    TaskToolMatcher,
    TaskToolMatchInput,
    TaskToolMatchOutput,
)
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchReason
from identity_auth_server.pipelines.task_tool_matcher.utils import EmbeddingService, EmbeddingTopNMatches

SYS_PROMPT = """Generate an API request with the tool description based on the dialogue context.
The tool description should be concise and to the point, and MUST be in the following format:

<tool_assistant>
tool: [describe the tool functionality]
</tool_assistant>

Based on the dialogue context, identify the specific task that needs to be performed and describe it accurately using a style similar to API documentation. Ensure your description is clear, precise, and do not include detailed values.

Example dialogue:
User: Hi, can you help me check my alarm for March 20th, 2023 at 6:30AM?
AI: Sure, to access your alarm information, I'll need to authenticate. Can you please provide me with your email, username, and password?
User: My email is janesmith@example.com, username is JaneSmith, and password is password.
AI: Thank you for the information. Let me authenticate you first.

Example output:
<tool_assistant>
tool: Get the user token by username and password.
</tool_assistant>

Only output the tool description within the specified format. Do not provide any explanation or commentary.
"""


class HybridTaskToolMatcher(TaskToolMatcher):
    """A hybrid task-tool matcher that uses LLM prediction and embeddings to determine if a tool matches a task."""

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
        self.openai_client = OpenAI(
            api_key=config.get("OPENAI_GPT4o_API_JWT_TOKEN"),
            base_url=config.get("OPENAI_GPT4o_API_BASE_URL"),
        )
        self.model_id = config.get("OPENAI_GPT4o_MODEL_ID")
        self.embedding_service = EmbeddingService(config)
        self.tool_names: List[str] = []

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

        # Embedding all the tools
        self.tool_names = [tool.name for tool in mcp_tools]
        tools_to_embed = [f"{tool.name}: {re.sub(r'[ \t]+', ' ', tool.description.strip())}" for tool in mcp_tools]
        embedded_tools = self.embedding_service.get_embeddings(tools_to_embed)

        raw_response = self.openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "system", "content": SYS_PROMPT}, {"role": "user", "content": task}],
        )
        response = raw_response.choices[0].message.content
        parsing_match = re.search(r"tool:\s*(.+?)\s*</tool_assistant>", response, re.DOTALL)
        if parsing_match:
            suggested_task = parsing_match.group(1).strip()
            embedded_task = self.embedding_service.get_embeddings([suggested_task])
            self.logger.debug(f"Task: {task}")
            self.logger.debug(f"Suggested Task: {suggested_task}")
        else:
            self.logger.warning("No suggested task found, using original task.")
            embedded_task = self.embedding_service.get_embeddings([task])

        matched: EmbeddingTopNMatches = self.embedding_service.get_top_n_matches(
            np.array(embedded_task), np.array(embedded_tools), n=1
        )[0]
        matched_tool = self.tool_names[matched.index]

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
            no_match_reason = TaskToolMatchReason.HYBRID_NO_MATCH_THRESHOLD
        if matched_tool == requested_tool:
            selected_task_to_similar_tool = True
        else:
            no_match_reason = TaskToolMatchReason.HYBRID_NO_MATCH_WITH_SELECTED

        if not task_to_tool_matches and not selected_task_to_similar_tool:
            no_match_reason = TaskToolMatchReason.HYBRID_NO_MATCH_WITH_ALL

        matches = task_to_tool_matches and selected_task_to_similar_tool

        if matches:
            self.logger.debug("Match found!")
            return TaskToolMatchOutput(task_tool_match=matches)
        else:
            self.logger.debug("No match found.")
            return TaskToolMatchOutput(task_tool_match=False, reason=no_match_reason)
