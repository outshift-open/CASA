"""Repository interface for LlmAppResponse."""

from abc import ABC, abstractmethod

from identity_auth_server.core.llm_app_response.types import LlmAppResponse, LlmAppResponseInput


class LlmAppResponseRepository(ABC):
    """Interface for LlmAppResponse repository implementations."""

    @abstractmethod
    def create(self, llm_app_response: LlmAppResponseInput) -> LlmAppResponse:
        """Persist a new LLM app response."""
        pass

    @abstractmethod
    def get_llm_app_response_by_token(self, token: str) -> list[LlmAppResponse]:
        """Retrieve all LLM app responses by llm_app_call_token."""
        pass
