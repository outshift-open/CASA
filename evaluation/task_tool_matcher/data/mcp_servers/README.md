# MCP Servers Tool Definitions

This folder contains tool definitions extracted from Model Context Protocol (MCP) servers, which can be used for evaluating and testing the task-tool matching pipeline.

## Overview

The MCP servers provide standardized interfaces for interacting with various external services and APIs.
The `generation/` subdirectory contains:

- `extract_mcp_tools.py` - Python script to launch and connect to MCP servers and extract tool definitions
- `servers_config.json` - Configuration file defining how to connect to each MCP server

## Usage

### Extracting Tool Definitions

To regenerate the tool definition files:

1. Have Docker running, the script will pull and run the MCP servers as needed.
2. Configure desired MCP servers in `servers_config.json` with default settings (as the tools from the servers will not be used)
3. Run the extraction script:

```bash
python evaluation/task_tool_matcher/data/mcp_servers/generation/extract_mcp_servers.py
```

This will:
- Launch the MCP servers defined in `servers_config.json`
- Connect to each configured MCP server
- Query available tools using the MCP protocol
- Save tool definitions to JSON files in this directory


### Synthesizing Tasks from Tools

After obtaining MCP tool descriptions, and saving them in JSON files,
from the command line at root level, you can launch a synthetic data generation to obtain one or more task(s) requiring the given tool to be carried out by an agent:

```bash
cd evaluation/task_tool_matcher/data;
python generation.py \
    --input-files mcp_servers/atlassian_tools.json mcp_servers/github-official_tools.json \
    --output-file generated_tasks.json \  
    --multiplier 5
```

The results are stored in `generated_tasks.json` with:
- tool_name: the name of the tool
- synthetic_tasks: a list of `multiplier` synthetic tasks requiring that tool
- system_prompt: the system prompt used for the generation
where the multiplier controls the number of tasks generated per tool. The calls go through AsyncOpenAI, limited to a maximum of 10 at a time.
