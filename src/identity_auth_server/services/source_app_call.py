"""Service layer for source app call operations."""

from abc import ABC, abstractmethod
from typing import Any

from identity_auth_server.core.source_app_call.repository import SourceAppCallRepository
from identity_auth_server.core.source_app_call.types import SourceAppCall, SourceAppCallInput


# interface for source app call service
class SourceAppCallService(ABC):
    """Interface for SourceAppCallService."""

    # initialize the service
    def __init__(self, source_app_call_repository: SourceAppCallRepository):
        """Initialize the SourceAppCallService with a repository."""
        self.source_app_call_repository = source_app_call_repository

    @abstractmethod
    def create_source_app_call(self, source_app_call: SourceAppCallInput) -> SourceAppCall:
        """Create a new source app call."""
        pass


# implementation of source app call service
class SourceAppCallServiceImpl(SourceAppCallService):
    """Implementation of SourceAppCallService."""

    # create a new source app call
    def create_source_app_call(self, source_app_call: SourceAppCallInput) -> Any:
        """Create a new source app call."""
        return self.source_app_call_repository.create(source_app_call)
