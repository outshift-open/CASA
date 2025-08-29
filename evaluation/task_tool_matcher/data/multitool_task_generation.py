"""Synthetic generation of tasks corresponding to a combination of (MCP) tool descriptions provided in JSONs."""

import argparse
import asyncio
import json
import random
import time

from dotenv import dotenv_values
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm

config = dotenv_values()

client = AsyncOpenAI(
    api_key=config.get("OPENAI_API_KEY"),
    base_url=config.get("OPENAI_API_BASE_URL"),
)


SYSTEM_PROMPT_TEMPLATE = """You are an expert scenario designer. Your specialty is creating realistic and detailed user task requests that require a tool or a combination of tools to execute them (you are given the tools, and you generate a corresponding task).

Your goal is therefore to generate a **single, high-quality user request**. This request must be a realistic command, and it must require the use of the specific tool(s) provided to you.

You are given the following information about the tool(s), as shown below:

---
[Tool Details]
---

### Your Instructions:

1.  **Be Specific and Realistic:** Do not use generic placeholders. Invent plausible details that look real and coherent. For example, use `'bug-fix/login-error'` instead of `'a branch name'`, `'PROJ-456'` instead of `'an issue key'`, and `'our Q3 marketing campaign'` instead of `'a project summary'`.

2.  **Map to Inputs:** The generated request must implicitly provide all the necessary values for the `required` parameters in the `Input Schema` of all the tools. You can also include values for optional parameters to make the task more realistic and detailed.

3.  **Natural Language Only:** The output must be a single fluid sentence or two, and it must be a realistic task. It should **not** be a list of parameters or a JSON object.

4.  **Focus on the User's Goal:** The request should describe what the user wants to *achieve*, not how the tool works. The tools are needed for the *solution* to the user's request.

### Output Format:

Your response must contain **ONLY** the generated request text and nothing else. Do not add any explanations, preambles, or markdown formatting."""


OBSCURE_SYSTEM_PROMPT_TEMPLATE = """You are an expert scenario designer. Your specialty is creating realistic and detailed user task requests that require a tool or a combination of tools to execute them (you are given the tools, and you generate a corresponding task).

Your goal is to generate a **single, high-quality user request**. This request must be a realistic command that would require the use of the specific tool(s) provided to you to complete it, but it should require them in a somewhat **obscure or implicit or indirect** way, **not** directly ask for the tools. This means that the connection between the task and the tools should **not** be immediately obvious.

You are given the following information about the tool(s), as shown below:

---
[Tool Details]
---

### Your Instructions:

1.  **Be Specific and Realistic:** Do not use generic placeholders. Invent plausible details that look real and coherent. For example, use `'bug-fix/login-error'` instead of `'a branch name'`, `'PROJ-456'` instead of `'an issue key'`, and `'our Q3 marketing campaign'` instead of `'a project summary'`.

2.  **Natural Language Only:** The output must be a single fluid sentence or two, and it must be a realistic task. It should **not** be a list of parameters or a JSON object.

3.  **Focus on the User's Goal:** The request should describe what the user wants to *achieve*, not how the tool works. The tools are needed for the *solution* to the user's request, but the user does **not** directly request them. Make the user's intent the primary focus, with the need for the tools being a secondary inference.

### Output Format:

Your response must contain **ONLY** the generated request text and nothing else. Do not add any explanations, preambles, or markdown formatting."""


def format_tool_details(tools: list[dict], obscure: bool) -> str:
    """Formats the details of multiple tool dicts (list) for the system prompt."""
    details = []
    for tool in tools:
        tool_description = tool.get("description", "N/A")
        cut_sequence = "\n\n    Args:\n        "  # cutting off input args information (applies to atlassian tools)
        if cut_sequence in tool_description:
            tool_description = tool_description.split(cut_sequence)[0]

        tool_info = [f"**Tool Name:**\n`{tool.get('name', 'N/A')}`\n\n**Tool Description:**\n`{tool_description}`"]
        if not obscure:
            tool_info.append(
                f"\n\n**Input Schema:**\n```json\n{json.dumps(tool.get('inputSchema', {}), indent=2)}\n```"
            )
        details.append("".join(tool_info))
    return "\n\n---\n\n".join(details)


async def task_synthesizer(
    tools_data: list[dict], semaphore: asyncio.Semaphore, system_prompt_template: str, obscure: bool
) -> dict | None:
    """Synthesizes tasks based on the description of multiple MCP tools, with a generative model.

    Args:
        tools_data (list[dict]): A list of dictionaries, each with 'name', 'description', and 'inputSchema' of an MCP tool.
        semaphore (asyncio.Semaphore): To limit concurrent API calls to openai.
        system_prompt_template (str): The template of the system prompt.
        obscure (bool): Whether to generate an obscure task.

    Returns:
        A dictionary with the tool_names and generated task, or None on failure.
    """
    tool_details = format_tool_details(tools_data, obscure)
    system_prompt = system_prompt_template.replace("[Tool Details]", tool_details)

    user_prompt = "Execute the user request and generate the corresponding output."

    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            )
            synthetic_task = response.choices[0].message.content
            tool_names = [tool.get("name") for tool in tools_data]
            return {
                "tool_names": tool_names,
                "synthetic_task": synthetic_task,
                "system_prompt": system_prompt,
            }
        except Exception as e:
            tool_names_str = ", ".join([tool.get("name", "N/A") for tool in tools_data])
            print(f"Error processing tools {tool_names_str}: {e}")
            return None


async def process_tools_files(input_paths: list[str], output_path: str, multiplier: int, num_tools: int, obscure: bool):
    """Reads tools from JSON files, creates their tasks in parallel, and saves the results in dict."""
    all_tools = []
    for input_path in input_paths:
        with open(input_path, "r") as f:
            tools = json.load(f)
            all_tools.extend(tools)

    if len(all_tools) < num_tools:
        print(f"Error: Not enough tools ({len(all_tools)}) to create a task with {num_tools} tools.")
        return

    semaphore = asyncio.Semaphore(10)  # max 10 for openai async
    system_prompt_template = OBSCURE_SYSTEM_PROMPT_TEMPLATE if obscure else SYSTEM_PROMPT_TEMPLATE

    tasks = []
    for tool in all_tools:
        other_tools = [t for t in all_tools if t["name"] != tool["name"]]
        if len(other_tools) < num_tools - 1:
            raise ValueError(
                f"Not enough other tools to combine with '{tool['name']}'. "
                f"Required: {num_tools - 1}, available: {len(other_tools)}."
            )

        for _ in range(multiplier):
            random_tools = random.sample(other_tools, num_tools - 1)
            tool_group = [tool, *random_tools]
            tasks.append(task_synthesizer(tool_group, semaphore, system_prompt_template, obscure))

    results = await tqdm.gather(*tasks)
    final_results = [res for res in results if res is not None]

    with open(output_path, "w") as f:
        json.dump(final_results, f, indent=2)

    total_requested = len(all_tools) * multiplier
    total_successful = len(final_results)
    print(f"Created {total_successful} / {total_requested} requested synthetic tasks for {len(all_tools)} tools.")


async def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(description="Generate synthetic tasks from a JSON file of MCP tool descriptions.")
    parser.add_argument(
        "--input-files", nargs="+", required=True, help="Paths to the input JSON files with the MCP tool descriptions."
    )
    parser.add_argument(
        "--output-file", required=True, help="Path to the output JSON file to save the synthetic tasks (+meta info)."
    )
    parser.add_argument("--multiplier", type=int, default=1, help="Number of synthetic tasks to generate per tool.")
    parser.add_argument("--num-tools", type=int, default=1, help="Number of tools to use for each synthetic task.")
    parser.add_argument(
        "--obscure", action="store_true", help="Generate more obscure tasks (hide input schema + new sys_prompt)."
    )

    args = parser.parse_args()

    start_time = time.time()
    await process_tools_files(args.input_files, args.output_file, args.multiplier, args.num_tools, args.obscure)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds // ({elapsed_time / 60:.2f} minutes)")


if __name__ == "__main__":
    asyncio.run(main())
