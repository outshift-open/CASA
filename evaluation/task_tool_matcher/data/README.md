# Task-Tool Matching Data Generation (Not Synthetic Task Creator)

This directory contains the data generation pipeline for creating synthetic evaluation datasets for the task-tool matching system.

## Overview

The generation system creates realistic task descriptions paired with MCP (Model Context Protocol) tools to evaluate and test task-tool matching algorithms. It generates datasets with configurable distributions of correct matches, wrong tool selections, and no-tool scenarios.


### Prerequisites

Ensure you have the virtual environment activated and the project dependencies installed.

Extract the MCP server tools first, by refering to `evaluation/task_tool_matcher/data/mcp_servers/README.md`.


### Synthesizing Tasks from Tools

After obtaining MCP server info, and saving them in JSON files in `evaluation/task_tool_matcher/data/mcp_servers`,
from the command line at root level, you can launch a synthetic data generation to obtain one or more task(s) requiring the given tool to be carried out by an agent:

```bash
python evaluation/task_tool_matcher/data/task_generation.py \
    --input-dir evaluation/task_tool_matcher/data/mcp_servers  \
    --output-file evaluation/task_tool_matcher/data/generated_tasks.json \
    --multiplier 3
```

You can also generate tasks requiring multiple tools by setting `num_tools` to your chosen integer value (not recommended to go beyond 3 or 4):
```bash
python evaluation/task_tool_matcher/data/task_generation.py \
    --input-dir evaluation/task_tool_matcher/data/mcp_servers  \
    --output-file evaluation/task_tool_matcher/data/generated_tasks.json \
    --multiplier 3 --num_tools 2
```

The results are stored in `generated_tasks.json`, in a list of samples as the one below:
```json
{
    "tool_names": [
      "azmcp-monitor-table-list"
    ],
    "mcp_servers": [
      "azure"
    ],
    "synthetic_tasks": [
      "Task Description 1",
      "Task Description 2",
      "Task Description 3"
    ],
    "system_prompt": "obscure_base",
    "tools_per_task": 1,
    "SO_tasks_per_sample": 3,
    "conversation": false
}
```

- tool_names: the names of the tools
- mcp_servers: the names of the MCP servers
- synthetic_tasks: a list of `multiplier` synthetic tasks requiring the tools
- system_prompt: the tag of the system prompt used for the generation
where the multiplier controls the number of tasks generated per tool. The calls go through AsyncOpenAI, limited to a maximum of 10 at a time.


### Simulating the Tool Requests from Tasks
To the tool requests dataset, you can import and call the function `generate_tool_requests_data` from the script or directly call the script from the CLI as below:

```bash
source .venv/bin/activate
python -m evaluation.task_tool_matcher.data.generation.synthetic_data_generator --config {CONFIG PATH} --input {TASKS JSON PATH} --output {OUTPUT JSON PATH}
```

This will generate synthetic tool-task pairings, following the configuration in `config.json`.
For multi-tool tasks datasets, the script automatically detects this and adapts sampling algorithms accordingly.
Edit `config.json` to customize the generation process:

```json
{
    "mcp_servers": [
        "atlassian",
        "github-official",
        "grafana",
        "hummingbot-mcp",
        "mongodb",
        "nasdaq-data-link",
        "notion",
        "paper-search",
        "azure",
        "sonarqube",
        "stripe",
        "wikipedia-mcp"
    ], //remove any MCP server(s) you do not intend to use
    "num_correct_matches": 1056, //select how many correct matches you want (max= # tools * multiplier)
    "ratio_wrong_matches": 2, //set the ratio of wrong matches, ex: 2 -> 2*1056 wrong matches
    "ratio_null_matches": 2   //set the ratio of null matches, ex: 2 -> 2*1056 null matches (null refers to the correct tool being in a **different MCP server**)
}

```

The generation script depends on MCP server tool definitions being available in the `mcp_servers/` directory. Ensure you've run the MCP tool extraction process first if needed.



### Generating Conversations (Single Agent Mode)
```bash
python evaluation/task_tool_matcher/data/task_generation.py \
    --input-dir evaluation/task_tool_matcher/data/mcp_servers  \
    --output-file evaluation/task_tool_matcher/data/conv_1tool_5SO_12MCP.json \
    --multiplier 5 --num_tools 1 --conversation
```
