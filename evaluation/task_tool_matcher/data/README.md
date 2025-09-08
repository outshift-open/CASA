# Task-Tool Matching Data Generation (Not Synthetic Task Creator)

This directory contains the data generation pipeline for creating synthetic evaluation datasets for the task-tool matching system.

## Overview

The generation system creates realistic task descriptions paired with MCP (Model Context Protocol) tools to evaluate and test task-tool matching algorithms. It generates datasets with configurable distributions of correct matches, wrong tool selections, and no-tool scenarios.

## Files

- `generation/synthetic_data_generator.py` - Main generation script that creates synthetic task-tool matching data
- `generation/config.json` - Configuration file defining generation parameters
- `generated_data.json.gz` - Compressed output file containing the generated evaluation dataset (created after running)

## Usage

### Prerequisites

Ensure you have the virtual environment activated and the project dependencies installed.

Generate the synthetic tasks dataset first, by refering to `evaluation/task_tool_matcher/data/mcp_servers/README.md`. You need to have a `generated_tasks.json` to run the matching generator.

### Generating Data

To regenerate the evaluation dataset:

```bash
# From the project root directory
source .venv/bin/activate
python -m evaluation.task_tool_matcher.data.generation.synthetic_data_generator
```

This will (up to task descriptions this is covered by prerequisites):
- Load MCP server tool definitions from the `../mcp_servers/` directory
- Generate synthetic tasks based on the configuration in `config.json`
- Create realistic task descriptions with appropriate tool matches/mismatches
- Save the generated dataset to `generated_data.json` and compress it to `generated_data.json.gz`
- Display distribution analysis comparing expected vs actual match types

### Configuration

Edit `config.json` to customize the generation process:

```json
{
    "mcp_servers": ["atlassian_tools", "github_official_tools"],
    "num_entries_per_server": 10,
    "task_character_limit": 150,
    "available_tools_per_task": 5,
    "match_distribution": {
        "match": 0.4,        // 40% correct tool matches
        "wrong_tool": 0.4,   // 40% incorrect tool selections
        "no_tool": 0.2       // 20% tasks requiring no tools
    }
}
```

**Configuration Parameters:**
- `mcp_servers` - List of MCP server tool definition files to use (without .json extension)
- `num_entries_per_server` - Number of evaluation entries to generate per server
- `task_character_limit` - Maximum character length for generated task descriptions
- `available_tools_per_task` - Maximum number of tools available for each task
- `match_distribution` - Target distribution of match types for balanced evaluation

### Output

The generated dataset (`generated_data.json`) contains evaluation entries with:
- **input** - Task description, requested tool, available tools, and MCP tool definitions
- **correct_choice** - The tool that should actually be selected (or null if no tool needed)
- **match** - Boolean indicating if the requested tool is correct for the task

By default the output file is compressed as `generated_data.json.gz` to save space.

## Dependencies

The generation script depends on MCP server tool definitions being available in the `mcp_servers/` directory. Ensure you've run the MCP tool extraction process first if needed.
