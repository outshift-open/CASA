# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tool check factory module."""

from casa_auth_server.checks.base import AndToolCheck, BaseToolCheck
from casa_auth_server.core.types import ToolCheckFlags


class ToolCheckFactory:
    """Factory that builds a composite tool check from a list of registered checks."""

    def __init__(self, checks: list[BaseToolCheck]):
        """Initialize the factory with a list of tool checks."""
        self._checks = checks

    def get_tool_check(self, flags: ToolCheckFlags) -> BaseToolCheck:
        """Return a composite tool check for the given flags."""
        final_check = AndToolCheck(first=None, second=None)
        for check in self._checks:
            if (flags & check.flag) == check.flag:
                final_check = AndToolCheck(AndToolCheck(final_check.first, final_check.second), check)

        return final_check
