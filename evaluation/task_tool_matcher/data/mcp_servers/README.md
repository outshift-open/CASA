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
