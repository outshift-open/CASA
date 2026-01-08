"""Shared fixtures and session hooks for integration tests."""

import logging
import time
from collections.abc import Generator
from multiprocessing import Process

import pytest
import requests
import uvicorn
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()

from identity_auth_server.api.app import app

logger = logging.getLogger(__name__)

# _CLEANUP_FLAG_ENV = "CLEANUP_INTEGRATION_DB"
# _FALSE_VALUES = {"0", "false", "no", "off"}
# _TABLES_TO_CLEAN: tuple[str, ...] = (
#     "apps",
#     "authorization_servers",
#     "client_credentials",
#     "tokens",
#     "mcp_app_call_sessions",
#     "llm_app_call_sessions",
#     "source_app_call_sessions",
#     "mcp_app_tool_calls",
#     "llm_app_responses",
#     "llm_app_calls",
#     "source_app_responses",
#     "source_app_calls",
# )
#
#
# def pytest_addoption(parser: pytest.Parser) -> None:
#     """Register CLI options controlling post-test database cleanup."""
#     parser.addoption(
#         "--no-cleanup-integration-db",
#         action="store_true",
#         default=False,
#         help="Skip truncating integration tables after the test session finishes.",
#     )
#
#
# def _flag_enabled(config: pytest.Config) -> bool:
#     if config.getoption("no_cleanup_integration_db"):
#         return False
#
#     env_value = os.getenv(_CLEANUP_FLAG_ENV)
#     if env_value is None:
#         return True
#
#     return env_value.lower() not in _FALSE_VALUES
#
#
# def _truncate_tables(tables: Iterable[str]) -> None:
#     statement = text("TRUNCATE TABLE " + ", ".join(f'"{table}"' for table in tables) + " RESTART IDENTITY CASCADE")
#     with app_database.session_scope() as session:
#         session.execute(statement)
#
#
# @pytest.fixture(scope="session", autouse=True)
# def _cleanup_integration_db(request: pytest.FixtureRequest) -> Generator[None, None, None]:
#     """Optionally purge integration tables after all tests in this package run."""
#     yield
#
#     if not _flag_enabled(request.config):
#         return
#
#     try:
#         _truncate_tables(_TABLES_TO_CLEAN)
#         logger.info("Integration DB cleanup complete for tables: %s", ", ".join(_TABLES_TO_CLEAN))
#     except (OperationalError, ProgrammingError) as exc:
#         logger.warning("Integration DB cleanup skipped due to error: %s", exc)


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Provide a FastAPI test client backed by the real application."""
    with TestClient(app, "http://localhost:3000") as test_client:
        yield test_client


@pytest.fixture(scope="session")
def api_server():
    """Bring server up."""
    proc = Process(
        target=uvicorn.run,
        kwargs={"app": "identity_auth_server.api.app:app", "host": "127.0.0.1", "port": 3000, "log_level": "info"},
        daemon=True,
    )

    proc.start()

    # Wait for the server to be ready
    # This is a simple way to wait. A more robust solution might involve
    # polling the health check endpoint until it returns a 200 OK.
    retries = 5
    while retries > 0:
        try:
            response = requests.get("http://127.0.0.1:3000/health")
            if response.status_code == 200:
                break
        except requests.ConnectionError:
            pass
        retries -= 1
        time.sleep(0.5)
    if retries == 0:
        proc.terminate()  # Clean up the process if it never became ready
        pytest.fail("Server did not start within the allotted time.")

    yield  # This is where the testing happens

    # Teardown: terminate the server process
    proc.terminate()
