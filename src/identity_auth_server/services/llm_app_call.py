"""Service layer for LLM app call operations."""

from abc import ABC, abstractmethod

from identity_auth_server.core.llm_app_call.repository import LlmAppCallRepository
from identity_auth_server.core.llm_app_call.types import LlmAppCall, LlmAppCallInput


class LlmAppCallService(ABC):
    """Interface for LlmAppCallService."""

    def __init__(self, llm_app_call_repository: LlmAppCallRepository):
        """Initialize the service with a repository."""
        self.llm_app_call_repository = llm_app_call_repository

    @abstractmethod
    def create_llm_app_call(self, llm_app_call: LlmAppCallInput) -> LlmAppCall:
        """Create a new LLM app call."""
        pass


class LlmAppCallServiceImpl(LlmAppCallService):
    """Implementation of LlmAppCallService."""

    def create_llm_app_call(self, llm_app_call: LlmAppCallInput) -> LlmAppCall:
        """Create a new LLM app call."""
        return self.llm_app_call_repository.create(llm_app_call)
