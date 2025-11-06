"""SQLAlchemy model for the llm_app_responses table."""

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Text

from identity_auth_server.database.postgres.postgres import Base


class LlmAppResponseModel(Base):
    """SQLAlchemy model for the llm_app_responses table."""

    __tablename__ = "llm_app_responses"

    id = Column(UUID, primary_key=True)
    llm_app_call_id = Column(UUID, ForeignKey("llm_app_calls.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), nullable=False)
    proxy_call_id = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    tool_calls = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
