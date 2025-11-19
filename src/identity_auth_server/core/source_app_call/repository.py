"""Repository interface for SourceAppCall."""

from abc import ABC, abstractmethod

from identity_auth_server.core.source_app_call.types import SourceAppCall, SourceAppCallInput


class SourceAppCallRepository(ABC):
    """Interface for SourceAppCallRepository."""

    @abstractmethod
    def create(self, source_app_call: SourceAppCallInput) -> SourceAppCall:
        """Create a new source app call."""
        pass

    @abstractmethod
    def get_source_app_call_by_token(self, token: str) -> list[SourceAppCall]:
        """Retrieve all source app calls by source_app_call_token."""
        pass
