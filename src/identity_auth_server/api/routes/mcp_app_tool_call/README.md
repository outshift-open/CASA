````markdown
# MCP App Tool Call API Routes

This package exposes REST endpoints for persisting tool calls executed via MCP integrations. Routes are registered with FastAPI and backed by the Postgres implementation of `McpAppToolCallRepository`.

## POST `/mcp-app-tool-call`

Persist a new MCP tool invocation and associate it to previously recorded source and LLM artifacts.

- **Request Body** — `McpAppToolCallInput`
  - `token` (`string`): Unique identifier for the tool call being stored.
  - `source_app_call_token` (`string`): Token resolving the originating source app call.
  - `llm_app_call_token` (`string`, optional): Token for the LLM app call that triggered this tool invocation.
  - `tool` (`string`): Serialized payload describing the tool execution.
- **Response Body** — `McpAppToolCall`
  - `id` (`UUID`): Generated identifier for the stored tool call.
  - `source_app_call_id` (`UUID`): Identifier of the linked source app call.
  - `llm_app_call_id` (`UUID|null`): Identifier of the associated LLM app call, if provided.
  - `llm_app_response_id` (`UUID|null`): Identifier of the most recent response for the linked LLM app call.
  - `token` (`string`): Echo of the tool call token.
  - `tool` (`string`): Echo of the serialized tool payload.
  - `blocked` (`boolean`): Indicates whether the tool call is blocked.
  - `blocked_by_type_id` (`UUID|null`): Optional identifier for the block reason.
  - `created_at` (`string`, ISO 8601 timestamp): UTC timestamp assigned during persistence.

### Example

```bash
curl -X POST \
  http://localhost:8000/mcp-app-tool-call \
  -H 'Content-Type: application/json' \
  -d '{
    "token": "tool-call-token-123",
    "source_app_call_token": "source-token-123",
    "llm_app_call_token": "llm-call-token-456",
    "tool": "{\"name\": \"search_docs\", \"args\": {\"query\": \"latest policy\"}}"
  }'
```

**Sample response**

```json
{
  "id": "8e4a4e44-325d-46a7-9dd7-4d1db93d7b3a",
  "source_app_call_id": "f77d93ce-4d02-46ef-8b0a-ecfa6a3ab7da",
  "llm_app_call_id": "22aa889c-1b53-4d7f-b65f-5fa94b1f5f09",
  "llm_app_response_id": "3fa9aae3-a7f9-4322-b6d1-42bbdc4ad129",
  "tool": "{\"name\": \"search_docs\", \"args\": {\"query\": \"latest policy\"}}",
  "blocked": false,
  "blocked_by_type_id": null,
  "created_at": "2025-01-08T12:36:00.123456Z"
}
```

> ℹ️ The router mounts without a prefix; adjust the URL if the application composes routers under a shared path.
````
