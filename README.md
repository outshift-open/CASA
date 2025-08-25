[![pytest](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pytest.yml/badge.svg)](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pytest.yml) [![pre-commit](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pre-commit.yml)

# Identity Auth Server

The Identity Auth Server provides RESTful endpoints that accept a task description, a requested tool, and other available tools, then checks whether the requested tool best matches the task intention. It supports both MCP Identity badge-based tool extraction and direct MCP tool object matching.

## API Endpoints

### POST `/task/intent/mcp/tool-match`
Matches tools based on direct MCP tool objects.

**Request Body:**
- `task`: Task description string
- `requested_tool`: Specific tool name being requested  
- `available_tools`: List of available tool names
- `mcp_tools`: List of MCP tool objects

### POST `/task/intent/mcp/badge/tool-match`
Matches tools based on MCP badge information.

**Request Body:**
- `task`: Task description string
- `requested_tool`: Specific tool name being requested
- `available_tools`: List of available tool names
- `mcp_badge`: MCP identity badge containing tool objects

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Quick Start

### Option 1: Local Development

#### 1. Environment Setup
After cloning the repo, initialize the development environment:

```shell
make init
```

This will:
- Create a Python virtual environment
- Install all dependencies (including dev dependencies)
- Set up pre-commit hooks

#### 2. Activate Environment
```shell
source .venv/bin/activate
```

#### 3. Run the Server
```shell
# Development server with auto-reload
uvicorn identity_auth_server.api.app:app --reload

# Or using FastAPI's built-in development server
fastapi dev src/identity_auth_server/api/app.py
```

### Option 2: Docker Setup

#### Using Make Commands (Recommended)

```shell
# Build the Docker image
make docker-build

# Run with Docker Compose
make docker-run

# Stop Docker services
make docker-stop
```

#### Manual Docker Commands

```shell
# Build the image
docker build -f deployments/docker/Dockerfile -t identity-auth-server .

# Run with Docker Compose
cd deployments/docker-compose
docker compose up --build -d

# Stop services
cd deployments/docker-compose
docker compose down
```

### Accessing the API

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

#### Docker Commands
- `make docker-build` - Build the Docker image
- `make docker-run` - Run the application using Docker Compose
- `make docker-stop` - Stop Docker Compose services

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

### Required Access Keys
This project uses python-dotenv to handle secret keys.
Make a copy of `.env.sample` and rename it `.env` in the same directory (it is already covered in gitignore, make sure it remains hidden).
In your `.env`, fill the needed secret information that you personally have.


### Evaluations

#### Task Tool Matcher Evaluation

Initial assumptions and constraints
- Tasks are less than 150 characters
- Tasks should match to either a single tool or no tool
- Distribution (40% match, 40% wrong tool, 20% no tool)
