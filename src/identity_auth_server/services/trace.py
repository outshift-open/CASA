"""Service layer for trace retrieval."""

from abc import ABC, abstractmethod
from uuid import UUID

from identity_auth_server.core.trace.repository import TraceRepository
from identity_auth_server.core.trace.types import Trace, TraceList


class TraceService(ABC):
    """Interface defining trace service methods."""

    def __init__(self, trace_repository: TraceRepository):
        """Initialize the service with a trace repository."""
        self.trace_repository = trace_repository

    @abstractmethod
    def get_trace(self, source_app_call_id: UUID) -> Trace:
        """Retrieve a trace for a specific source app call."""
        pass

    @abstractmethod
    def get_traces(self, page: int, page_size: int) -> TraceList:
        """Retrieve paginated traces."""
        pass


class TraceServiceImpl(TraceService):
    """Concrete implementation of TraceService."""

    def get_trace(self, source_app_call_id: UUID) -> Trace:
        """Retrieve a trace for a specific source app call."""
        return self.trace_repository.get(source_app_call_id)

    def get_traces(self, page: int, page_size: int) -> TraceList:
        """Retrieve paginated traces."""
        return self.trace_repository.get_all(page, page_size)
