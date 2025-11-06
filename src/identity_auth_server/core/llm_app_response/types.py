"""Data models for llm app responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LlmAppResponseInput(BaseModel):
    """Input model for creating an LLM app response."""

    token: str
    source_app_call_token: str
    proxy_call_id: str
    message: str
    tool_calls: str


class LlmAppResponse(BaseModel):
    """Data model for an LLM app response."""

    id: UUID
    llm_app_call_id: UUID
    token: str | None = None
    proxy_call_id: str
    message: str
    tool_calls: str
    created_at: datetime
