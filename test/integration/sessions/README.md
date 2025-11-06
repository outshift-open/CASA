# SESSIONS - Integration Tests for the API

This directory contains integration tests for the API routes defined in the `src/identity_auth_server/api/routes` package - specifically the `sessions` route. These tests validate the end-to-end functionality of the sessions API endpoints, ensuring they correctly handle requests and interact with the underlying database.

## Test cases

### Happy Path Tests

1. Create a source app session.
- Create a source app session and verify the returned token.

2. Create an LLM app session.
- Create a source app session, then create an LLM app session linked to that source app session. Verify the returned token.

3. Create an MCP app session with LLM app session.
- Create a source app session, then create an LLM app session linked to that source app session, then create an MCP app session linked to both the source app session and LLM app session. Verify the returned token.

4. Retrieve multiple sessions.
- Create multiple source app sessions with various combinations of LLM app sessions and MCP app sessions. Verify the results.

5. Create multiple LLM app sessions from a single source app session.
- Create a source app session, then create multiple LLM app sessions linked to that source app session. Verify the results.

7. Create multiple MCP app sessions from a single source app session and LLM app session.
- Create a source app session, then create an LLM app session linked to that source app session, then create multiple MCP app sessions linked to both the source app session and LLM app session. Verify the results.

## Cleaning up test data

Integration tests create real records in the backing PostgreSQL database, so the suite truncates the relevant tables by default once it completes. During test runs the `DB_NAME` environment variable is automatically suffixed with `_test`, ensuring the test data lands in a dedicated database. To **opt out** of the cleanup (for example, when inspecting data manually), either pass the `--no-cleanup-integration-db` flag to `pytest` or set the `CLEANUP_INTEGRATION_DB` environment variable to a falsy value (`0`, `false`, `no`, `off`).

### Error Path Tests

1. Create an LLM app session with a non-existent source app session token.
- Attempt to create an LLM app session with a token that does not correspond to any existing source app session. Verify that the appropriate error is returned.

2. Create an MCP app session with a non-existent source app session token.
- Attempt to create an MCP app session with a token that does not correspond to any existing source app session. Verify that the appropriate error is returned.

3. Create an MCP app session with a non-existent LLM app session token.
- Attempt to create an MCP app session with a token that does not correspond to any existing LLM app session. Verify that the appropriate error is returned.

4. Create an MCP app session with an LLM app session token that does not belong to the provided source app session token.
- Attempt to create an MCP app session with an LLM app session token that is not linked to the provided source app session token. Verify that the appropriate error is returned.

5. Retrieve a non-existent source app session.
- Attempt to retrieve a source app session using a token that does not correspond to any existing source app session. Verify that the appropriate error is returned.

6. Retrieve a non-existent LLM app session.
- Attempt to retrieve an LLM app session using a token that does not correspond to any existing LLM app session. Verify that the appropriate error is returned.

7. Retrieve a non-existent MCP app session.
- Attempt to retrieve an MCP app session using a token that does not correspond to any existing MCP app session. Verify that the appropriate error is returned.
