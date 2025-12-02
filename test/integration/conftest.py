"""Shared fixtures and session hooks for integration tests."""

import logging
from collections.abc import Generator

import pytest
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
