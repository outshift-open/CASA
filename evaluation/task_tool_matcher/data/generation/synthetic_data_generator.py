"""Dataset generation for task-tool matching evaluation, simulates tool selector.

This module generates synthetic data entries for evaluating task-tool matching algorithms.
"""

import argparse
import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict:
    """Load and validate configuration from JSON file."""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    required_keys = ["mcp_servers", "num_correct_matches", "ratio_wrong_matches", "ratio_null_matches"]
    if not all(key in config for key in required_keys):
        raise ValueError(f"Missing required configuration keys in {config_path}")

    return config


def load_mcp_tools(mcp_server_names: List[str]) -> Dict[str, List[str]]:
    """Load all tools for each MCP server (hashed)."""
    mcp_to_tools = {}
    for server_name in mcp_server_names:
        file_path = Path(f"evaluation/task_tool_matcher/data/mcp_servers/{server_name.replace('-', '_')}.json")
        if not file_path.exists():
            raise FileNotFoundError(f"MCP server file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            server_data = json.load(f)
            mcp_to_tools[server_name] = [tool["name"] for tool in server_data["tools"]]
    return mcp_to_tools


def create_task_collection(input_path: str) -> List[Dict[str, Any]]:
    """Load generated tasks and create a flat list of tasks with their metadata."""
    tasks_file = Path(input_path)
    if not tasks_file.exists():
        raise FileNotFoundError(f"Generated tasks file not found: {tasks_file}")

    with open(tasks_file, "r", encoding="utf-8") as f:
        tasks_data = json.load(f)

    all_tasks = []
    for item in tasks_data:
        for task in item.get("synthetic_tasks", []):
            all_tasks.append(
                {
                    "task": task,
                    "correct_tools": item["tool_names"],
                    "mcp_servers": item["mcp_servers"],
                }
            )

    print(f"\nLoaded a total of {len(all_tasks)} tasks from {input_path}")
    print(f"-- System prompt tag: {tasks_data[0]['system_prompt']}")
    print(f"-- Tools per task:    {tasks_data[0]['tools_per_task']}")
    print(f"-- Structured output: {tasks_data[0]['SO_tasks_per_sample']} tasks per tool")
    print(f"-- Conversation mode: {tasks_data[0]['conversation']}\n")

    return all_tasks


def generate_matches(all_tasks: List[Dict[str, Any]], config: Dict, mcp_tools: Dict[str, List[str]]) -> List[Dict]:
    """Generate correct, wrong, and null matches with a flexible sampling strategy."""
    num_correct = config["num_correct_matches"]
    num_wrong = int(num_correct * config["ratio_wrong_matches"])
    num_null = int(num_correct * config["ratio_null_matches"])

    generated_entries = []

    if len(all_tasks) < num_correct:
        raise ValueError(f"Not enough unique tasks ({len(all_tasks)}) to generate {num_correct} correct matches.")
    correct_tasks = random.sample(all_tasks, k=num_correct)

    for task in correct_tasks:
        generated_entries.append(
            {
                "input": {
                    "task": task["task"],
                    "requested_tools": task["correct_tools"],
                    "mcp_servers": task["mcp_servers"],
                },
                "groundtruth": {
                    "tools": task["correct_tools"],
                    "mcp_servers": task["mcp_servers"],
                },
                "match_tag": "correct",
            }
        )

    if num_wrong > 0:
        remaining = num_wrong
        coverage = num_wrong // len(all_tasks)
        wrong_tasks_base = []
        if coverage > 0:
            wrong_tasks_base = [task for _ in range(coverage) for task in all_tasks]
            remaining = num_wrong - len(wrong_tasks_base)
        wrong_tasks_base.extend(random.sample(all_tasks, k=remaining))

        for task in wrong_tasks_base:
            possible_wrong_tools = [t for t in mcp_tools[task["mcp_servers"][0]] if not t in task["correct_tools"]]
            if not possible_wrong_tools:
                raise ValueError(
                    f"Not enough tools in MCP server '{task['mcp_servers'][0]}' to create a wrong match for task '{task['task']}'."
                )
            wrong_tools = random.sample(possible_wrong_tools, k=len(task["correct_tools"]))

            generated_entries.append(
                {
                    "input": {
                        "task": task["task"],
                        "requested_tools": wrong_tools,
                        "mcp_servers": task["mcp_servers"],
                    },
                    "groundtruth": {
                        "requested_tools": task["correct_tools"],
                        "mcp_servers": task["mcp_servers"],
                    },
                    "match_tag": "wrong",
                }
            )

    if num_null > 0:
        remaining = num_null
        coverage = num_null // len(all_tasks)
        null_tasks_base = []
        if coverage > 0:
            null_tasks_base = [task for _ in range(coverage) for task in all_tasks]
            remaining = num_null - len(null_tasks_base)
        null_tasks_base.extend(random.sample(all_tasks, k=remaining))

        mcp_list = list(mcp_tools.keys())
        other_mcps_hash = {mcp: [other for other in mcp_list if other != mcp] for mcp in mcp_list}

        for task in null_tasks_base:
            possible_other_mcps = other_mcps_hash.get(task["mcp_servers"][0], [])
            if not possible_other_mcps:
                raise ValueError(f"Not enough other MCP servers to create a null match for task '{task['task']}'.")

            wrong_mcp = random.choice(possible_other_mcps)
            wrong_mcp_tools = mcp_tools[wrong_mcp]
            wrong_tools = random.sample(wrong_mcp_tools, k=len(task["correct_tools"]))

            generated_entries.append(
                {
                    "input": {
                        "task": task["task"],
                        "requested_tools": wrong_tools,
                        "mcp_servers": [wrong_mcp * len(wrong_tools)],
                    },
                    "groundtruth": {
                        "requested_tools": task["correct_tools"],
                        "mcp_servers": task["mcp_servers"],
                    },
                    "match_tag": "null",
                }
            )

    return generated_entries


def generate_tool_requests_data(config_path: str, input_path: str, output_path: str) -> list[dict]:
    """Simulate data of tool requests from tasks, parametrized by config.

    Args:
        config_path: Path to the configuration file (can have separate ones for validation/testing).
        input_path: Path to the input JSON file with the synthetic task(s) per MCP tool.
        output_path: Path to the output JSON file where simulated matches will be saved.
    Outputs:

    """
    config = load_config(config_path)
    all_tasks = create_task_collection(input_path)

    if not all_tasks:
        raise ValueError("No tasks were loaded. Aborting generation.")

    mcp_to_tools = load_mcp_tools(config["mcp_servers"])
    generated_data = generate_matches(all_tasks, config, mcp_to_tools)

    output_path_mod = Path(output_path)
    output_path_mod.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path_mod, "w", encoding="utf-8") as f:
        json.dump(generated_data, f, indent=2)

    logger.info(f"Successfully generated {len(generated_data)} simulated tool requests.")
    num_correct = config["num_correct_matches"]
    num_wrong = int(num_correct * config["ratio_wrong_matches"])
    num_null = int(num_correct * config["ratio_null_matches"])

    logger.info(
        f"Generation summary: \nCorrect={num_correct}, Wrong={num_wrong}, Null={num_null}. \nSaved to {output_path}\n"
    )

    return generated_data


def main():
    """Main function to run the simulated pair data generation script."""
    parser = argparse.ArgumentParser(description="Generate task-tool matching evaluation data.")
    parser.add_argument(
        "--config",
        default="evaluation/task_tool_matcher/data/generation/config.json",
        help="Path to the configuration file (can have separate ones for validation/testing).",
    )
    parser.add_argument(
        "--input",
        default="evaluation/task_tool_matcher/data/DEL.json",
        help="Path to the input JSON file with the synthetic task(s) per MCP tool.",
    )
    parser.add_argument(
        "--output",
        default="evaluation/task_tool_matcher/data/generated_data.json",
        help="Path to the output JSON file where simulated matches will be saved.",
    )
    args = parser.parse_args()

    _ = generate_tool_requests_data(config_path=args.config, input_path=args.input, output_path=args.output)


if __name__ == "__main__":
    main()
