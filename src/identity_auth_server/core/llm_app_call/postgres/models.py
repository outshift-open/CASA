"""SQLAlchemy model for the llm_app_calls table."""

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Text

from identity_auth_server.database.postgres.postgres import Base


class LlmAppCallModel(Base):
    """SQLAlchemy model for the llm_app_calls table."""

    __tablename__ = "llm_app_calls"

    id = Column(UUID, primary_key=True)
    source_app_call_id = Column(UUID, ForeignKey("source_app_calls.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), nullable=False)
    proxy_call_id = Column(String(255), nullable=False, unique=True)
    messages = Column(Text, nullable=False)
    tools = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
