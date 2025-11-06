"""SQLAlchemy model for the source_app_responses table."""

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Text

from identity_auth_server.database.postgres.postgres import Base


class SourceAppResponseModel(Base):
    """SQLAlchemy model for source app responses."""

    __tablename__ = "source_app_responses"

    id = Column(UUID, primary_key=True)
    source_app_call_id = Column(UUID, ForeignKey("source_app_calls.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), nullable=False)
    output = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
