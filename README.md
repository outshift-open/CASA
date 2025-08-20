[![pytest](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pytest.yml/badge.svg)](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pytest.yml) [![pre-commit](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pre-commit.yml)

# Identity Auth Server

A FastAPI-based server for matching tasks with appropriate tools using Model Context Protocol (MCP) integration. This server provides intelligent tool matching capabilities for Zero Trust Architecture (ZTA) identity and authentication workflows.

## Overview

The Identity Auth Server provides RESTful endpoints that accept task descriptions and available tools, then returns the most appropriate tool matches using configurable matching algorithms. It supports both MCP badge-based tool extraction and direct MCP tool object matching.

### Key Features

- **Task-Tool Matching**: Intelligent matching of tasks to appropriate tools
- **MCP Integration**: Support for Model Context Protocol (MCP) tools and badges  
- **Configurable Matchers**: Pluggable matching algorithms (currently includes random matcher)
- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **Type Safety**: Full Pydantic model validation and type hints

## API Endpoints

### POST `/task/intent/mcp/badge/tool-match`
Matches tools based on MCP badge information.

**Request Body:**
- `task`: Task description string
- `requested_tool`: Specific tool name being requested
- `available_tools`: List of available tool names
- `mcp_badge`: MCP identity badge containing tool objects

### POST `/task/intent/mcp/tool-match`
Matches tools based on direct MCP tool objects.

**Request Body:**
- `task`: Task description string
- `requested_tool`: Specific tool name being requested  
- `available_tools`: List of available tool names
- `mcp_tools`: List of MCP tool objects

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Quick Start

### 1. Environment Setup
After cloning the repo, initialize the development environment:

```shell
make init
```

This will:
- Create a Python virtual environment
- Install all dependencies (including dev dependencies)
- Set up pre-commit hooks

### 2. Activate Environment
```shell
source .venv/bin/activate
```

### 3. Run the Server
```shell
# Development server with auto-reload
uvicorn identity_auth_server.api.app:app --reload

# Or using FastAPI's built-in development server
fastapi dev src/identity_auth_server/api/app.py
```

The server will be available at `http://localhost:8000` with interactive API documentation at `http://localhost:8000/docs`.

## Development

### Available Commands

- `make help` - Show all available commands
- `make init` - Initialize development environment
- `make update` - Update dependencies after changes to pyproject.toml
- `make clean` - Clean up and recreate the virtual environment
- `make test` - Run unit tests with pytest
- `make check` - Run code quality checks (linting, formatting)
- `make build` - Build the package for distribution

### Code Quality

This project uses modern Python development tools:

- **uv** - Ultra-fast Python package manager
- **Ruff** - Lightning-fast linting and formatting  
- **mypy** - Static type checking
- **pytest** - Testing framework
- **pre-commit** - Git hooks for code quality

Code quality checks run automatically on commit via pre-commit hooks.

### Project Structure

```
src/identity_auth_server/
├── api/                    # FastAPI application and API types
│   ├── app.py             # Main FastAPI application
│   └── types.py           # API request/response models
├── pipelines/             # Core processing pipelines
│   └── task_tool_matcher/ # Tool matching logic
└── types.py               # Common type definitions
```

## Architecture

The server is built with a modular architecture:

- **API Layer**: FastAPI endpoints handling HTTP requests/responses
- **Pipeline Layer**: Core business logic for task-tool matching
- **Type System**: Comprehensive type definitions using Pydantic models
- **Factory Pattern**: Configurable matcher selection via TaskToolMatcherFactory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run quality checks: `make check`
5. Run tests: `make test`  
6. Submit a pull request

All commits must pass pre-commit hooks including linting, formatting, and type checking.

## License

See [LICENSE](LICENSE) file for details.

## Authors

- Chiara Troiani (chtroian@cisco.com)
- Majed El Helou (melhelou@cisco.com)  
- Ben Ryder (beryder@cisco.com)
