"""Tracing service implementation"""

from identity_auth_server.core.events import BaseEvent
from identity_auth_server.telemetry.tracer_repository import Trace, TraceList, TracerRepository


class Tracer:
    def __init__(self, tracer_repository: TracerRepository):
        self._tracer_repository = tracer_repository

    def record_event(self, event: BaseEvent):
        self._tracer_repository.store_event(event)

    def get_traces(self, page: int, page_size: int) -> TraceList:
        """Retrieve all traces in a paginated fashion."""
        if page < 1:
            raise ValueError("page must be greater than 0")
        if page_size < 1:
            raise ValueError("page_size must be greater than 0")

        return self._tracer_repository.get_all(page, page_size)

    def get_traces_by_user_input_and_event_type(self, user_input_id: str, event_type: str) -> list[Trace]:
        return self._tracer_repository.get_traces_by_user_input_and_event_type(user_input_id, event_type)
