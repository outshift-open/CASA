"""Tool check factory module."""

from typing import List

from identity_auth_server.checks.base import AndToolCheck, BaseToolCheck
from identity_auth_server.core.types import ToolCheckFlags


class ToolCheckFactory:
    """Factory that builds a composite tool check from a list of registered checks."""

    def __init__(self, checks: List[BaseToolCheck]):
        """Initialize the factory with a list of tool checks."""
        self._checks = checks

    def get_tool_check(self, flags: ToolCheckFlags) -> BaseToolCheck:
        """Return a composite tool check for the given flags."""
        final_check = AndToolCheck(first=None, second=None)
        for check in self._checks:
            if (flags & check.flag) == check.flag:
                final_check = AndToolCheck(AndToolCheck(final_check.first, final_check.second), check)

        return final_check
