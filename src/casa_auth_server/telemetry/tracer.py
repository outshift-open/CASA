# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tracing service implementation."""

from typing import Optional
from uuid import UUID

from casa_auth_server.core.events import BaseEvent
from casa_auth_server.telemetry.tracer_repository import Trace, TraceList, TracerRepository


class Tracer:
    """Service for recording and querying domain event traces."""

    def __init__(self, tracer_repository: TracerRepository):
        """Initialize the tracer with a backing repository."""
        self._tracer_repository = tracer_repository

    def record_event(self, event: BaseEvent):
        """Persist an event to the trace store."""
        self._tracer_repository.store_event(event)

    def get_traces(
        self, page: int, page_size: int, mas_id: Optional[UUID] = None, fetch_all: bool = False
    ) -> TraceList:
        """Retrieve all traces in a paginated fashion."""
        if not fetch_all:
            if page < 1:
                raise ValueError("page must be greater than 0")
            if page_size < 1:
                raise ValueError("page_size must be greater than 0")

        return self._tracer_repository.get_all(page, page_size, mas_id=mas_id, fetch_all=fetch_all)

    def get_traces_by_user_input_and_event_type(self, user_input_id: str, event_type: str) -> list[Trace]:
        """Return all traces for a given user input filtered by event type."""
        return self._tracer_repository.get_traces_by_user_input_and_event_type(user_input_id, event_type)
