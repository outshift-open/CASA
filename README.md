[![pytest](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pytest.yml/badge.svg)](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pytest.yml) [![pre-commit](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pre-commit.yml)

# Identity Auth Server

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

#### Setup .env

Create a `.env` file by copying the provided sample and updating it with your configuration:

```shell
cp .env.sample .env
```

### Database Setup

Ensure you have a PostgreSQL database running and accessible. Update the `.env` file with your database connection details.

### Keycloak Setup

You can run a local Keycloak instance using Docker Compose:

```shell
make keycloak-run
```

Update the `.env` file with the Keycloak admin username and password.
Keycloak will be accessible at `http://localhost:8080/`.

#### 3. Run the Server

```shell
make auth-server-run
```

Or manually:

```shell
source .venv/bin/activate

# Development server with auto-reload
uvicorn identity_auth_server.api.app:app --reload

# Or using FastAPI's built-in development server
fastapi dev src/identity_auth_server/api/app.py
```

The first time you run the server, it will automatically apply database migrations.

### Accessing the API

The server will be available at `http://localhost:8000` with interactive API documentation at `http://localhost:8000/docs`.

### Option 2: ZTA Explorer UI

For a graphical interface to manage applications and explore the ZTA system, you can run the ZTA Explorer UI:

#### Prerequisites

Ensure you have the UI environment configured:

```shell
cp zta-explorer-ui/.env.sample zta-explorer-ui/.env
```

Update `zta-explorer-ui/.env` with your API server URL (default: `http://localhost:8000`).

#### Run with Docker Compose

```shell
make ui-run
```

The UI will be available at `http://localhost:1234`.

To stop the UI:

```shell
make ui-stop
```

For more information about the UI, see the [ZTA Explorer UI README](zta-explorer-ui/README.md).

### Option 3: Run the Demo Setup

To run everything on docker, simply run:

```shell
make demo-run
```

and to stop

```shell
make demo-stop
```

To test the setup run the `curl` command described in this [section](#test-the-demo-setup).

If you want to do things manually, the sections below will show you how.

#### Frontend Auth Explorer

In a new terminal, navigate to `demo/demo-ui` and run:

```shell
yarn install
yarn run dev
```

The frontend will be available at `http://localhost:5173`.

#### Deploy LiteLLM proxy

In a new terminal, navigate to `demo/workshop/llm` and run:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install uv
uv pip install -r ../requirements.txt
uv pip install ../../../
```

Copy the .env sample to .env and set the master and salt keys

```shell
cp .env.sample .env
```

Copy the .config.yaml sample to config.yaml and set the LLM configuration (the Base URL and the Api Key)

```shell
cp ../llm/config.yaml.sample ../llm/config.yaml
```

Run LiteLLM

```shellcd llm
litellm --config config.yaml
```

LiteLLM will be available at `http://localhost:4000`.

#### Deploy MCP Server

In a new terminal, navigate to `demo/workshop/mcp` and run:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install uv
uv pip install -r ../requirements.txt
uv pip install ../../../
```

Run MCP server

```shellcd mcp
python main.py
```

The MCP server will be available at `http://localhost:3000`.

#### Deploy Agent

In a new terminal, navigate to `demo/workshop/app` and run:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install uv
uv pip install -r ../requirements.txt
uv pip install ../../../
uv pip install ./v2
```

Run the Agent

```shell
python main.py
```

The Agent will connect to both the LiteLLM proxy and the MCP server, and should be available at `http://localhost:8082`.

#### Deploy Trusted Client (previously called Source)

In a new terminal, navigate to `demo/workshop/source` and run:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install uv
uv pip install -r ../requirements.txt
uv pip install ../../../
```

Run the Trusted Client

```shell
python main.py
```

The Trusted Client will be available at `http://localhost:3999`.

### Test the demo setup

You can use curl to send a request to the Trusted Client, which will forward it to the Agent.

```shell
curl -X POST http://localhost:3999/process \
  -H "Content-Type: application/json" \
  -d '{"content": "Get the account summary and scheduled payments"}' | jq
```

If everything is set up correctly, you should see a JSON response with the Agent's response.
The ZTA Auth explorer should also show the blocked and approved MCP tool calls in the UI running at `http://localhost:5173`.

## Development

### Available Commands

- `make help` - Show all available commands
- `make init` - Initialize development environment
- `make update` - Update dependencies after changes to pyproject.toml
- `make clean` - Clean up and recreate the virtual environment
- `make test` - Run unit tests (excludes integration tests)
- `make test-integration` - Run only integration tests
- `make check` - Run code quality checks (linting, formatting)
- `make build` - Build the package for distribution

### Testing

The test suite is organized into unit tests and integration tests:

- **Unit tests** - Fast, isolated tests that don't require database or running services
- **Integration tests** - End-to-end tests that require database and running FastAPI application

By default, `pytest` and `make test` run only unit tests (integration tests are skipped). This is useful for:

- Fast local development
- CI/CD pipelines without database setup
- Quick validation of changes

To run different test suites:

```shell
# Run only unit tests (default)
pytest
# or
make test

# Run only integration tests
make test-integration

# Run all tests (unit + integration) by specifying the directory
pytest test/integration/ && pytest
```

**Note:** Integration tests require:

- PostgreSQL database running
- Proper environment configuration (.env file)
- Database migrations applied

#### Docker Commands

- `make docker-build` - Build the Docker image
- `make docker-run` - Run the application using Docker Compose
- `make docker-stop` - Stop Docker Compose services
- `make ui-run` - Run the ZTA Explorer UI
- `make ui-stop` - Stop the ZTA Explorer UI

### Code Quality

This project uses modern Python development tools:

- **uv** - Ultra-fast Python package manager
- **Ruff** - Lightning-fast linting and formatting
- **mypy** - Static type checking
- **pytest** - Testing framework
- **pre-commit** - Git hooks for code quality

Code quality checks run automatically on commit via pre-commit hooks.
