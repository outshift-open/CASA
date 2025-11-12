"""SQLAlchemy models for tokens."""

from sqlalchemy import UUID, Column, String

from identity_auth_server.database.postgres.postgres import Base


class TokenModel(Base):
    """SQLAlchemy model backing the tokens table."""

    __tablename__ = "tokens"

    id = Column(UUID, primary_key=True)
    token = Column(String, nullable=False)
