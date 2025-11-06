"""Repository interface for LlmAppCall."""

from abc import ABC, abstractmethod

from identity_auth_server.core.llm_app_call.types import LlmAppCall, LlmAppCallInput


class LlmAppCallRepository(ABC):
    """Interface for LlmAppCallRepository."""

    @abstractmethod
    def create(self, llm_app_call: LlmAppCallInput) -> LlmAppCall:
        """Create a new LLM app call."""
        pass
