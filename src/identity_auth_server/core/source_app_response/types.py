"""Data models for source app responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SourceAppResponseInput(BaseModel):
    """Input model for creating a source app response."""

    token: str
    source_app_call_token: str
    output: str


class SourceAppResponse(BaseModel):
    """Data model for a source app response."""

    id: UUID
    source_app_call_id: UUID
    token: str
    output: str
    created_at: datetime
