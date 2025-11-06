"""Service layer for sessions."""

from abc import ABC, abstractmethod

from identity_auth_server.core.session.repository import SessionRepository
from identity_auth_server.core.session.types import (
    SessionLlmAppInput,
    SessionLlmAppOutput,
    SessionMcpAppInput,
    SessionMcpAppOutput,
    SessionSourceAppInput,
    SessionSourceAppOutput,
)


class SessionService(ABC):
    """Interface defining trace service methods."""

    def __init__(self, session_repository: SessionRepository):
        """Initialize the service with a session repository."""
        self.session_repository = session_repository

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


class SessionServiceImpl(SessionService):
    """Concrete implementation of SessionService."""

    def __init__(self, session_repository: SessionRepository):
        """Store the backing session repository."""
        super().__init__(session_repository)

    def create_source_app_session(self, input: SessionSourceAppInput) -> str:
        """Create a new source app session and return its token."""
        return self.session_repository.create_source_app_session(input)

    def create_llm_app_session(self, input: SessionLlmAppInput) -> str:
        """Create a new llm app session and return its token."""
        return self.session_repository.create_llm_app_session(input)

    def create_mcp_app_session(self, input: SessionMcpAppInput) -> str:
        """Create a new mcp app session and return its token."""
        return self.session_repository.create_mcp_app_session(input)

    def validate_source_app_call_token(self, source_app_call_token: str) -> SessionSourceAppOutput:
        """Validate a source app call token."""
        return self.session_repository.validate_source_app_call_token(source_app_call_token)

    def validate_llm_app_call_token(self, llm_app_call_token: str) -> SessionLlmAppOutput:
        """Validate an llm app call token."""
        return self.session_repository.validate_llm_app_call_token(llm_app_call_token)

    def validate_mcp_app_call_token(self, mcp_app_call_token: str) -> SessionMcpAppOutput:
        """Validate an mcp app call token."""
        return self.session_repository.validate_mcp_app_call_token(mcp_app_call_token)
