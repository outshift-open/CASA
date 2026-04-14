"""Data loading utilities for evaluation."""

import gzip
import json
import logging
import os
from pathlib import Path
from typing import List

from evaluation.task_tool_matcher.types import (
    EvaluateEntryTaskToolMatcher,
    EvaluateGroundTruthTaskToolMatcher,
    EvaluateInput,
)
from identity_auth_server.types import McpServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_mcp_servers() -> dict[str, McpServer]:
    """Load MCP Server data from server JSON file."""
    config_path = Path("evaluation/task_tool_matcher/data/generation/config.json")
    mcp_servers_path = Path("evaluation/task_tool_matcher/data/mcp_servers")

    if not config_path.exists():
        raise FileNotFoundError(f"Data creation config file not found: {config_path}")
    if not mcp_servers_path.exists():
        raise FileNotFoundError(f"MCP server tools file not found: {mcp_servers_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    mcp_servers = {}
    for server_name in config.get("mcp_servers", []):
        logger.info(f"Processing MCP server: {server_name}")
        server_name = server_name.replace("-", "_")
        with open(mcp_servers_path / f"{server_name}.json", "r", encoding="utf-8") as f:
            mcp_server = json.load(f)
            mcp_servers[mcp_server["name"]] = McpServer(**mcp_server)

    return mcp_servers


def load_evaluation_data(file_path: str) -> List[EvaluateEntryTaskToolMatcher]:
    """Load evaluation data from JSON or compressed JSON file.

    Hypothesis: Each entry contains one task and one requested tool. Even if support for multiple tools is available,
    the current evaluation dataset is one task - one tool.

    Args:
        file_path: Path to the JSON or .json.gz file

    Returns:
        List of evaluation entries

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Evaluation data file not found: {file_path}")

    if file_path.endswith(".gz"):
        with gzip.open(file_path, "rt", encoding="utf-8") as f:
            data = json.load(f)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    mcp_servers = load_mcp_servers()
    eval_data: List[EvaluateEntryTaskToolMatcher] = []
    for entry in data:
        requested_mcp_servers_data = []
        for requested_server in entry["input"]["mcp_servers"]:
            requested_mcp_servers_data.append(mcp_servers[requested_server])
        eval_data.append(
            EvaluateEntryTaskToolMatcher(
                input=EvaluateInput(
                    task=entry["input"]["task"],
                    requested_tools=entry["input"]["tools"],
                    requested_mcp_servers=requested_mcp_servers_data,
                ),
                groundtruth=EvaluateGroundTruthTaskToolMatcher(
                    tools=entry["groundtruth"]["tools"],
                    mcp_servers=entry["groundtruth"]["mcp_servers"],
                ),
                match_tag=entry["match_tag"],
            )
        )
    return eval_data


def find_evaluation_data_file() -> str:
    """Find the evaluation data file, preferring compressed version.

    Returns:
        Path to the evaluation data file

    Raises:
        FileNotFoundError: If no evaluation data file is found
    """
    data_dir = "evaluation/task_tool_matcher/data"
    compressed_file = os.path.join(data_dir, "generated_data.json.gz")
    regular_file = os.path.join(data_dir, "generated_data.json")

    if os.path.exists(compressed_file):
        print(f"Found compressed evaluation data: {compressed_file}")
        return compressed_file
    elif os.path.exists(regular_file):
        print(f"Found regular evaluation data: {regular_file}")
        return regular_file
    else:
        raise FileNotFoundError(f"No evaluation data file found. Expected: {compressed_file} or {regular_file}")
