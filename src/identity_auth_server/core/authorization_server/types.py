"""Data models for AS."""

from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from identity_auth_server.core.authorization_server.types import App

# pylint: disable=too-few-public-methods


class AuthorizationServer(SQLModel, table=True):
    """SQLModel an authorization server.

    Represents an authorization server with a unique realm.
    """

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    realm: str
    client_credentials: List["ClientCredentials"] = Relationship(back_populates="authorization_server")
    apps: List["App"] = Relationship(back_populates="authorization_server")


class ClientCredentials(SQLModel, table=True):
    """SQLModel for client credentials."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    authorization_server_id: str = Field(foreign_key="authorizationserver.id")
    authorization_server: Optional[AuthorizationServer] = Relationship(back_populates="client_credentials")
    client_id: str
    client_secret: str
    tokens: List["Token"] = Relationship(back_populates="client_credential")
    apps: List[App] = Relationship(back_populates="client_credentials")


class Token(SQLModel, table=True):
    """Pydantic model for a token."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    client_credential_id: str = Field(foreign_key="clientcredentials.id")
    client_credential: Optional[ClientCredentials] = Relationship(back_populates="tokens")
    value: str  # This will be hashed
    expires_at: str


class ActorClaim(SQLModel):
    """Pydantic model for the JWT 'act' (actor) claim.

    Represents an actor in a delegation chain. Can be nested to represent
    a chain of delegation where the outermost act claim represents the
    current actor and nested act claims represent prior actors.

    As per RFC 8693, for access control decisions, only the top-level
    claims and the current actor (outermost act claim) should be considered.
    """

    sub: str  # Subject identifier of the actor
    act: Optional["ActorClaim"] = None  # Nested actor claim for delegation chains


class TokenRequestParams(SQLModel):
    """Pydantic model for the token parameters."""

    client_id: str
    grant_type: str
    scopes: list[str] | None = None
    sub: str | None = None
    act: ActorClaim | None = None
    other: dict | None = None


class TokenIntrospectParams(SQLModel):
    """Pydantic model for the token introspection parameters."""

    token: str


class TokenResponse(SQLModel):
    """Pydantic model for the token response."""

    access_token: str


class TokenIntrospectResponse(SQLModel):
    """Pydantic model for the token introspection response."""

    client_id: str | None = None
    scope: str | None = None
    sub: str | None = None
    act: str | None = None
    other: dict | None = None
    exp: int | None = None
