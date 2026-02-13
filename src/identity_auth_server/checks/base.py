from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel

from identity_auth_server.core.events import MCPToolBlockingReason, MCPToolBlockingType
from identity_auth_server.core.types import ToolCheckFlags, UserInput
from identity_auth_server.types import McpServer


class Payload(BaseModel):
    llm_selected_tools: List[str]
    requested_tool: str
    mcp_server: McpServer
    user_input: UserInput


class CheckResult(BaseModel):
    satisfied: bool = True
    blocking_type: Optional[MCPToolBlockingType] = None
    blocking_reason: Optional[MCPToolBlockingReason] = None


class BaseToolCheck(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def is_satisfied(self, payload: Payload) -> CheckResult:
        raise NotImplementedError()

    @property
    @abstractmethod
    def flag(self) -> ToolCheckFlags:
        raise NotImplementedError()

    def __and__(self, other: "BaseToolCheck") -> "AndToolCheck":
        return AndToolCheck(self, other)


@dataclass(frozen=True)
class AndToolCheck(BaseToolCheck):
    first: BaseToolCheck
    second: BaseToolCheck

    def is_satisfied(self, payload: Payload) -> CheckResult:
        if self.first is None or self.second is None:
            return False
        check_result = self.first.is_satisfied(payload)
        if not check_result.satisfied:
            return check_result

        check_result = self.second.is_satisfied(payload)
        if not check_result.satisfied:
            return check_result

        return CheckResult(satisfied=True)
