# Copyright 2026 Cisco Systems, Inc. and its affiliates
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

"""Tracer repository implementation."""

from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict
from sqlmodel import JSON, Column, Field, Session, SQLModel, desc, func, select

from casa_auth_server.core.events import BaseEvent


class Trace(SQLModel, table=True):  # type: ignore[call-arg]
    """SQLModel for storing event traces."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_input_id: UUID | None = Field(foreign_key="userinput.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    event_type: str
    event: dict[str, Any] = Field(sa_column=Column(JSON))


class TraceList(BaseModel):
    """Paginated list of events."""

    items: dict[str, list[Trace]]
    total: int
    page: int
    page_size: int


class TracerRepository(ABC):
    """Interface exposing the methods of TracerRepository."""

    @abstractmethod
    def store_event(self, event):
        """Stores an event in the database."""

    @abstractmethod
    def get_all(self, page: int, page_size: int, mas_id: UUID | None = None, fetch_all: bool = False) -> TraceList:
        """Retrieve traces for all source app calls using pagination."""
        pass

    @abstractmethod
    def get_traces_by_user_input_and_event_type(self, user_input_id: str, event_type: str) -> list[Trace]:
        """Retrieve traces for a specific user input and event type."""
        pass


class TracerPostgresRepository(TracerRepository):
    """Postgre implementation of TracerRepository."""

    def __init__(self, session: Session):
        """Initialize the tracer repository.

        Args:
            session: SQLModel database session.
        """
        self._session = session

    def store_event(self, event: BaseEvent):
        """Stores an event in the database."""
        trace = Trace(
            id=event.id,
            user_input_id=UUID(event.user_input_id),
            created_at=event.created_at,
            event_type=type(event).__name__,
            event=event.model_dump(mode="json"),
        )
        self._session.add(trace)

    def get_all(
        self, page: int = 0, page_size: int = 100, mas_id: UUID | None = None, fetch_all: bool = False
    ) -> TraceList:
        """Retrieve traces for all source app calls using pagination."""
        mas_filter = Trace.event["mas_id"].as_string() == str(mas_id) if mas_id is not None else True  # type: ignore[assignment]
        group_by_qry = (
            select(Trace.user_input_id, func.max(Trace.created_at).label("created_at"))
            .where(mas_filter)
            .group_by(Trace.user_input_id)
            .subquery()
        )
        paginated_qry = select(group_by_qry.c.user_input_id).order_by(desc(group_by_qry.c.created_at))
        if not fetch_all:
            paginated_qry = paginated_qry.offset((page - 1) * page_size).limit(page_size)
        total_qry = select(func.count()).select_from(group_by_qry)
        traces_qry = select(Trace).filter(Trace.user_input_id.in_(paginated_qry)).order_by(desc(Trace.created_at))  # type: ignore[union-attr]
        if mas_id is not None:
            traces_qry = traces_qry.where(Trace.event["mas_id"].as_string() == str(mas_id))
        traces = self._session.exec(traces_qry).all()
        total = self._session.exec(total_qry).one()

        items: dict[str, list[Trace]] = defaultdict(list)
        for trace in traces:
            items[str(trace.user_input_id)].append(trace)

        for id in items:
            items[id].sort(key=lambda t: t.created_at)

        return TraceList(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_traces_by_user_input_and_event_type(self, user_input_id: str, event_type: str) -> list[Trace]:
        """Retrieve traces for a specific user input and event type."""
        traces = self._session.exec(select(Trace).filter_by(user_input_id=user_input_id, event_type=event_type)).all()
        return traces
