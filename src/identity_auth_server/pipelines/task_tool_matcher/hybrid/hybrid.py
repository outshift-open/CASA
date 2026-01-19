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

SYS_PROMPT = """You are a tool calling agent. Based on the dialog context, generate the description of the ideal tool that you should
call using a style similar to API documentation.
The tool description should be concise and to the point, should not include detailed values, and MUST be in the
following format:
<tool_assistant>
tool: [describe the tool functionality]
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
        self.model_id = config.get("PIPELINE_OPENAI_GPT4o_MODEL_ID")
        self.embedding_service = EmbeddingService(config)
        self.tool_names: List[str] = []
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
        suggested_task = ""

        # Embedding all the tools
        self.tool_names = [tool.name for tool in mcp_tools]
        tools_to_embed = [f"{tool.name}: {re.sub(r'[ \t]+', ' ', tool.description.strip())}" for tool in mcp_tools]
        embedded_tools = self.embedding_service.get_embeddings(tools_to_embed)

        raw_response = self.openai_client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "system", "content": SYS_PROMPT}, {"role": "user", "content": task}],
            temperature=0.0,
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

        task_to_tool_matches = False
        selected_task_to_similar_tool = False
        no_match_reason = None

        if self.tuning:
            # bypass the selected task to similar tool match condition
            selected_task_to_similar_tool = True

        debug_data = {
            "requested_tool": requested_tool,
            "suggested_task": suggested_task,
            "matched_tool": matched_tool,
            "matched_distance": matched.distance,
            "match_threshold": self.match_threshold,
        }
        self.logger.debug(f"Requested Tool:  {requested_tool.upper()}")
        # self.logger.debug(f"# Total Tools: {len(mcp_tools)}")
        self.logger.debug(f"Matched Tool:    {matched_tool.upper()}")
        self.logger.debug(f"Distance: {matched.distance}")
        self.logger.debug("")
        # self.logger.debug(f"debug data: {debug_data}")

        if matched_tool == requested_tool:
            selected_task_to_similar_tool = True
            self.logger.debug("Requested tool and Matched tool are the same:               TRUE")
        else:
            no_match_reason = TaskToolMatchReason.HYBRID_NO_MATCH_WITH_SELECTED
            self.logger.debug("Requested tool and Matched tool are the same:               FALSE")
        if matched.distance >= self.match_threshold:
            task_to_tool_matches = True
            self.logger.debug("Requested tool and Matched tool similarity above threshold: TRUE")
        else:
            no_match_reason = TaskToolMatchReason.HYBRID_NO_MATCH_THRESHOLD
            self.logger.debug("Requested tool and Matched tool similarity above threshold: FALSE")

        if not task_to_tool_matches and not selected_task_to_similar_tool:
            no_match_reason = TaskToolMatchReason.HYBRID_NO_MATCH_WITH_ALL

        if self.tuning:
            # bypass the selected task to similar tool match condition
            selected_task_to_similar_tool = True

        matches = task_to_tool_matches and selected_task_to_similar_tool

        if matches:
            self.logger.debug("Task and tool result:                                       APPROVED")
            self.logger.debug("")
            self.logger.debug("----- End of Hybrid Task Tool Match -----")
            self.logger.debug("")
            return TaskToolMatchOutput(task_tool_match=matches)
        else:
            self.logger.debug("Task and tool result:                                       REJECTED")
            self.logger.debug("")
            self.logger.debug("----- End of Hybrid Task Tool Match -----")
            self.logger.debug("")
            return TaskToolMatchOutput(task_tool_match=False, reason=no_match_reason, debug=debug_data)
