"""Top-level pytest configuration for all tests."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from dotenv import dotenv_values

_DB_SUFFIX = "_test"
_ORIGINAL_DB_NAME = os.environ.get("DB_NAME")
_CONFIG_DB_NAME = _ORIGINAL_DB_NAME or dotenv_values().get("DB_NAME")

if _CONFIG_DB_NAME:
    _TARGET_DB_NAME = _CONFIG_DB_NAME if _CONFIG_DB_NAME.endswith(_DB_SUFFIX) else f"{_CONFIG_DB_NAME}{_DB_SUFFIX}"
    os.environ["DB_NAME"] = _TARGET_DB_NAME
else:
    _TARGET_DB_NAME = None


@pytest.fixture(scope="session", autouse=True)
def _restore_database_name() -> Generator[None, None, None]:
    """Ensure the DB_NAME environment variable is restored after tests."""
    try:
        yield
    finally:
        if _ORIGINAL_DB_NAME is None:
            os.environ.pop("DB_NAME", None)
        else:
            os.environ["DB_NAME"] = _ORIGINAL_DB_NAME
