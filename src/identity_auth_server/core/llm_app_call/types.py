"""Data models for llm app calls."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LlmAppCallInput(BaseModel):
    """Input model for creating an LLM app call."""

    token: str
    source_app_call_token: str
    proxy_call_id: str
    messages: str
    tools: str


class LlmAppCall(BaseModel):
    """Data model for an LLM app call."""

    id: UUID
    source_app_call_id: UUID
    token: str | None = None
    proxy_call_id: str
    messages: str
    tools: str
    created_at: datetime
