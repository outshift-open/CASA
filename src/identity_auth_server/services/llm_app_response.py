"""Service layer for LLM app response operations."""

from abc import ABC, abstractmethod

from identity_auth_server.core.llm_app_response.repository import LlmAppResponseRepository
from identity_auth_server.core.llm_app_response.types import LlmAppResponse, LlmAppResponseInput


class LlmAppResponseService(ABC):
    """Interface for LlmAppResponse service implementations."""

    def __init__(self, llm_app_response_repository: LlmAppResponseRepository):
        """Initialize the service with a repository."""
        self.llm_app_response_repository = llm_app_response_repository

    @abstractmethod
    def create_llm_app_response(self, llm_app_response: LlmAppResponseInput) -> LlmAppResponse:
        """Create a new LLM app response."""
        pass


class LlmAppResponseServiceImpl(LlmAppResponseService):
    """Implementation of the LlmAppResponse service."""

    def create_llm_app_response(self, llm_app_response: LlmAppResponseInput) -> LlmAppResponse:
        """Create a new LLM app response."""
        return self.llm_app_response_repository.create(llm_app_response)
