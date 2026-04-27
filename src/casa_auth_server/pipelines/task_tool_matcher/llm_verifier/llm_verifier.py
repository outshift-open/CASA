"""Hybrid Task Tool Matcher implementation."""

import json
import logging
import os

import httpx
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from casa_auth_server.pipelines.task_tool_matcher.task_tool_matcher import (
    TaskToolMatcher,
    TaskToolMatchInput,
    TaskToolMatchOutput,
)
from casa_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchReason

SYS_PROMPT = """You are a guardrail agent. You are responsible for providing access to tools based on user requests.
Analyze the user request and the requested tool to determine if the tool is appropriate to fulfill the user request.
Note that a tool is **appropriate** if it can help accomplish ANY part of the user's request, even if additional tools are needed to complete the full task.
A tool is **not appropriate** only if it is unrelated or would not contribute to fulfilling the user's request.

Your input is a JSON object with the following fields:
- original prompt: the original user prompt
- tool name: the name of the tool that is requested to be called
- tool description: a description of the tool that is requested to be called

# input
"""


class LlmVerifierTaskToolMatcherConditions(BaseModel):
    """Conditions for llm verifier task-tool matcher."""

    appropriate: bool


class LlmVerifierTaskToolMatcher(TaskToolMatcher):
    """A Llm Verifier task-tool matcher that uses LLM prediction to determine if a tool matches a task."""

    def __init__(self):
        """Initialize the verifier matcher."""
        super().__init__()
        self.logger.setLevel(logging.DEBUG)
        load_dotenv(".env")
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_GPT4o_API_JWT_TOKEN"),
            base_url=os.getenv("OPENAI_GPT4o_API_BASE_URL"),
            timeout=httpx.Timeout(30.0, connect=5.0),
        )
        self.model_id = os.getenv("PIPELINE_OPENAI_GPT4o_MODEL_ID")
        self.tool_names = []
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

        structured_input = {
            "original prompt": task,
            "tool name": requested_tool,
            "tool description": next((tool.description for tool in mcp_tools if tool.name == requested_tool), ""),
        }
        self.logger.debug(f"LLM Verifier structured input: {json.dumps(structured_input, indent=2)}")
        structured_raw_response = self.openai_client.responses.parse(
            model=self.model_id,
            input=[
                {"role": "system", "content": SYS_PROMPT},
                {"role": "user", "content": json.dumps(structured_input)},
            ],
            text_format=LlmVerifierTaskToolMatcherConditions,
            temperature=0.0,
        )
        structured_response = structured_raw_response.output_parsed
        self.logger.debug(structured_response)

        matches = structured_response.appropriate
        no_match_reason = TaskToolMatchReason.LLM_VERIFIER_NO_MATCH if not matches else None
        debug_data = structured_response.__dict__
        if matches:
            self.logger.debug("Task and tool result:                                       APPROVED")
            self.logger.debug("")
            self.logger.debug("----- End of LLM Verifier Task Tool Match -----")
            self.logger.debug("")
            return TaskToolMatchOutput(task_tool_match=matches)
        else:
            self.logger.debug("Task and tool result:                                       REJECTED")
            self.logger.debug("")
            self.logger.debug("----- End of LLM Verifier Task Tool Match -----")
            self.logger.debug("")
            return TaskToolMatchOutput(task_tool_match=False, reason=no_match_reason, debug=debug_data)
