# Source App Call API Routes

This package exposes REST endpoints for persisting source application call records. Routes are registered via FastAPI and backed by the Postgres implementation of `SourceAppCallRepository`.

## POST `/source-app-call`

Create a new source app call record.

- **Request Body** — `SourceAppCallInput`
  - `token` (`string`): Authentication or correlation token attached to the originating source app call.
  - `input` (`string`): Raw payload submitted by the source application.
- **Response Body** — `SourceAppCall`
  - `id` (`UUID`): Generated identifier for the stored source app call.
  - `token` (`string`): Echo of the request token value.
  - `input` (`string`): Echo of the request payload.
  - `created_at` (`string`, ISO 8601 timestamp): Creation time in UTC supplied by the persistence layer.

### Example

```bash
curl -X POST \
  http://localhost:8000/source-app-call \
  -H 'Content-Type: application/json' \
  -d '{
    "token": "sample-token-123",
    "input": "{\"event\": \"login\", \"user\": \"alice\"}"
  }'
```

**Sample response**

```json
{
  "id": "0d9f1a63-b3aa-4c3c-86b5-4e25a9fb42de",
  "input": "{\"event\": \"login\", \"user\": \"alice\"}",
  "created_at": "2024-06-17T14:21:33.902176Z"
}
```

> ℹ️ The router does not attach a prefix by default. When mounted under a larger FastAPI application, the final path may include an additional prefix depending on how it is included.
