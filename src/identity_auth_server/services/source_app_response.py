"""Service layer for source app response operations."""

from abc import ABC, abstractmethod

from identity_auth_server.core.source_app_response.repository import SourceAppResponseRepository
from identity_auth_server.core.source_app_response.types import SourceAppResponse, SourceAppResponseInput


class SourceAppResponseService(ABC):
    """Interface for SourceAppResponse service implementations."""

    def __init__(self, source_app_response_repository: SourceAppResponseRepository):
        """Initialize the service with a repository."""
        self.source_app_response_repository = source_app_response_repository

    @abstractmethod
    def create_source_app_response(self, source_app_response: SourceAppResponseInput) -> SourceAppResponse:
        """Create a new source app response."""
        raise NotImplementedError


class SourceAppResponseServiceImpl(SourceAppResponseService):
    """Implementation of the SourceAppResponse service."""

    def create_source_app_response(self, source_app_response: SourceAppResponseInput) -> SourceAppResponse:
        """Create a new source app response."""
        return self.source_app_response_repository.create(source_app_response)
