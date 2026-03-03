"""Base classes for tool access checks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel

from identity_auth_server.core.events import MCPToolBlockingReason, MCPToolBlockingType
from identity_auth_server.core.types import ToolCheckFlags, UserInput
from identity_auth_server.types import McpServer


class Payload(BaseModel):
    """Payload for tool check evaluation."""

    llm_selected_tools: List[str]
    requested_tool: str
    mcp_server: McpServer
    user_input: UserInput


class CheckResult(BaseModel):
    """Result of a tool check evaluation."""

    satisfied: bool = True
    blocking_type: Optional[MCPToolBlockingType] = None
    blocking_reason: Optional[MCPToolBlockingReason] = None


class BaseToolCheck(ABC):
    """Base class for tool access checks."""

    def __init__(self):
        """Initialize the tool check."""
        pass

    @abstractmethod
    def is_satisfied(self, payload: Payload) -> CheckResult:
        """Check if the tool access is satisfied."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def flag(self) -> ToolCheckFlags:
        """Get the check flag."""
        raise NotImplementedError()

    def __and__(self, other: "BaseToolCheck") -> "AndToolCheck":
        """Combine checks with AND logic."""
        return AndToolCheck(self, other)


@dataclass(frozen=True)
class AndToolCheck(BaseToolCheck):
    """Check that combines two checks with AND logic."""

    flag = ToolCheckFlags.NONE
    first: Optional[BaseToolCheck]
    second: Optional[BaseToolCheck]

    def is_satisfied(self, payload: Payload) -> CheckResult:
        """Check if both checks are satisfied."""
        if self.first is None and self.second is None:
            return CheckResult(satisfied=True)

        if self.first is None or self.second is None:
            return CheckResult(satisfied=False)

        check_result = self.first.is_satisfied(payload)
        if not check_result.satisfied:
            return check_result

        check_result = self.second.is_satisfied(payload)
        if not check_result.satisfied:
            return check_result

        return CheckResult(satisfied=True)
