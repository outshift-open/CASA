"""SQLAlchemy models for session tracking."""

from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint

from identity_auth_server.database.postgres.postgres import Base


class SourceAppCallSessionModel(Base):
    """SQLAlchemy model backing the source_app_call_sessions table."""

    __tablename__ = "source_app_call_sessions"
    __table_args__ = (UniqueConstraint("token", name="uq_source_app_call_sessions_token"),)

    id = Column(UUID, primary_key=True)
    token = Column(String, nullable=False)
    input = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


class LlmAppCallSessionModel(Base):
    """SQLAlchemy model backing the llm_app_call_sessions table."""

    __tablename__ = "llm_app_call_sessions"
    __table_args__ = (UniqueConstraint("token", name="uq_llm_app_call_sessions_token"),)

    id = Column(UUID, primary_key=True)
    source_app_call_session_id = Column(UUID, ForeignKey("source_app_call_sessions.id"), nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


class McpAppCallSessionModel(Base):
    """SQLAlchemy model backing the mcp_app_call_sessions table."""

    __tablename__ = "mcp_app_call_sessions"
    __table_args__ = (UniqueConstraint("token", name="uq_mcp_app_call_sessions_token"),)

    id = Column(UUID, primary_key=True)
    source_app_call_session_id = Column(UUID, ForeignKey("source_app_call_sessions.id"), nullable=False)
    llm_app_call_session_id = Column(UUID, ForeignKey("llm_app_call_sessions.id"), nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


class SourceAppCallSessionToolModel(Base):
    """SQLAlchemy model backing the source_app_call_session_tools table."""

    __tablename__ = "source_app_call_session_tools"
    __table_args__ = (UniqueConstraint("source_app_call_session_id", "tool", name="uq_source_app_call_session_tool"),)

    id = Column(UUID, primary_key=True)
    source_app_call_session_id = Column(UUID, ForeignKey("source_app_call_sessions.id"), nullable=False)
    tool = Column(String, nullable=False)
    approved = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
