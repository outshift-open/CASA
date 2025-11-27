"""SQLAlchemy models for tokens."""

from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import mapped_column, relationship

from identity_auth_server.database.postgres.postgres import Base


class ClientCredentialsModel(Base):
    """SQLAlchemy model for the client_credentials table."""

    __tablename__ = "client_credentials"

    id = Column(UUID, primary_key=True)
    authorization_server_id = mapped_column(ForeignKey("authorization_servers.id"))
    authorization_server = relationship("AuthorizationServerModel", back_populates="client_credentials")
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)


class AuthorizationServerModel(Base):
    """SQLAlchemy model for the authorization_servers table."""

    __tablename__ = "authorization_servers"

    id = Column(UUID, primary_key=True)
    realm = Column(String, nullable=False)


class TokenModel(Base):
    """SQLAlchemy model backing the tokens table."""

    __tablename__ = "tokens"

    id = Column(UUID, primary_key=True)
    client_credential_id = mapped_column(ForeignKey("client_credentials.id"))
    client_credential = relationship("ClientCredentialsModel", back_populates="tokens")
    value = Column(String, nullable=False)
    expires_at = Column(String, nullable=False)
