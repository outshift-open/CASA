"""Data models for clients."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ClientInput(BaseModel):
    """Input model for creating a client."""

    client_id: str
    name: str
    secret: str | None = None


class Client(BaseModel):
    """Data model for a client."""

    id: UUID
    client_id: str
    name: str
    secret: str | None = None
    created_at: datetime
    updated_at: datetime
