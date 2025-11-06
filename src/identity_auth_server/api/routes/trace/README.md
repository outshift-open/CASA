````markdown
# Trace API Routes

This package exposes REST endpoints for retrieving trace timelines that join source calls, LLM interactions, and MCP tool executions. Routes are registered with FastAPI and backed by the Postgres implementation of `TraceRepository`.

## GET `/trace/{source_app_call_id}`

Fetch the full trace for a specific source app call.

- **Path Parameter**
  - `source_app_call_id` (`UUID`): Identifier for the source app call whose trace should be returned.
- **Response Body** — `Trace`
  - `source_app_call` (`SourceAppCall`): Details of the originating source app call.
  - `source_app_response` (`SourceAppResponse|null`): Latest response emitted for the source app call, if available.
  - `llm_app_calls` (`TraceLlmAppCall[]`): Ordered list of LLM calls (including `proxy_call_id`) and their latest LLM response (`llm_app_response`), if any.
  - `mcp_app_tool_calls` (`TraceMcpAppToolCall[]`): Ordered list of MCP tool calls, including any human-readable block description.

### Example

```bash
curl http://localhost:8000/trace/0d9f1a63-b3aa-4c3c-86b5-4e25a9fb42de
```

**Sample response**

```json
{
  "source_app_call": {
    "id": "0d9f1a63-b3aa-4c3c-86b5-4e25a9fb42de",
    "input": "{\"event\": \"login\", \"user\": \"alice\"}",
    "created_at": "2025-01-08T12:32:00.123456Z"
  },
  "source_app_response": {
    "id": "2247b294-5d35-45b1-b5c5-12d16b532aa4",
    "source_app_call_id": "0d9f1a63-b3aa-4c3c-86b5-4e25a9fb42de",
    "output": "{\"status\": \"ok\"}",
    "created_at": "2025-01-08T12:32:30.123456Z"
  },
  "llm_app_calls": [
    {
      "llm_app_call": {
        "id": "bd0f15af-0b5c-4c20-a6a4-59f05bf537f7",
        "source_app_call_id": "0d9f1a63-b3aa-4c3c-86b5-4e25a9fb42de",
        "proxy_call_id": "proxy-123",
        "messages": "[]",
        "tools": "[]",
        "created_at": "2025-01-08T12:33:00.123456Z"
      },
      "llm_app_response": {
        "id": "59611ba1-7fba-42ad-9d30-b809ea178c01",
        "llm_app_call_id": "bd0f15af-0b5c-4c20-a6a4-59f05bf537f7",
        "proxy_call_id": "proxy-123",
        "message": "{\"reply\": \"All set!\"}",
        "tool_calls": "[]",
        "created_at": "2025-01-08T12:33:30.123456Z"
      }
    }
  ],
  "mcp_app_tool_calls": [
    {
      "tool_call": {
        "id": "1d1e3a2c-ff2f-4d5b-9183-2a88b6ebb22a",
        "source_app_call_id": "0d9f1a63-b3aa-4c3c-86b5-4e25a9fb42de",
        "llm_app_call_id": "bd0f15af-0b5c-4c20-a6a4-59f05bf537f7",
        "llm_app_response_id": "59611ba1-7fba-42ad-9d30-b809ea178c01",
        "tool": "{\"name\": \"search_docs\", \"args\": {\"query\": \"latest policy\"}}",
        "blocked": false,
        "blocked_by_type_id": null,
        "created_at": "2025-01-08T12:34:00.123456Z"
      },
      "blocked_by_description": null
      }
    }
  ]
}
```

## GET `/trace`

Retrieve paginated traces across all source app calls.

- **Query Parameters**
  - `page` (`integer`, default `1`, minimum `1`): Page number to retrieve.
  - `page_size` (`integer`, default `20`, min `1`, max `100`): Maximum number of items to return.
- **Response Body** — `TraceList`
  - `items` (`Trace[]`): Collection of trace entries for the requested page.
  - `total` (`integer`): Total number of traces available.
  - `page` (`integer`): Echo of the requested page number.
  - `page_size` (`integer`): Echo of the requested page size.

### Example

```bash
curl "http://localhost:8000/trace?page=1&page_size=10"
```

**Sample response**

```json
{
  "items": [
    {
      "source_app_call": { "id": "0d9f1a63-b3aa-4c3c-86b5-4e25a9fb42de", "token": "sample-token-123", "input": "{}", "created_at": "2025-01-08T12:32:00.123456Z" },
      "source_app_response": null,
      "llm_app_calls": [],
      "mcp_app_tool_calls": []
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

> ℹ️ The router is mounted without a prefix; adjust the URL if the application composes routers under a shared path.
````
