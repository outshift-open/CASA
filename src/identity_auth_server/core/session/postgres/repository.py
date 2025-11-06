"""PostgreSQL implementation of SessionRepository."""

import datetime
from uuid import UUID, uuid4

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.session.postgres.models import (
    LlmAppCallSessionModel,
    McpAppCallSessionModel,
    SourceAppCallSessionModel,
)
from identity_auth_server.core.session.repository import SessionRepository
from identity_auth_server.core.session.types import (
    SessionLlmAppInput,
    SessionLlmAppOutput,
    SessionMcpAppInput,
    SessionMcpAppOutput,
    SessionSourceAppInput,
    SessionSourceAppOutput,
)
from identity_auth_server.database.postgres.postgres import PostgresDB


class SessionPostgresRepository(SessionRepository):
    """PostgreSQL-backed session repository implementation."""

    def __init__(self, database: PostgresDB):
        """Initialize the repository with a database session."""
        self.database = database

    def create_source_app_session(self, input: SessionSourceAppInput) -> str:
        """Persist a source app session and return the generated token."""
        db_session = SourceAppCallSessionModel(
            id=uuid4(),
            token=self._generate_token(),
            input=input.input,
            created_at=self._current_time(),
        )

        with self.database.session_scope() as session:
            session.add(db_session)
            session.flush()
            session.refresh(db_session)

            return db_session.token

    def create_llm_app_session(self, input: SessionLlmAppInput) -> str:
        """Persist an LLM app session tied to an existing source session."""
        with self.database.session_scope() as session:
            source_session = (
                session.query(SourceAppCallSessionModel)
                .filter(SourceAppCallSessionModel.token == input.source_app_call_token)
                .one_or_none()
            )

            if source_session is None:
                raise ResourceNotFoundError(f"Source app session not found for token: {input.source_app_call_token}")

            db_session = LlmAppCallSessionModel(
                id=uuid4(),
                source_app_call_session_id=source_session.id,
                token=self._generate_token(),
                created_at=self._current_time(),
            )

            session.add(db_session)
            session.flush()
            session.refresh(db_session)

            return db_session.token

    def create_mcp_app_session(self, input: SessionMcpAppInput) -> str:
        """Persist an MCP app session tied to existing source and LLM sessions."""
        with self.database.session_scope() as session:
            source_session = (
                session.query(SourceAppCallSessionModel)
                .filter(SourceAppCallSessionModel.token == input.source_app_call_token)
                .one_or_none()
            )

            if source_session is None:
                raise ResourceNotFoundError(f"Source app session not found for token: {input.source_app_call_token}")

            llm_session = (
                session.query(LlmAppCallSessionModel)
                .filter(LlmAppCallSessionModel.token == input.llm_app_call_token)
                .one_or_none()
            )

            if llm_session is None:
                raise ResourceNotFoundError(f"LLM app session not found for token: {input.llm_app_call_token}")

            if llm_session.source_app_call_session_id != source_session.id:
                raise ValueError("LLM session does not belong to the provided source session")

            db_session = McpAppCallSessionModel(
                id=uuid4(),
                source_app_call_session_id=source_session.id,
                llm_app_call_session_id=llm_session.id,
                token=self._generate_token(),
                created_at=self._current_time(),
            )

            session.add(db_session)
            session.flush()
            session.refresh(db_session)

            return db_session.token

    def validate_source_app_call_token(self, source_app_call_token: str) -> SessionSourceAppOutput:
        """Validate that a source app session token exists."""
        with self.database.session_scope() as session:
            session_record = (
                session.query(SourceAppCallSessionModel)
                .filter(SourceAppCallSessionModel.token == source_app_call_token)
                .one_or_none()
            )

            if session_record is None:
                raise ResourceNotFoundError(f"Source app session not found for token: {source_app_call_token}")

            return SessionSourceAppOutput(valid=True)

    def validate_llm_app_call_token(self, llm_app_call_token: str) -> SessionLlmAppOutput:
        """Validate that an LLM app session token exists and return its associations."""
        with self.database.session_scope() as session:
            llm_session = (
                session.query(LlmAppCallSessionModel)
                .filter(LlmAppCallSessionModel.token == llm_app_call_token)
                .one_or_none()
            )

            if llm_session is None:
                raise ResourceNotFoundError(f"LLM app session not found for token: {llm_app_call_token}")

            source_session = self._load_source_session(session, llm_session.source_app_call_session_id)

            return SessionLlmAppOutput(valid=True, source_app_call_token=source_session.token)

    def validate_mcp_app_call_token(self, mcp_app_call_token: str) -> SessionMcpAppOutput:
        """Validate that an MCP app session token exists and return its associations."""
        with self.database.session_scope() as session:
            mcp_session = (
                session.query(McpAppCallSessionModel)
                .filter(McpAppCallSessionModel.token == mcp_app_call_token)
                .one_or_none()
            )

            if mcp_session is None:
                raise ResourceNotFoundError(f"MCP app session not found for token: {mcp_app_call_token}")

            source_session = self._load_source_session(session, mcp_session.source_app_call_session_id)
            llm_session = self._load_llm_session(session, mcp_session.llm_app_call_session_id)

            return SessionMcpAppOutput(
                valid=True,
                source_app_call_token=source_session.token,
                llm_app_call_token=llm_session.token,
            )

    @staticmethod
    def _generate_token() -> str:
        """Generate a random session token."""
        return uuid4().hex

    @staticmethod
    def _current_time() -> datetime.datetime:
        """Return the current UTC timestamp."""
        return datetime.datetime.now(datetime.timezone.utc)

    @staticmethod
    def _load_source_session(session, session_id: UUID) -> SourceAppCallSessionModel:
        """Load a source session by id, raising if absent."""
        source_session = (
            session.query(SourceAppCallSessionModel).filter(SourceAppCallSessionModel.id == session_id).one_or_none()
        )

        if source_session is None:
            raise ResourceNotFoundError(f"Source app session not found for id: {session_id}")

        return source_session

    @staticmethod
    def _load_llm_session(session, session_id: UUID) -> LlmAppCallSessionModel:
        """Load an LLM session by id, raising if absent."""
        llm_session = (
            session.query(LlmAppCallSessionModel).filter(LlmAppCallSessionModel.id == session_id).one_or_none()
        )

        if llm_session is None:
            raise ResourceNotFoundError(f"LLM app session not found for id: {session_id}")

        return llm_session
