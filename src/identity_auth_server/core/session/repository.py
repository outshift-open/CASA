"""Repository interface for Session."""

from abc import ABC, abstractmethod

from identity_auth_server.core.session.types import (
    SessionLlmAppInput,
    SessionLlmAppOutput,
    SessionMcpAppInput,
    SessionMcpAppOutput,
    SessionSourceAppInput,
    SessionSourceAppOutput,
)


class SessionRepository(ABC):
    """Interface for SessionRepository."""

    @abstractmethod
    def create_source_app_session(self, input: SessionSourceAppInput) -> str:
        """Create a new source app session and return its token."""
        pass

    @abstractmethod
    def create_llm_app_session(self, input: SessionLlmAppInput) -> str:
        """Create a new llm app session and return its token."""
        pass

    @abstractmethod
    def create_mcp_app_session(self, input: SessionMcpAppInput) -> str:
        """Create a new mcp app session and return its token."""
        pass

    @abstractmethod
    def validate_source_app_call_token(self, source_app_call_token: str) -> SessionSourceAppOutput:
        """Validate a source app call token."""
        pass

    @abstractmethod
    def validate_llm_app_call_token(self, llm_app_call_token: str) -> SessionLlmAppOutput:
        """Validate an llm app call token."""
        pass

    @abstractmethod
    def validate_mcp_app_call_token(self, mcp_app_call_token: str) -> SessionMcpAppOutput:
        """Validate an mcp app call token."""
        pass
