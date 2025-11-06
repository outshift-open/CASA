"""Data models for sessions."""

from pydantic import BaseModel


class SessionSourceAppInput(BaseModel):
    """Input model for creating a source session."""

    input: str


class SessionLlmAppInput(BaseModel):
    """Input model for creating an app session."""

    source_app_call_token: str


class SessionMcpAppInput(BaseModel):
    """Input model for creating an app session."""

    source_app_call_token: str
    llm_app_call_token: str


class SessionSourceAppOutput(BaseModel):
    """Output model for validating a source session."""

    valid: bool


class SessionLlmAppOutput(BaseModel):
    """Output model for validating an llm session."""

    valid: bool
    source_app_call_token: str


class SessionMcpAppOutput(BaseModel):
    """Output model for validating an mcp session."""

    valid: bool
    source_app_call_token: str
    llm_app_call_token: str
