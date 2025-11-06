````markdown
# LLM App Response API Routes

This package exposes REST endpoints for persisting responses returned by LLM applications. Routes are registered with FastAPI and backed by the Postgres implementation of `LlmAppResponseRepository`.

## POST `/llm-app-response`

Create a new LLM app response record.

- **Request Body** — `LlmAppResponseInput`
  - `token` (`string`): Identifier supplied with the LLM response payload.
  - `source_app_call_token` (`string`): Token linking the response back to the originating source app call.
  - `proxy_call_id` (`string`): Proxy-supplied identifier that correlates the response with a previously stored LLM app call.
  - `message` (`string`): Primary response message returned by the LLM.
  - `tool_calls` (`string`): Serialized representation of tool invocations (if any) included in the response.
- **Response Body** — `LlmAppResponse`
  - `id` (`UUID`): Generated identifier for the stored response.
  - `llm_app_call_id` (`UUID`): Identifier of the LLM app call associated with this response.
  - `token` (`string`): Echo of the response token.
  - `proxy_call_id` (`string`): Echo of the proxy correlation identifier.
  - `message` (`string`): Echo of the response message.
  - `tool_calls` (`string`): Echo of the serialized tool call payloads.
  - `created_at` (`string`, ISO 8601 timestamp): UTC timestamp assigned during persistence.

### Example

```bash
curl -X POST \
  http://localhost:8000/llm-app-response \
  -H 'Content-Type: application/json' \
  -d '{
    "token": "llm-response-token-123",
    "source_app_call_token": "source-token-123",
    "proxy_call_id": "proxy-123",
    "message": "{\"reply\": \"All set!\"}",
    "tool_calls": "[]"
  }'
```

**Sample response**

```json
{
  "id": "fde0974b-65fd-4a30-a65d-bdeb46f23fc7",
  "llm_app_call_id": "c22d7a2b-c8d4-4f5c-8f82-6f3f274cb918",
  "proxy_call_id": "proxy-123",
  "message": "{\"reply\": \"All set!\"}",
  "tool_calls": "[]",
  "created_at": "2025-01-08T12:35:00.123456Z"
}
```

> ℹ️ No prefix is applied by default. If the router is included under a larger path, the final URL may differ.
````
