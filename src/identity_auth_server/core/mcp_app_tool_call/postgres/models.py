"""SQLAlchemy models for MCP app tool calls and blocked by types."""

from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, String, Text

from identity_auth_server.database.postgres.postgres import Base


class BlockedByTypeModel(Base):
    """SQLAlchemy model representing reasons a tool call might be blocked."""

    __tablename__ = "blocked_by_types"

    id = Column(UUID, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)


class McpAppToolCallModel(Base):
    """SQLAlchemy model for the mcp_app_tool_calls table."""

    __tablename__ = "mcp_app_tool_calls"

    id = Column(UUID, primary_key=True)
    source_app_call_id = Column(UUID, ForeignKey("source_app_calls.id", ondelete="CASCADE"), nullable=False)
    llm_app_call_id = Column(UUID, ForeignKey("llm_app_calls.id", ondelete="SET NULL"), nullable=True)
    llm_app_response_id = Column(UUID, ForeignKey("llm_app_responses.id", ondelete="SET NULL"), nullable=True)
    blocked_by_type_id = Column(UUID, ForeignKey("blocked_by_types.id", ondelete="SET NULL"), nullable=True)
    token = Column(String(255), nullable=False)
    tool = Column(Text, nullable=False)
    blocked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False)
