"""Tracer repository implementation."""

from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict
from sqlmodel import JSON, Column, Field, Session, SQLModel, desc, func, select

from identity_auth_server.core.events import BaseEvent


class Trace(SQLModel, table=True):
    """SQLModel for storing event traces."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_input_id: Optional[UUID] = Field(foreign_key="userinput.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    event_type: str
    event: Dict[str, Any] = Field(sa_column=Column(JSON))


class TraceList(BaseModel):
    """Paginated list of events."""

    items: Dict[str, List[Trace]]
    total: int
    page: int
    page_size: int


class TracerRepository(ABC):
    """Interface exposing the methods of TracerRepository."""

    @abstractmethod
    def store_event(self, event):
        """Stores an event in the database."""

    @abstractmethod
    def get_all(self, page: int, page_size: int) -> TraceList:
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

    def get_all(self, page: int = 0, page_size: int = 100) -> TraceList:
        """Retrieve traces for all source app calls using pagination."""
        group_by_qry = (
            select(Trace.user_input_id, func.max(Trace.created_at).label("created_at"))
            .group_by(Trace.user_input_id)
            .subquery()
        )
        paginated_qry = (
            select(group_by_qry.c.user_input_id)
            .order_by(desc(group_by_qry.c.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        total_qry = select(func.count()).select_from(group_by_qry)
        traces = self._session.exec(
            select(Trace).filter(Trace.user_input_id.in_(paginated_qry)).order_by(desc(Trace.created_at))
        ).all()
        total = self._session.exec(total_qry).one()

        items: Dict[str, List[Trace]] = defaultdict(list)
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
