"""SQLAlchemy model for the source_app_calls table."""

from sqlalchemy import UUID, Column, DateTime, String

from identity_auth_server.database.postgres.postgres import Base


class SourceAppCallModel(Base):
    """SQLAlchemy model for the source_app_calls table."""

    __tablename__ = "source_app_calls"

    id = Column(UUID, primary_key=True)
    token = Column(String, nullable=False)
    input = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
