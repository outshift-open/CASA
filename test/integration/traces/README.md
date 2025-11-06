# TRACES - Integration Tests for the API

This directory contains integration tests for the API routes defined in the `src/identity_auth_server/api/routes` package. These tests validate the end-to-end functionality of the API endpoints, ensuring they correctly handle requests and interact with the underlying database.

## Test cases

### Happy Path Tests

1. Source app call, no other calls.
- Create a source app call, then fetch the trace and verify

2. Source app call, Source app response.
- Create a source app call, then create a source app response linked to that call. Fetch the trace and verify.

3. Source app call, LLM app call.
- Create a source app call, then create an LLM app call linked to that source app call. Fetch the trace and verify.

4. Source app call, LLM app call, LLM app response.
- Create a source app call, then create an LLM app call linked to that source app call, then create an LLM app response linked to that LLM app call. Fetch the trace and verify.

5. Source app call, LLM app call, LLM app response, then another LLM app call and response.
- Create a source app call, then create an LLM app call linked to that source app call, then create an LLM app response linked to that LLM app call. Then create another LLM app call and response linked to the same source app call. Fetch the trace and verify.

6. Source app call, LLM app call, LLM app response, MCP tool call.
- Create a source app call, then create an LLM app call linked to that source app call, then create an LLM app response linked to that LLM app call. Then create an MCP tool call linked to the source app call and LLM app call. Fetch the trace and verify.

7. Source app call, LLM app call, LLM app response, MCP tool call that is blocked.
- Create a source app call, then create an LLM app call linked to that source app call, then create an LLM app response linked to that LLM app call. Then create an MCP tool call linked to the source app call and LLM app call, and mark it as blocked. Fetch the trace and verify.

8. Source app call, MCP tool call without LLM app call.
- Create a source app call, then create an MCP tool call linked to that source app call without an LLM app call. Fetch the trace and verify.

9. Source app call, MCP tool call that is blocked.
- Create a source app call, then create an MCP tool call linked to that source app call without an LLM app call, and mark it as blocked. Fetch the trace and verify.

10. Retrieve multiple traces.
- Create multiple source app calls with various combinations of responses and calls. Fetch each trace individually and verify the results.

## Cleaning up test data

Integration tests create real records in the backing PostgreSQL database, so the suite truncates the relevant tables by default once it completes. During test runs the `DB_NAME` environment variable is automatically suffixed with `_test`, ensuring the test data lands in a dedicated database. To **opt out** of the cleanup (for example, when inspecting data manually), either pass the `--no-cleanup-integration-db` flag to `pytest` or set the `CLEANUP_INTEGRATION_DB` environment variable to a falsy value (`0`, `false`, `no`, `off`).

### Error Path Tests

1. Create a source app response with a non-existent source app call token.
- Attempt to create a source app response with a token that does not correspond to any existing source app call. Verify that the appropriate error is returned.

2. Create an LLM app call with a non-existent source app call token.
- Attempt to create an LLM app call with a token that does not correspond to any existing source app call. Verify that the appropriate error is returned.

3. Create an LLM app response with a non-existent source app call token.
- Attempt to create an LLM app response with a token that does not correspond to any existing source app call. Verify that the appropriate error is returned.

4. Create an LLM app response with a non-existent LLM app call token.
- Attempt to create an LLM app response with a token that does not correspond to any existing LLM app call. Verify that the appropriate error is returned.

5. Create an MCP tool call with a non-existent source app call token.
- Attempt to create an MCP tool call with a token that does not correspond to any existing source app call. Verify that the appropriate error is returned.

6. Create an MCP tool call with a non-existent LLM app call token.
- Attempt to create an MCP tool call with a token that does not correspond to any existing LLM app call. Verify that the appropriate error is returned.

7. Fetch a trace for a non-existent source app call ID.
- Attempt to fetch a trace using a source app call ID that does not exist in the database. Verify that the appropriate error is returned.
