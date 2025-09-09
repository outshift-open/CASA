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
from tqdm.asyncio import tqdm

config = dotenv_values()

client = AsyncOpenAI(
    api_key=config.get("OPENAI_API_KEY"),
    base_url=config.get("OPENAI_API_BASE_URL"),
)


async def task_synthesizer(tool_data: dict, semaphore: asyncio.Semaphore, obscure: bool) -> dict | None:
    """Synthesizes tasks based on the description of a single MCP tool, with a generative model.

    Args:
        tool_data (dict): A dictionary with 'name', 'description', and 'inputSchema of MCP tools.
        semaphore (asyncio.Semaphore): To limit concurrent API calls to openai.
        obscure (bool): Whether to generate an obscure task or regular.

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
        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            )
            synthetic_task = response.choices[0].message.content

            if obscure:
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
                "system_prompt": "obscure_base" if not obscure else "obscure_base_plus_conv",
                "mcp_server": tool_data.get("mcp_server"),
            }
        except Exception as e:
            print(f"Error processing tool {tool_data.get('name', 'N/A')}: {e}")
            return None


async def process_tools_files(input_paths: list[str], output_path: str, multiplier: int, obscure: bool):
    """Reads tools from JSON files, creates their tasks in parallel, and saves the results in dict."""
    all_tools = []
    for input_path in input_paths:  # MCP server
        with open(input_path, "r") as f:
            mcp_server = json.load(f)
            tools = mcp_server.get("tools", [])
            for tool in tools:
                tool["mcp_server"] = mcp_server.get("name", "N/A")
            all_tools.extend(tools)

    final_results = []
    semaphore = asyncio.Semaphore(10)  # max 10 for openai async

    for idx, tool in enumerate(all_tools):
        tasks = [task_synthesizer(tool, semaphore, obscure) for _ in range(multiplier)]
        results = await tqdm.gather(*tasks)

        valid_results = [res for res in results if res is not None]
        if not valid_results:
            continue
        result = {
            "tool_name": [valid_results[0]["tool_name"]],
            "mcp_server": [valid_results[0]["mcp_server"]],
            "synthetic_tasks": [res["synthetic_task"] for res in valid_results],
            "system_prompt": valid_results[0]["system_prompt"],
        }
        final_results.append(result)

    if idx % 100 == 0:
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
    parser.add_argument(
        "--obscure", action="store_true", help="Generate more obscure tasks (hide input schema + new sys_prompt)."
    )

    args = parser.parse_args()

    input_files = [os.path.join(args.input_dir, f) for f in os.listdir(args.input_dir) if f.endswith(".json")]

    if not input_files:
        print(f"No JSON files (ending with '.json') found in {args.input_dir}")
        return

    start_time = time.time()
    await process_tools_files(input_files, args.output_file, args.multiplier, args.obscure)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
