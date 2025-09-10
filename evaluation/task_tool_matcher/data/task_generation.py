"""Synthetic generation of tasks corresponding to (MCP) tool descriptions provided in JSONs."""

import argparse
import asyncio
import json
import os
import time

from dotenv import dotenv_values
from openai import AsyncOpenAI
from system_prompts import OBSCURE_SYSTEM_PROMPT_TEMPLATE as SYSTEM_PROMPT_1_TOOL
from system_prompts import REPHRASE_SYSTEM_PROMPT
from tqdm import tqdm

# from tqdm.asyncio import tqdm

config = dotenv_values()

client = AsyncOpenAI(
    api_key=config.get("OPENAI_API_KEY"),
    base_url=config.get("OPENAI_API_BASE_URL"),
)


async def task_synthesizer(tool_data: dict, semaphore: asyncio.Semaphore, conversation: bool) -> dict | None:
    """Synthesizes tasks based on the description of a single MCP tool, with a generative model.

    Args:
        tool_data (dict): A dictionary with 'name', 'description', and 'inputSchema of MCP tools.
        semaphore (asyncio.Semaphore): To limit concurrent API calls to openai.
        conversation (bool): Whether to generate a conversation task or regular.

    Returns:
        A dictionary with the tool_name and generated task, or None on failure.
    """
    tool_description = tool_data.get("description", "N/A")
    cut_sequence = "\n    Args:\n"  # cutting off input args info (applies to atlassian & hummingbot & paper-search)
    if cut_sequence in tool_description:
        tool_description = tool_description.split(cut_sequence)[0]
    cut_sequence = "\n\nParameters:\n"  # cutting off input args information (applies to nasdaq)
    if cut_sequence in tool_description:
        tool_description = tool_description.split(cut_sequence)[0]

    system_prompt_template = SYSTEM_PROMPT_1_TOOL
    system_prompt = system_prompt_template.replace("[Tool Name]", tool_data.get("name", "N/A"))
    system_prompt = system_prompt.replace("[Tool Description]", tool_description)
    user_prompt = "Execute the user request and generate the corresponding output."

    async with semaphore:
        model_name = "gpt-4"
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        )
        synthetic_task = response.choices[0].message.content

        if conversation:  # TODO: adapt
            rephrase_prompt = REPHRASE_SYSTEM_PROMPT.format(task=synthetic_task)
            rephrase_response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": rephrase_prompt},
                    {"role": "user", "content": "Rephrase the above request."},
                ],
            )
            rephrased_task = rephrase_response.choices[0].message.content
            synthetic_task = rephrased_task

        return {
            "tool_name": tool_data.get("name"),
            "synthetic_task": synthetic_task,
            "system_prompt": "obscure_base" if not conversation else "obscure_base_plus_conv",
            "mcp_server": tool_data.get("mcp_server"),
        }


async def process_tools_files(input_paths: list[str], output_path: str, multiplier: int, conversation: bool):
    """Reads tools from JSON files, creates their tasks in parallel, and saves the results in dict."""
    final_results = []
    semaphore = asyncio.Semaphore(10)  # max 10 for openai async

    for input_path in input_paths:  # MCP server
        print(f"MCP: {input_path}")
        all_tools = []
        with open(input_path, "r") as f:
            mcp_server = json.load(f)
            tools = mcp_server.get("tools", [])
            for tool in tools:
                tool["mcp_server"] = mcp_server.get("name", "N/A")
            all_tools.extend(tools)

        for idx, tool in tqdm(
            enumerate(all_tools), total=len(all_tools)
        ):  # basic loop because it's 1 tool 1 task (otherwise sampler loop needed)
            tasks = [task_synthesizer(tool, semaphore, conversation) for _ in range(multiplier)]
            results = await asyncio.gather(*tasks)

            valid_results = [res for res in results if res is not None]
            if not valid_results:
                continue
            result = {
                "tool_names": [valid_results[0]["tool_name"]],
                "mcp_servers": [valid_results[0]["mcp_server"]],
                "synthetic_tasks": [res["synthetic_task"] for res in valid_results],
                "system_prompt": valid_results[0]["system_prompt"],
                "multi_tool": 1,
                "conversation": True if conversation else False,
            }
            final_results.append(result)

            if idx % 20 == 0:
                with open(output_path, "w") as f:
                    json.dump(final_results, f, indent=2)


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
    parser.add_argument("--conversation", action="store_true", help="Generate conversation tasks if set to True.")

    args = parser.parse_args()

    input_files = [os.path.join(args.input_dir, f) for f in os.listdir(args.input_dir) if f.endswith(".json")]

    if not input_files:
        print(f"No JSON files (ending with '.json') found in {args.input_dir}")
        return

    start_time = time.time()
    await process_tools_files(input_files, args.output_file, args.multiplier, args.conversation)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
