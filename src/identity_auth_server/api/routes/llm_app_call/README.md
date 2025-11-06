# LLM App Call API Routes

This package exposes REST endpoints for persisting LLM application call records. Routes are registered via FastAPI and backed by the Postgres implementation of `LlmAppCallRepository`.

## POST `/llm-app-call`

Create a new LLM app call record.

- **Request Body** — `LlmAppCallInput`
  - `token` (`string`): Authentication or correlation token attached to the LLM app call.
  - `source_app_call_token` (`string`): Token linking the LLM call back to the originating source app call.
  - `proxy_call_id` (`string`): Identifier supplied by the proxy layer to correlate the request and downstream response.
  - `messages` (`string`): Serialized representation of messages sent to the LLM.
  - `tools` (`string`): Serialized representation of tools available to the LLM.
- **Response Body** — `LlmAppCall`
  - `id` (`UUID`): Generated identifier for the stored LLM app call.
  - `source_app_call_id` (`UUID`): Identifier of the source app call associated with this LLM call.
  - `token` (`string`): Echo of the request token value.
  - `proxy_call_id` (`string`): Echo of the provided proxy correlation identifier.
  - `messages` (`string`): Echo of the serialized messages.
  - `tools` (`string`): Echo of the serialized tools.
  - `created_at` (`string`, ISO 8601 timestamp): Creation time in UTC supplied by the persistence layer.

### Example

```bash
curl -X POST \
  http://localhost:8000/llm-app-call \
  -H 'Content-Type: application/json' \
  -d '{
    "token": "llm-call-token-123",
    "source_app_call_token": "source-token-123",
    "proxy_call_id": "proxy-123",
    "messages": "[{\"role\": \"user\", \"content\": \"Hello\"}]",
    "tools": "[{\"name\": \"get_weather\", \"description\": \"Get weather data\"}]"
  }'
```

**Sample response**

```json
{
  "id": "c22d7a2b-c8d4-4f5c-8f82-6f3f274cb918",
  "source_app_call_id": "0d9f1a63-b3aa-4c3c-86b5-4e25a9fb42de",
  "proxy_call_id": "proxy-123",
  "messages": "[{\"role\": \"user\", \"content\": \"Hello\"}]",
  "tools": "[{\"name\": \"get_weather\", \"description\": \"Get weather data\"}]",
  "created_at": "2025-01-08T12:30:00.123456Z"
}
```

> ℹ️ The router does not attach a prefix by default. When mounted under a larger FastAPI application, the final path may include an additional prefix depending on how it is included.
