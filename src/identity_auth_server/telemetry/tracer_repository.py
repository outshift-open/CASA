"""Tracer repository implementation"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlmodel import JSON, Column, Field, Session, SQLModel

from identity_auth_server.core.events import BaseEvent


class Trace(SQLModel, table=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_input_id: Optional[UUID] = Field(foreign_key="userinput.id")
    created_at: datetime = datetime.now(timezone.utc)
    event_type: str
    event: Dict[str, Any] = Field(sa_column=Column(JSON))


class TracerRepository(ABC):
    """Interface exposing the methods of TracerRepository."""

    @abstractmethod
    def store_event(self, event):
        """Stores an event in the database."""


class TracerPostgresRepository(TracerRepository):
    """Postgre implementation of TracerRepository."""

    def __init__(self, session: Session):
        self._session = session

    def store_event(self, event: BaseEvent):
        """Stores an event in the database."""
        # event.model_dump(mode="json")
        trace = Trace(
            id=event.id,
            user_input_id=UUID(event.user_input_id),
            created_at=event.created_at,
            event_type=type(event).__name__,
            event=event.model_dump(mode="json"),
        )
        self._session.add(trace)
        # TODO: call commit only once in the session factory
        # self._session.flush()
        self._session.commit()
        self._session.refresh(trace)
