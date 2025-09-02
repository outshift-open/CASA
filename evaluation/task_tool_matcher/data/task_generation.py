"""Synthetic generation of tasks corresponding to (MCP) tool descriptions provided in JSONs."""

import argparse
import asyncio
import json
import time

from dotenv import dotenv_values
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm

config = dotenv_values()

client = AsyncOpenAI(
    api_key=config.get("OPENAI_API_KEY"),
    base_url=config.get("OPENAI_API_BASE_URL"),
)


SYSTEM_PROMPT_TEMPLATE = """You are an expert scenario designer. Your specialty is creating realistic and detailed user task requests that require a certain tool to execute them (you are given the tool, and you generate a corresponding task).

Your goal is therefore to generate a **single, high-quality user request**. This request must be a realistic command, and it must require the use of the specific tool provided to you.

You are given the following information about the tool, as shown below:

**Tool Name:**
`[Tool Name]`

**Tool Description:**
`[Tool Description]`

**Input Schema:**
```json
[Input Schema]
```

### Your Instructions:

1.  **Be Specific and Realistic:** Do not use generic placeholders. Invent plausible details that look real and coherent. For example, use `'bug-fix/login-error'` instead of `'a branch name'`, `'PROJ-456'` instead of `'an issue key'`, and `'our Q3 marketing campaign'` instead of `'a project summary'`.

2.  **Map to Inputs:** The generated request must implicitly provide all the necessary values for the `required` parameters in the `Input Schema`. You can also include values for optional parameters to make the task more realistic and detailed.

3.  **Natural Language Only:** The output must be a single fluid sentence or two, and it must be a realistic task. It should **not** be a list of parameters or a JSON object.

4.  **Focus on the User's Goal:** The request should describe what the user wants to *achieve*, not how the tool works. The tool is needed for the *solution* to the user's request.

### Output Format:

Your response must contain **ONLY** the generated request text and nothing else. Do not add any explanations, preambles, or markdown formatting."""


OBSCURE_SYSTEM_PROMPT_TEMPLATE = """You are an expert scenario designer. Your specialty is creating realistic and detailed user task requests that require a certain tool to execute them (you are given the tool, and you generate a corresponding task).

Your goal is to generate a **single, high-quality user request**. This request must be a realistic command that would require the use of the specific tool provided to you to complete it, but it should require it in a somewhat **obscure or implicit or indirect** way, **not** directly ask for the tool. This means that the connection between the task and the tool should **not** be immediately obvious.

You are given the following information about the tool, as shown below:

**Tool Name:**
`[Tool Name]`

**Tool Description:**
`[Tool Description]`

### Your Instructions:

1.  **Be Specific and Realistic:** Do not use generic placeholders. Invent plausible details that look real and coherent. For example, use `'bug-fix/login-error'` instead of `'a branch name'`, `'PROJ-456'` instead of `'an issue key'`, and `'our Q3 marketing campaign'` instead of `'a project summary'`.

2.  **Natural Language Only:** The output must be a single fluid sentence or two, and it must be a realistic task. It should **not** be a list of parameters or a JSON object.

3.  **Focus on the User's Goal:** The request should describe what the user wants to *achieve*, not how the tool works. The tool is needed for the *solution* to the user's request, but the user does **not** directly request it. Make the user's intent the primary focus, with the need for the tool being a secondary inference.

### Output Format:

Your response must contain **ONLY** the generated request text and nothing else. Do not add any explanations, preambles, or markdown formatting."""


async def task_synthesizer(tool_data: dict, semaphore: asyncio.Semaphore, obscure: bool) -> dict | None:
    """Synthesizes tasks based on the description of a single MCP tool, with a generative model.

    Args:
        tool_data (dict): A dictionary with 'name', 'description', and 'inputSchema of MCP tools.
        semaphore (asyncio.Semaphore): To limit concurrent API calls to openai.
        obscure (bool): Whether to generate an obscure task or regular.

    Returns:
        A dictionary with the tool_name and generated task, or None on failure.
    """
    system_prompt_template = OBSCURE_SYSTEM_PROMPT_TEMPLATE if obscure else SYSTEM_PROMPT_TEMPLATE

    tool_description = tool_data.get("description", "N/A")
    if obscure:
        cut_sequence = "\n    Args:\n"  # cutting off input args info (applies to atlassian & hummingbot & paper-search)
        if cut_sequence in tool_description:
            tool_description = tool_description.split(cut_sequence)[0]
        cut_sequence = "\n\nParameters:\n"  # cutting off input args information (applies to nasdaq)
        if cut_sequence in tool_description:
            tool_description = tool_description.split(cut_sequence)[0]

    system_prompt = system_prompt_template.replace("[Tool Name]", tool_data.get("name", "N/A"))
    system_prompt = system_prompt.replace("[Tool Description]", tool_description)

    if not obscure:
        system_prompt = system_prompt.replace("[Input Schema]", json.dumps(tool_data.get("inputSchema", {}), indent=2))
    elif "[Input Schema]" in system_prompt:
        system_prompt = system_prompt.replace("[Input Schema]", "")

    user_prompt = "Execute the user request and generate the corresponding output."

    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            )
            synthetic_task = response.choices[0].message.content
            return {
                "tool_name": tool_data.get("name"),
                "synthetic_task": synthetic_task,
                "system_prompt": system_prompt,
            }
        except Exception as e:
            print(f"Error processing tool {tool_data.get('name', 'N/A')}: {e}")
            return None


async def process_tools_files(input_paths: list[str], output_path: str, multiplier: int, obscure: bool):
    """Reads tools from JSON files, creates their tasks in parallel, and saves the results in dict."""
    all_tools = []
    for input_path in input_paths:
        with open(input_path, "r") as f:
            tools = json.load(f)
            all_tools.extend(tools)

    semaphore = asyncio.Semaphore(10)  # max 10 for openai async

    tasks = []
    for tool in all_tools:
        for _ in range(multiplier):
            tasks.append(task_synthesizer(tool, semaphore, obscure))

    results = await tqdm.gather(*tasks)

    grouped_results = {}  # to regroup results by tool name
    for res in results:
        if res is None:
            continue
        tool_name = res["tool_name"]
        if tool_name not in grouped_results:
            grouped_results[tool_name] = {
                "tool_name": tool_name,
                "synthetic_tasks": [],
                "system_prompt": res["system_prompt"],
            }
        grouped_results[tool_name]["synthetic_tasks"].append(res["synthetic_task"])

    final_results = list(grouped_results.values())

    with open(output_path, "w") as f:
        json.dump(final_results, f, indent=2)

    total_requested = len(all_tools) * multiplier
    total_successful = sum(len(res.get("synthetic_tasks", [])) for res in final_results)
    print(
        f"Successfully created {total_successful} out of {total_requested} requested synthetic tasks for {len(final_results)} tools."
    )


async def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(description="Generate synthetic tasks from a JSON file of MCP tool descriptions.")
    parser.add_argument(
        "--input-files", nargs="+", required=True, help="Paths to the input JSON files with the MCP tool descriptions."
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

    start_time = time.time()
    await process_tools_files(args.input_files, args.output_file, args.multiplier, args.obscure)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
