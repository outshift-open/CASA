"""Dataset generation for task-tool matching evaluation.

This module generates synthetic data entries for evaluating task-tool matching algorithms.
It creates realistic task descriptions and pairs them with appropriate MCP tools.
"""

import argparse
import gzip
import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional

from mcp import types as mcp_types

from evaluation.task_tool_matcher.types import EvaluateEntryTaskToolMatcher
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchInput
from identity_auth_server.types import McpServer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _generate_task_description(
    tools: List[mcp_types.Tool],
    config: Dict,
    requested_tool: Optional[str] = None,
    match_type: str = "match",
    correct_tool: Optional[str] = None,
) -> str:
    """Generate a realistic task description based on available tools and match type.

    Args:
        tools: List of available MCP tools
        config: Configuration dictionary
        requested_tool: Optional specific tool to generate task for
        match_type: Type of match (match, wrong_tool, no_tool)
        correct_tool: For wrong_tool cases, the tool that should actually be used

    Returns:
        Generated task description string
    """
    # Load tasks from generated_tasks.json
    tasks_file = Path("evaluation/task_tool_matcher/data/generated_tasks.json")
    if not tasks_file.exists():
        logger.warning(f"Generated tasks file not found: {tasks_file}")
        return _fallback_task_description(match_type, config)

    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load generated tasks: {e}")
        return _fallback_task_description(match_type, config)

    # Create a mapping from tool name to tasks
    tool_tasks_map = {item["tool_name"]: item["synthetic_tasks"] for item in tasks_data}

    # Generate task based on match type
    if match_type == "match" and requested_tool:
        # Randomly pick from tasks for the requested tool
        if tool_tasks_map.get(requested_tool):
            return random.choice(tool_tasks_map[requested_tool])
    elif match_type == "wrong_tool" and correct_tool:
        # Randomly pick from tasks for the correct tool (not the requested one)
        if tool_tasks_map.get(correct_tool):
            return random.choice(tool_tasks_map[correct_tool])
    elif match_type == "no_tool":
        # Generate generic messages that have nothing to do with tools
        no_tool_tasks = [
            "Tell me a funny joke about cats and dogs",
            "What's the weather forecast for next week?",
            "Explain the theory of relativity in simple terms",
            "Write a haiku about the ocean at sunset",
            "What's 247 multiplied by 83?",
            "Translate 'good morning' to French and German",
            "What are some good book recommendations for summer reading?",
            "How do I make the perfect chocolate chip cookies?",
            "What's the history of the Renaissance period?",
            "Give me some tips for staying motivated while exercising",
        ]
        return random.choice(no_tool_tasks)

    # Fallback if specific tool tasks not found
    return _fallback_task_description(match_type, config)


def _fallback_task_description(match_type: str, config: Dict) -> str:
    """Fallback task description generation when generated_tasks.json is unavailable.

    Args:
        match_type: Type of match (match, wrong_tool, no_tool)
        config: Configuration dictionary

    Returns:
        Generated fallback task description string
    """
    if match_type == "no_tool":
        no_tool_tasks = [
            "Tell me a funny joke about cats and dogs",
            "What's the weather forecast for next week?",
            "Explain the theory of relativity in simple terms",
            "Write a haiku about the ocean at sunset",
            "What's 247 multiplied by 83?",
            "Translate 'good morning' to French and German",
            "What are some good book recommendations for summer reading?",
            "How do I make the perfect chocolate chip cookies?",
            "What's the history of the Renaissance period?",
            "Give me some tips for staying motivated while exercising",
        ]
        return random.choice(no_tool_tasks)

    # Fallback to generic task descriptions
    generic_tasks = [
        "Help me manage my project tasks",
        "I need to organize my workflow",
        "Assist with data retrieval and analysis",
        "Help me automate routine operations",
        "Support my development workflow",
        "Help me track and manage issues",
        "Assist with content creation and editing",
        "Help me integrate different systems",
    ]

    task = random.choice(generic_tasks)

    # Respect character limit from config
    max_length = config.get("task_character_limit", 150)
    if len(task) > max_length:
        task = task[: max_length - 3] + "..."

    return task


def _select_tools_by_distribution(tools: List[mcp_types.Tool], config: Dict) -> tuple[List[str], Optional[str], str]:
    """Select available tools and requested tool based on match distribution.

    Args:
        tools: List of available MCP tools
        config: Configuration dictionary containing match distribution

    Returns:
        Tuple of (available_tools, requested_tool, match_type)
    """
    if not tools:
        return [], None, "no_tool"

    tool_names = [tool.name for tool in tools]
    max_available = min(len(tools), config.get("available_tools_per_task", 5))

    # Select available tools (at least 2 if tools exist)
    # If less than 2 tools exist, then wrong tool case is not possible
    num_available = random.randint(2, max_available)
    available_tools = random.sample(tool_names, k=num_available)

    # Determine match type based on distribution
    distribution = config.get("match_distribution", {"match": 0.4, "wrong_tool": 0.4, "no_tool": 0.2})
    rand = random.random()

    cumulative_prob = 0
    match_type = "match"  # default

    for match_type_key, prob in distribution.items():
        cumulative_prob += prob
        if rand <= cumulative_prob:
            match_type = match_type_key
            break

    # Select requested tool based on match type
    if match_type == "no_tool":
        # For no_tool cases, we still need to provide a tool since the model doesn't allow None
        # We'll select a random tool but the task generation should reflect that it doesn't match
        requested_tool = random.choice(available_tools)
        logger.debug(f"Generated 'no_tool' case with tool: {requested_tool}")
    elif match_type == "match":
        # Tool should be in available tools
        requested_tool = random.choice(available_tools)
    elif match_type == "wrong_tool":
        # Tool will be in available tools but shouldn't match the task
        requested_tool = random.choice(available_tools)
    else:
        requested_tool = random.choice(available_tools) if available_tools else None

    return available_tools, requested_tool, match_type


def generate_data_entry(mcp_server: McpServer, config: Dict) -> EvaluateEntryTaskToolMatcher:
    """Generate a single data entry for task-tool matching evaluation.

    Args:
        mcp_server: Description of the MCP Server (name, tools, resources)
        config: Configuration dictionary

    Returns:
        EvaluateEntryTaskToolMatcher instance with generated data

    Raises:
        ValueError: If tools list is empty or if requested_tool is None
    """
    if not mcp_server.tools or len(mcp_server.tools) == 0:
        raise ValueError("Cannot generate data entry: tools list is empty")

    # Select tools based on distribution configuration
    available_tools, requested_tool, match_type = _select_tools_by_distribution(mcp_server.tools, config)

    # Ensure requested_tool is not None (required by the model)
    if requested_tool is None:
        requested_tool = random.choice(available_tools) if available_tools else mcp_server.tools[0].name

    # Determine correct choice and match based on match type
    if match_type == "match":
        correct_choice = requested_tool
        match = True
    elif match_type == "no_tool":
        correct_choice = None
        match = False
    else:  # wrong_tool
        # The requested tool is wrong, so the correct choice should be a different available tool
        # This ensures requested_tool and correct_choice never match when distribution is "wrong_tool"
        other_tools = [tool for tool in available_tools if tool != requested_tool]
        if other_tools:
            correct_choice = random.choice(other_tools)
        else:
            # If no other tools available, treat as no_tool case
            correct_choice = None
        match = False

    # Generate task description based on match type (pass correct_choice for wrong_tool cases)
    task_description = _generate_task_description(mcp_server.tools, config, requested_tool, match_type, correct_choice)

    # Create the input object
    task_input = TaskToolMatchInput(
        task=task_description, requested_tool=requested_tool, mcp_server=mcp_server, available_tools=available_tools
    )

    # Create the evaluation entry
    entry = EvaluateEntryTaskToolMatcher(input=task_input, correct_choice=correct_choice, match=match)

    return entry


def _load_config(config_path: str) -> Dict:
    """Load and validate configuration from JSON file.

    Args:
        config_path: Path to configuration JSON file

    Returns:
        Parsed configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file contains invalid JSON
        ValueError: If required config keys are missing
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Validate required configuration keys
    required_keys = ["mcp_servers", "num_entries_per_server"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")

    # Set defaults for optional keys
    config.setdefault("available_tools_per_task", 5)
    config.setdefault("task_character_limit", 150)
    config.setdefault("match_distribution", {"match": 0.4, "wrong_tool": 0.4, "no_tool": 0.2})

    return config


def _load_mcp_server(server_name: str) -> McpServer:
    """Load MCP Server description from server JSON file.

    Args:
        server_name: Name of the MCP server

    Returns:
        MCP Server description (name, tools, resources)

    Raises:
        FileNotFoundError: If server file doesn't exist
        json.JSONDecodeError: If server file contains invalid JSON
    """
    file_path = Path("evaluation/task_tool_matcher/data/mcp_servers") / f"{server_name}.json"

    if not file_path.exists():
        raise FileNotFoundError(f"MCP server tools file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        mcp_server = json.load(f)

    # Cast to McpServer
    mcp_server = McpServer(**mcp_server)

    logger.info(f"Loaded {len(mcp_server.tools)} tools from {server_name}")

    return mcp_server


def _print_distribution_analysis(distribution_counts: Dict[str, int], config: Dict, total_entries: int) -> None:
    """Print distribution analysis comparing expected vs actual distributions.

    Args:
        distribution_counts: Dictionary with actual counts for each distribution type
        config: Configuration dictionary containing expected distribution
        total_entries: Total number of entries generated
    """
    if total_entries == 0:
        logger.warning("No entries to analyze")
        return

    # Calculate actual percentages
    actual_match_pct = (distribution_counts["match"] / total_entries) * 100
    actual_wrong_tool_pct = (distribution_counts["wrong_tool"] / total_entries) * 100
    actual_no_tool_pct = (distribution_counts["no_tool"] / total_entries) * 100

    # Get expected distributions from config
    expected_dist = config.get("match_distribution", {"match": 0.4, "wrong_tool": 0.4, "no_tool": 0.2})
    expected_match_pct = expected_dist.get("match", 0.0) * 100
    expected_wrong_tool_pct = expected_dist.get("wrong_tool", 0.0) * 100
    expected_no_tool_pct = expected_dist.get("no_tool", 0.0) * 100

    # Print distribution analysis
    print("\n" + "=" * 60)
    print("DISTRIBUTION ANALYSIS")
    print("=" * 60)
    print(f"Total entries generated: {total_entries}")
    print()

    print("EXPECTED vs ACTUAL DISTRIBUTIONS:")
    print("-" * 40)
    print(f"{'Type':<12} {'Expected':<12} {'Actual':<12} {'Count':<8} {'Diff'}")
    print("-" * 40)

    match_diff = actual_match_pct - expected_match_pct
    wrong_tool_diff = actual_wrong_tool_pct - expected_wrong_tool_pct
    no_tool_diff = actual_no_tool_pct - expected_no_tool_pct

    print(
        f"{'Match':<12} {expected_match_pct:>6.1f}% {actual_match_pct:>10.1f}% {distribution_counts['match']:>6} {match_diff:>+6.1f}%"
    )
    print(
        f"{'Wrong Tool':<12} {expected_wrong_tool_pct:>6.1f}% {actual_wrong_tool_pct:>10.1f}% {distribution_counts['wrong_tool']:>6} {wrong_tool_diff:>+6.1f}%"
    )
    print(
        f"{'No Tool':<12} {expected_no_tool_pct:>6.1f}% {actual_no_tool_pct:>10.1f}% {distribution_counts['no_tool']:>6} {no_tool_diff:>+6.1f}%"
    )

    print("-" * 40)
    print(
        f"{'TOTAL':<12} {'100.0%':<12} {actual_match_pct + actual_wrong_tool_pct + actual_no_tool_pct:>6.1f}% {total_entries:>6}"
    )

    print("\nNOTE: Distributions are based on random sampling and may vary from expected percentages.")
    print("=" * 60)


def _compress_file(file_path: Path) -> Path:
    """Compress a file using gzip compression.

    Args:
        file_path: Path to the file to compress

    Returns:
        Path to the compressed file

    Raises:
        OSError: If compression fails
    """
    compressed_path = file_path.with_suffix(file_path.suffix + ".gz")

    try:
        with open(file_path, "rb") as f_in:
            with gzip.open(compressed_path, "wb") as f_out:
                f_out.write(f_in.read())

        # Get file sizes for logging
        original_size = file_path.stat().st_size
        compressed_size = compressed_path.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100

        logger.info("File compressed successfully:")
        logger.info(f"  Original size: {original_size:,} bytes")
        logger.info(f"  Compressed size: {compressed_size:,} bytes")
        logger.info(f"  Compression ratio: {compression_ratio:.1f}%")
        logger.info(f"  Compressed file: {compressed_path}")

        # Remove original file to save space
        file_path.unlink()
        logger.info(f"Original file removed: {file_path}")

        return compressed_path

    except OSError as e:
        logger.error(f"Failed to compress file {file_path}: {e}")
        raise


def decompress_generated_data(compressed_path: str) -> List[Dict]:
    """Decompress and load generated data from a gzipped JSON file.

    Args:
        compressed_path: Path to the compressed JSON file

    Returns:
        List of dictionaries containing the generated data

    Raises:
        FileNotFoundError: If compressed file doesn't exist
        gzip.BadGzipFile: If file is not a valid gzip file
        json.JSONDecodeError: If decompressed content is not valid JSON
    """
    compressed_file = Path(compressed_path)

    if not compressed_file.exists():
        raise FileNotFoundError(f"Compressed file not found: {compressed_path}")

    try:
        with gzip.open(compressed_file, "rt", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"Successfully loaded {len(data)} entries from compressed file: {compressed_path}")
        return data

    except (gzip.BadGzipFile, json.JSONDecodeError) as e:
        logger.error(f"Failed to decompress/parse file {compressed_path}: {e}")
        raise


def generate_data(config_path: str, compress_output: bool = True) -> None:
    """Generate task-tool matching data based on the provided configuration.

    Args:
        config_path: Path to the configuration JSON file
        compress_output: Whether to compress the output file using gzip

    Raises:
        FileNotFoundError: If config file or MCP server files don't exist
        json.JSONDecodeError: If JSON files contain invalid data
        ValueError: If configuration is invalid
    """
    logger.info(f"Loading configuration from {config_path}")

    try:
        config = _load_config(config_path)
        logger.info(
            f"Configuration loaded successfully: {len(config.get('mcp_servers', []))} servers, "
            f"{config.get('num_entries_per_server')} entries per server"
        )
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

    entries = []
    servers_processed = 0

    # Track distributions during generation
    distribution_counts = {"match": 0, "wrong_tool": 0, "no_tool": 0}

    for server_name in config.get("mcp_servers", []):
        logger.info(f"Processing MCP server: {server_name}")

        try:
            mcp_server = _load_mcp_server(server_name)

            if not mcp_server.tools or len(mcp_server.tools) == 0:
                logger.warning(f"No tools found for server {server_name}, skipping")
                continue

            # Generate data entries for this server
            server_entries = []
            for i in range(config.get("num_entries_per_server", 0)):
                try:
                    entry = generate_data_entry(mcp_server, config)
                    server_entries.append(entry)

                    # Track the distribution type for this entry
                    if entry.match:
                        distribution_counts["match"] += 1
                    elif entry.correct_choice is not None:
                        distribution_counts["wrong_tool"] += 1
                    else:
                        distribution_counts["no_tool"] += 1

                except ValueError as e:
                    logger.error(f"Failed to generate entry {i + 1} for {server_name}: {e}")
                    continue

            entries.extend(server_entries)
            servers_processed += 1
            logger.info(f"Generated {len(server_entries)} entries for {server_name}")

        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to process server {server_name}: {e}")
            continue

    if not entries:
        logger.error("No data entries were generated")
        return

    # Save generated entries to JSON file
    output_path = Path("evaluation/task_tool_matcher/data/generated_data.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([entry.model_dump() for entry in entries], f, indent=2)

        logger.info(f"Successfully generated {len(entries)} entries from {servers_processed} servers")
        logger.info(f"Data saved to: {output_path}")

        # Compress the output file if requested
        if compress_output:
            logger.info("Compressing output file...")
            compressed_path = _compress_file(output_path)
            logger.info(f"Final compressed output: {compressed_path}")

        # Print distribution analysis
        _print_distribution_analysis(distribution_counts, config, len(entries))

    except (OSError, IOError) as e:
        logger.error(f"Failed to save generated data: {e}")
        raise


def main() -> None:
    """Main function to run the generation script."""
    parser = argparse.ArgumentParser(description="Generate task-tool matching evaluation data")
    parser.add_argument(
        "--no-compress", action="store_true", help="Skip compression of the output file (default: compress with gzip)"
    )
    parser.add_argument(
        "--config",
        default="evaluation/task_tool_matcher/data/generation/config.json",
        help="Path to the configuration file (default: evaluation/task_tool_matcher/data/generation/config.json)",
    )

    args = parser.parse_args()
    compress_output = not args.no_compress

    try:
        generate_data(args.config, compress_output=compress_output)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise


if __name__ == "__main__":
    main()
