"""Repository interface for SourceAppResponse."""

from abc import ABC, abstractmethod

from identity_auth_server.core.source_app_response.types import SourceAppResponse, SourceAppResponseInput


class SourceAppResponseRepository(ABC):
    """Interface for SourceAppResponseRepository."""

    @abstractmethod
    def create(self, source_app_response: SourceAppResponseInput) -> SourceAppResponse:
        """Create a new source app response."""
        raise NotImplementedError
