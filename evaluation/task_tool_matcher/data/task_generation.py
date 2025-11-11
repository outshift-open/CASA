"""Synthetic generation of tasks corresponding to (MCP) tool descriptions provided in JSONs."""

import argparse
import asyncio
import json
import os
import random
import time
from typing import List

from dotenv import dotenv_values
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, create_model
from system_prompts import CONVERSATION_SYSTEM_PROMPT_TEMPLATE as SYSTEM_PROMPT_CONVERSATION
from system_prompts import OBSCURE_SYSTEM_PROMPT_TEMPLATE as SYSTEM_PROMPT_1_TOOL
from system_prompts import OBSCURE_SYSTEM_PROMPT_TEMPLATE_N_TOOLS as SYSTEM_PROMPT_N_TOOLS
from tqdm import tqdm

# from tqdm.asyncio import tqdm

config = dotenv_values()

client = AsyncOpenAI(
    api_key=config.get("OPENAI_API_KEY"),
    base_url=config.get("OPENAI_API_BASE_URL"),
)


class SyntheticTask(BaseModel):
    """A single synthetic task for the tool."""

    task_text: str = Field(..., description="The text of the synthetic task.")


def create_tasks_model(n: int) -> type[BaseModel]:
    """Dynamically create a Pydantic model for a list of n tasks."""
    tasks_model = create_model(
        "SyntheticTasks",
        tasks=(List[SyntheticTask], Field(..., min_items=n, max_items=n)),
        __doc__=f"A list of {n} different synthetic tasks for the gen query.",
    )
    return tasks_model


class SyntheticConversation(BaseModel):
    """A single synthetic task-oriented conversation leading to a tool call (generated from tools)."""

    conversation_text: str = Field(..., description="The generated conversation text.")
    number_exchanges: int = Field(
        ..., description="The total number of exchanges taking place during the conversation."
    )
    final_tool_name: str = Field(..., description="The name of the final tool remaining to be called.")


def create_conversation_model() -> type[BaseModel]:
    """Dynamically create a Pydantic model for a synthetic conversation."""
    conversation_model = create_model(
        "SyntheticConversation",
        conversation_text=(str, Field(..., description="The generated conversation text.")),
        number_exchanges=(
            int,
            Field(..., description="The total number of exchanges taking place during the conversation."),
        ),
        final_tool_name=(str, Field(..., description="The name of the final tool remaining to be called.")),
    )
    return conversation_model


async def task_synthesizer(
    tool_set: list[dict], semaphore: asyncio.Semaphore, conversation: bool, n_tasks: int
) -> list[dict] | None:
    """Synthesizes tasks based on the description of a single MCP tool, with a generative model.

    Args:
        tool_set (list[dict]): A list of dictionaries with 'name', 'description', and 'inputSchema' of each tool.
        semaphore (asyncio.Semaphore): To limit concurrent API calls to openai.
        conversation (bool): Whether to generate a conversation task or regular.
        n_tasks (int): The number of tasks to generate per tool (or tool set).

    Returns:
        A list of dictionaries, each with the tool_name and a generated task, or None on failure.
    """
    for tool_data in tool_set:
        tool_description = tool_data["description"]
        # cutting off input args info (applies to atlassian & hummingbot & paper-search, nasdaq, stripe)
        cut_sequences = ["\n    Args:\n", "\n\nParameters:\n", "\n\nIt takes"]
        for cut_sequence in cut_sequences:
            if cut_sequence in tool_description:
                tool_description = tool_description.split(cut_sequence)[0]
        tool_data["description"] = tool_description.rstrip("\n")

    if len(tool_set) == 1:
        system_prompt_template = SYSTEM_PROMPT_1_TOOL
        system_prompt = system_prompt_template.replace("[Tool Name]", tool_set[0]["name"])
        system_prompt = system_prompt.replace("[Tool Description]", tool_set[0]["description"])
    else:
        system_prompt_template = SYSTEM_PROMPT_N_TOOLS
        system_prompt = system_prompt_template.replace(
            "[Tools Information]",
            "\n".join(
                [
                    f"**Tool Name:**\n`{tool_data['name']}`\n\n**Tool Description:**\n`{tool_data['description']}`\n"
                    for tool_data in tool_set
                ]
            ),
        )

    user_prompt = f"Execute the user request and generate {n_tasks} corresponding output example(s), make sure the various examples are diverse, **not similar** to each other."
    tasks_model = create_tasks_model(n_tasks)

    async with semaphore:
        model_name = "gpt-4o"
        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                tools=[
                    {
                        "type": "function",
                        "function": {"name": "SyntheticTasks", "parameters": tasks_model.model_json_schema()},
                    }
                ],
                tool_choice={"type": "function", "function": {"name": "SyntheticTasks"}},
            )

            tool_calls = response.choices[0].message.tool_calls
            if not tool_calls:
                print("The model did not return any tool calls.")
                return None

            tasks_json = tool_calls[0].function.arguments
            structured_response = tasks_model.model_validate_json(tasks_json)

            synthetic_tasks = [task.task_text for task in structured_response.tasks]

            if conversation:
                conversation_samples = []
                conversation_model = create_conversation_model()
                for task in synthetic_tasks:
                    conversation_prompt = SYSTEM_PROMPT_CONVERSATION.replace("([(User Task Request)])", task)
                    conversation_prompt = conversation_prompt.replace(
                        "([(Tools Information)])",
                        "\n".join(
                            [
                                f"**Tool Name:**\n`{tool_data['name']}`\n\n**Tool Description:**\n`{tool_data['description']}`\n\n**Input Schema:**\n`{json.dumps(tool_data['inputSchema'])}`\n\n**Output Schema:**\n`{json.dumps(tool_data['outputSchema'])}`\n\n\n"
                                for tool_data in tool_set
                            ]
                        ),
                    )
                    conversation_response = await client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": conversation_prompt},
                            {"role": "user", "content": "Execute the above request."},
                        ],
                        tools=[
                            {
                                "type": "function",
                                "function": {
                                    "name": "SyntheticConversation",
                                    "parameters": conversation_model.model_json_schema(),
                                },
                            }
                        ],
                        tool_choice={"type": "function", "function": {"name": "SyntheticConversation"}},
                    )

                    tool_calls = conversation_response.choices[0].message.tool_calls
                    if not tool_calls:
                        print("The conversation model did not return any tool calls.")
                        return None

                    tasks_json = tool_calls[0].function.arguments
                    structured_response = conversation_model.model_validate_json(tasks_json)

                    conversation_samples.append(
                        {
                            "tool_names": [tool_data["name"] for tool_data in tool_set],
                            "mcp_servers": [tool_data["mcp_server"] for tool_data in tool_set],
                            "synthetic_task": structured_response.conversation_text,
                            "root_intent_task": task,
                            "number_exchanges": structured_response.number_exchanges,
                            "final_tool_name": structured_response.final_tool_name,
                            "system_prompt": "conversation",
                        }
                    )
                return conversation_samples

            return [
                {
                    "tool_names": [tool_data["name"] for tool_data in tool_set],
                    "synthetic_task": task,
                    "system_prompt": "obscure_base" if not conversation else "obscure_base_plus_conv",
                    "mcp_servers": [tool_data["mcp_server"] for tool_data in tool_set],
                }
                for task in synthetic_tasks
            ]
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


async def process_tools_files(
    input_paths: list[str], output_path: str, n_tasks: int, conversation: bool, num_tools: int
) -> None:
    """Reads tools from JSON files, creates their tasks in parallel, and saves the results in dict."""
    final_results = []
    semaphore = asyncio.Semaphore(10)  # max 10, for openai async

    mcp_to_tools_hash = {}
    for input_path in input_paths:  # MCP server
        print(f"MCP: {input_path}")
        all_tools = []
        with open(input_path, "r") as f:
            mcp_server = json.load(f)
            tools = mcp_server.get("tools", [])
            for tool in tools:
                tool["mcp_server"] = mcp_server.get("name", "N/A")
            mcp_to_tools_hash[mcp_server["name"]] = tools
            all_tools.extend(tools)

        for idx, tool in tqdm(enumerate(all_tools), total=len(all_tools)):
            tool_set = [tool]
            if num_tools > 1:
                current_mcp = tool["mcp_server"]
                other_tools_from_mcp = [t for t in mcp_to_tools_hash[current_mcp] if t["name"] != tool["name"]]

                if num_tools - 1 > len(other_tools_from_mcp):
                    raise ValueError(
                        f"Not enough other tools ({len(other_tools_from_mcp)}) to sample {num_tools - 1} tools in MCP server '{current_mcp}'."
                    )

                sampled_tools = random.sample(other_tools_from_mcp, num_tools - 1)
                tool_set.extend(sampled_tools)

            results = await task_synthesizer(tool_set, semaphore, conversation, n_tasks)

            if not results:
                continue

            if conversation:
                result = {
                    "tool_names": results[0]["tool_names"],
                    "mcp_servers": results[0]["mcp_servers"],
                    "synthetic_tasks": [res["synthetic_task"] for res in results],
                    "root_intent_task": [res["root_intent_task"] for res in results],
                    "number_exchanges": [res["number_exchanges"] for res in results],
                    "final_tool_name": [res["final_tool_name"] for res in results],
                    "system_prompt": results[0]["system_prompt"],
                    "tools_per_task": num_tools,
                    "SO_tasks_per_sample": n_tasks,
                    "conversation": True if conversation else False,
                }
            else:
                result = {
                    "tool_names": results[0]["tool_names"],
                    "mcp_servers": results[0]["mcp_servers"],
                    "synthetic_tasks": [res["synthetic_task"] for res in results],
                    "system_prompt": results[0]["system_prompt"]
                    if num_tools == 1
                    else results[0]["system_prompt"] + "_multitool",
                    "tools_per_task": num_tools,
                    "SO_tasks_per_sample": n_tasks,
                    "conversation": True if conversation else False,
                }
            final_results.append(result)

            with open(output_path, "w") as f:
                json.dump(final_results, f, indent=2)

    return None


async def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic tasks from a JSON file of MCP Server descriptions."
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Path to the input directory containing JSON files with MCP server info (tools &more).",
    )
    parser.add_argument(
        "--output-file", required=True, help="Path to the output JSON file to save the synthetic tasks (+meta info)."
    )
    parser.add_argument(
        "--multiplier", type=int, default=1, help="Number of synthetic tasks to generate per (MCP) tool."
    )
    parser.add_argument("--conversation", action="store_true", help="Generate conversation data if set to True.")

    def positive_int(value):
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(f"{value} is not a positive int value, num_tools per task must be >= 1")
        return ivalue

    parser.add_argument(
        "--num_tools",
        type=positive_int,
        default=1,
        help="Number of tools per generated task (must be positive non-zero int).",
    )

    args = parser.parse_args()

    input_files = [os.path.join(args.input_dir, f) for f in os.listdir(args.input_dir) if f.endswith(".json")]

    if not input_files:
        print(f"No JSON files (ending with '.json') found in {args.input_dir}")
        return

    start_time = time.time()
    await process_tools_files(input_files, args.output_file, args.multiplier, args.conversation, args.num_tools)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
