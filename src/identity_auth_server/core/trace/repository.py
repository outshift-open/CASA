"""Repository interface for traces."""

from abc import ABC, abstractmethod
from uuid import UUID

from identity_auth_server.core.trace.types import Trace, TraceList


class TraceRepository(ABC):
    """Interface defining trace retrieval operations."""

    @abstractmethod
    def get(self, source_app_call_id: UUID) -> Trace:
        """Retrieve a trace for a single source app call."""
        pass

    @abstractmethod
    def get_all(self, page: int, page_size: int) -> TraceList:
        """Retrieve traces for all source app calls using pagination."""
        pass
