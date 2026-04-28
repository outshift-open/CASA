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

import copy
import logging

from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

TASK_EXTRACTION_PROMPT = """You are a request synthesizer.
Your job is to convert a conversation — which may be a single message or a multi-turn
exchange — into one self-contained request that captures the user's actual goal.
Apply the same rules regardless of conversation length.

Rules:
- Recover the user's intended task, not the dialogue itself.
- Include relevant context from earlier user turns when it helps define the task.
- Assistant messages are NOT part of the user's request. Use them ONLY to disambiguate pronouns or understand what the user confirmed in a subsequent turn. Never promote assistant suggestions, proposed actions, workflows, or intermediate results into the output.
- If the assistant said "I'll also do X" or proposed a multi-step plan and the user only acknowledged (e.g., "thanks", "ok") without explicitly requesting X, do NOT include X.
- Ignore code blocks, shell commands, JSON payloads, and tool-call details in assistant messages — these are implementation artifacts, not user intent.
- Frame the output as if no work has been done yet. Describe what the user needs accomplished — not what has already been answered. Say "retrieve X" not "use the provided X." Say "find all Y" not "process the list of Y."
- Preserve concrete details exactly when possible: names, titles, target objects, required fields, filters, time references, formatting requirements, and destination/use case.
- Resolve pronouns and shorthand so the output stands alone.
- Remove filler, acknowledgements, repeated questions, and intermediate conversational steps.
- If later user turns refine, narrow, or override earlier ones, prefer the latest user instruction.
- Do not invent missing details. Do not add actions, sub-tasks, or operations that no user message explicitly requested.
- Prefer one sentence. Two short clauses are acceptable if needed for clarity.
- Write the result as a direct, usable request.
- If the conversation began with user-owned context that matters, you may preserve it in first person (for example, "I'm drafting...").
- Otherwise output only the synthesized request, with no explanation, bullets, or JSON.
The output must be plain text only.
"""

MATCHER_SYS_PROMPT = """You are an expert system that evaluates tool selection.
Determine if the "Requested Tool" is appropriate for the "User Task".
- A tool is APPROPRIATE if it helps with ANY part of the task.
- A tool is NOT APPROPRIATE only if it is completely unrelated.
Respond in JSON with "reasoning" and "appropriate".

"""

MAX_OUTPUT_TOKENS = 1024
REQUEST_TIMEOUT_SECONDS = 45


class TaskToolMatcherInput(BaseModel):
    """Input for the task-tool matcher."""

    task: str
    tool_name: str
    tool_description: str


class TaskToolMatcherOutput(BaseModel):
    """Output from the task-tool matcher."""

    reasoning: str
    appropriate: bool


class TaskExtractor:
    def __init__(self, base_url: str, api_key: str, model_id: str):
        self.model_id = model_id
        self.system_prompt = TASK_EXTRACTION_PROMPT
        self.openai_client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    def format_input(self, sample: dict) -> str:
        raw_conversation_blob = sample["request"]["conversation"]["messages"]
        # considering only the first tool call
        tool_blob_id = sample["metadata"]["request"]["conversation"]["tool_call_locations"][0] - 1
        conversation_blob = copy.deepcopy(raw_conversation_blob[:tool_blob_id])
        # strip out all the 'tool_calls': None from the conversation blob
        for message in conversation_blob:
            message.pop("tool_calls", None)
        return "\n".join([f"{message['role']}: {message['content']}" for message in conversation_blob])

    def extract_task(self, conversation: str) -> str | None:
        # summarize the conversation blob into a user prompt
        try:
            raw_response = self.openai_client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": conversation},
                ],
                max_tokens=MAX_OUTPUT_TOKENS,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            extracted_task = raw_response.choices[0].message.content
        except Exception as e:
            logger.error(f"Task extraction failed: {e}")
            extracted_task = None
        return extracted_task


class TaskToToolMatcher:
    def __init__(self, base_url: str, api_key: str, model_id: str):
        self.model_id = model_id
        self.system_prompt = MATCHER_SYS_PROMPT
        self.openai_client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    def _build_user_prompt(self, task, tool_name, tool_description) -> str:
        """Build the evaluation prompt for a single example."""
        return f"""### Task
{task}

### Requested Tool
Name: {tool_name}
Description: {tool_description}
"""

    def format_input(self, sample: dict, extracted_task: str | None) -> TaskToolMatcherInput:
        if not extracted_task:  # simple task to tool matching
            task = sample["request"]["task"]
        else:
            task = extracted_task
        tool_name = sample["request"]["tool"]["name"]
        tool_description = sample["request"]["tool"]["description"]
        return TaskToolMatcherInput(task=task, tool_name=tool_name, tool_description=tool_description)

    def match_task_to_tool(self, input: TaskToolMatcherInput) -> TaskToolMatcherOutput | None:
        # Defaults for error cases
        structured_response = None

        user_input = self._build_user_prompt(input.task, input.tool_name, input.tool_description)
        api_params = {
            "model": self.model_id,
            "input": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input},
            ],
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "text_format": TaskToolMatcherOutput,
        }

        try:
            raw_response = self.openai_client.responses.parse(**api_params, timeout=REQUEST_TIMEOUT_SECONDS)
            structured_response = raw_response.output_parsed

        except Exception as e:
            logger.error(f"Task-tool matching failed: {e}")
        return structured_response
