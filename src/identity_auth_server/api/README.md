# Identity Auth Server API

This README covers how to run the Identity Auth Server API and provides examples for using the available endpoints.

## Running the API Server

### Prerequisites

Make sure you have the project dependencies installed:

```bash
# Install dependencies using uv
uv sync
```

### Starting the Server

You can start the API server using one of the following methods:

#### Using uvicorn (recommended for development)
```bash
# From the project root directory
uvicorn identity_auth_server.api.app:app --reload --host 0.0.0.0 --port 8000
```

#### Using FastAPI's built-in development server
```bash
# From the project root directory  
fastapi dev src/identity_auth_server/api/app.py
```

#### Using Docker Compose
```bash
# From the project root directory
make docker-run
```

The API will be available at `http://localhost:8000` by default.

### API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

The API provides two main endpoints for task-tool matching:

### 1. Badge-based Tool Matching

**Endpoint:** `POST /task/intent/mcp/badge/tool-match`

This endpoint matches tools based on an MCP (Model Context Protocol) identity badge. The badge is verified with the identity service and tools are extracted from it.

#### Request Body

```json
{
  "task": "string",
  "requested_tool": "string",
  "available_tools": ["string"],
  "mcp_badge": "string"
}
```

#### Query Parameters

- `task_tool_matcher` (optional): The matcher algorithm to use. Options: `"random"` (default), `"embeddings"`

#### Example curl Request

```bash
curl -X POST "http://localhost:8000/task/intent/mcp/badge/tool-match?task_tool_matcher=random" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create a new Jira issue for a bug report",
    "requested_tool": "jira_create_issue",
    "available_tools": ["jira_create_issue", "jira_update_issue", "jira_delete_issue" ],
    "mcp_badge": "'$(cat test/api/data/jira_mcp_badge.txt)'"
  }'
```

#### Example Response (Success)

```json
{
  "task_tool_match": true,
  "reason": null
}
```

#### Example Response (No Match)

```json
{
  "task_tool_match": false,
  "reason": "Random matcher decided this tool doesn't match the task"
}
```

### 2. Direct Tool Matching

**Endpoint:** `POST /task/intent/mcp/tool-match`

This endpoint matches tools based on directly provided MCP tool objects.

#### Request Body

```json
{
  "task": "string",
  "requested_tool": "string",
  "available_tools": ["string"],
  "mcp_tools": [
    {
      "name": "string",
      "description": "string",
      "inputSchema": {
        "type": "object",
        "properties": {}
      }
    }
  ]
}
```

#### Query Parameters

- `task_tool_matcher` (optional): The matcher algorithm to use. Options: `"random"` (default), `"embeddings"`

#### Example curl Request

```bash
curl -X POST "http://localhost:8000/task/intent/mcp/tool-match?task_tool_matcher=random" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze code repository for security vulnerabilities",
    "requested_tool": "security_scan",
    "available_tools": ["security_scan", "code_review", "dependency_check"],
    "mcp_tools": [
      {
        "name": "security_scan",
        "description": "Scans code repositories for security vulnerabilities and generates reports",
        "inputSchema": {
          "type": "object",
          "properties": {
            "repository_path": {
              "type": "string",
              "description": "Path to the code repository to scan"
            },
            "scan_type": {
              "type": "string",
              "enum": ["quick", "full", "custom"],
              "description": "Type of security scan to perform"
            }
          },
          "required": ["repository_path"]
        }
      },
      {
        "name": "code_review",
        "description": "Performs automated code review to identify code quality issues, best practices violations, and potential bugs",
        "inputSchema": {
          "type": "object",
          "properties": {
            "repository_path": {
              "type": "string",
              "description": "Path to the code repository to review"
            },
            "review_scope": {
              "type": "string",
              "enum": ["full", "changed_files", "specific_files"],
              "description": "Scope of the code review"
            },
            "file_patterns": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "File patterns to include in review (when scope is specific_files)"
            },
            "rules": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Specific rules or categories to check"
            }
          },
          "required": ["repository_path", "review_scope"]
        }
      },
      {
        "name": "dependency_check",
        "description": "Analyzes project dependencies for known vulnerabilities, license compliance, and outdated packages",
        "inputSchema": {
          "type": "object",
          "properties": {
            "project_path": {
              "type": "string",
              "description": "Path to the project directory containing dependency files"
            },
            "check_type": {
              "type": "string",
              "enum": ["vulnerabilities", "licenses", "outdated", "all"],
              "description": "Type of dependency check to perform"
            },
            "package_files": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Specific package files to analyze (e.g., package.json, requirements.txt, pom.xml)"
            },
            "severity_threshold": {
              "type": "string",
              "enum": ["low", "medium", "high", "critical"],
              "description": "Minimum severity level for vulnerability reporting"
            }
          },
          "required": ["project_path", "check_type"]
        }
      }
    ]
  }'
```

#### Example Response (Success)

```json
{
  "task_tool_match": true,
  "reason": null
}
```

#### Example Response (No Match)

```json
{
  "task_tool_match": false,
  "reason": "Random matcher decided this tool doesn't match the task"
}
```

## Matcher Types

The API supports different task-tool matching algorithms:

- **`random`**: A simple random matcher for testing and development
- **`embeddings`**: An advanced matcher using semantic embeddings (when available)

You can specify the matcher type using the `task_tool_matcher` query parameter.

## Testing

You can run the API tests using:

```bash
# Run all API tests
pytest test/api/

# Run specific endpoint tests
pytest test/api/test_app.py
```
