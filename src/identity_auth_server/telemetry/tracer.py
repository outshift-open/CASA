"""Tracing service implementation"""

from identity_auth_server.core.events import BaseEvent
from identity_auth_server.telemetry.tracer_repository import TracerRepository


class Tracer:
    def __init__(self, tracer_repository: TracerRepository):
        self._tracer_repository = tracer_repository

    def record_event(self, event: BaseEvent):
        self._tracer_repository.store_event(event)
