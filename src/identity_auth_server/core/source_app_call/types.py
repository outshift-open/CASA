"""Data models for source app calls."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SourceAppCallInput(BaseModel):
    """Input model for creating a source app call."""

    token: str
    input: str


class SourceAppCall(BaseModel):
    """Data model for a source app call."""

    id: UUID
    token: str | None = None
    input: str
    created_at: datetime
