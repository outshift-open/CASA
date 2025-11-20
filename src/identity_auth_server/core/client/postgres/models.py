"""SQLAlchemy model for the clients table."""

from sqlalchemy import UUID, Column, DateTime, String

from identity_auth_server.database.postgres.postgres import Base


class ClientModel(Base):
    """SQLAlchemy model for the clients table."""

    __tablename__ = "clients"

    id = Column(UUID, primary_key=True)
    client_id = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    secret = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
