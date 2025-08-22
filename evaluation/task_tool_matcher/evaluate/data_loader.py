"""Data loading utilities for evaluation."""

import gzip
import json
import os
from typing import List

from evaluation.task_tool_matcher.types import EvaluateEntryTaskToolMatcher


def load_evaluation_data(file_path: str) -> List[EvaluateEntryTaskToolMatcher]:
    """Load evaluation data from JSON or compressed JSON file.

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

    return [EvaluateEntryTaskToolMatcher(**entry) for entry in data]


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
