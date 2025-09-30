"""Hybrid Task Tool Matcher implementation."""

import json
import logging
import re
from typing import List

from dotenv import dotenv_values
from openai import OpenAI
from pydantic import BaseModel

from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import (
    TaskToolMatcher,
    TaskToolMatchInput,
    TaskToolMatchOutput,
)
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchReason

PREPROCESSING_SYS_PROMPT = """You are a tool calling agent. Based on the dialog context, generate the description of the ideal tool that you should call.
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

CONDITIONS_SYS_PROMPT = """You are a guardrail agent. Your input is a JSON object with the following fields:
-  original prompt: the original user prompt
-  reformulated prompt: a description of an ideal tool that should be called to satisfy the user prompt
-  tool name: the name of the tool that is going to be called
- tool description: a description of the tool that is going to be called
Your task is to determine if the requested tool matches the original prompt based on the following conditions:
1. Semantic Match: The tool's description should semantically align with the reformulated prompt.
2. Intent Match: The tool's description should reflect the primary intent of the original prompt.
3. Parameter Match: The original prompt should contain parameters that are necessary for the tool.
For each condition, output true if the condition is met, otherwise false.

# input
"""


class StructuredTaskToolMatcherConditions(BaseModel):
    """Conditions for structured task-tool matcher."""

    semantic: bool
    intent: bool
    parameters: bool


class StructuredTaskToolMatcher(TaskToolMatcher):
    """A structured task-tool matcher that uses LLM prediction and embeddings to determine if a tool matches a task."""

    def __init__(self):
        """Initialize the structured matcher."""
        super().__init__()
        self.logger.setLevel(logging.DEBUG)
        config = dotenv_values(".env")
        self.openai_client = OpenAI(
            api_key=config.get("OPENAI_GPT4o_API_JWT_TOKEN"),
            base_url=config.get("OPENAI_GPT4o_API_BASE_URL"),
        )
        self.model_id = config.get("OPENAI_GPT4o_MODEL_ID")
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

        raw_response = self.openai_client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "system", "content": PREPROCESSING_SYS_PROMPT}, {"role": "user", "content": task}],
        )
        response = raw_response.choices[0].message.content
        parsing_match = re.search(r"tool:\s*(.+?)\s*</tool_assistant>", response, re.DOTALL)
        if parsing_match:
            reformulated_task = parsing_match.group(1).strip()
            self.logger.debug(f"Task: {task}")
            self.logger.debug(f"Reformulated Task: {reformulated_task}")
        else:
            self.logger.warning("No reformulated task found, using original task.")
            reformulated_task = task

        structured_input = {
            "original prompt": task,
            "reformulated prompt": reformulated_task,
            "tool name": requested_tool,
            "tool description": next((tool.description for tool in mcp_tools if tool.name == requested_tool), ""),
        }
        structured_raw_response = self.openai_client.responses.parse(
            model=self.model_id,
            input=[
                {"role": "system", "content": CONDITIONS_SYS_PROMPT},
                {"role": "user", "content": json.dumps(structured_input)},
            ],
            text_format=StructuredTaskToolMatcherConditions,
        )
        structured_response = structured_raw_response.output_parsed
        self.logger.debug(structured_response)

        matches = structured_response.intent and structured_response.semantic
        no_match_reason = TaskToolMatchReason.STRUCTURED_NO_MATCH if not matches else None
        debug_data = structured_response.__dict__
        if matches:
            self.logger.debug("Task and tool result:                                       APPROVED")
            self.logger.debug("")
            self.logger.debug("----- End of Structured Task Tool Match -----")
            self.logger.debug("")
            return TaskToolMatchOutput(task_tool_match=matches)
        else:
            self.logger.debug("Task and tool result:                                       REJECTED")
            self.logger.debug("")
            self.logger.debug("----- End of Structured Task Tool Match -----")
            self.logger.debug("")
            return TaskToolMatchOutput(task_tool_match=False, reason=no_match_reason, debug=debug_data)
