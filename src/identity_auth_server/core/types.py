"""Data models for AS."""

from datetime import date
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

# pylint: disable=too-few-public-methods

######### APP TYPES #########


class AppType(str, Enum):
    """Enumeration of app types."""

    AGENT = "agent"
    MCP_SERVER = "mcp_server"


class Tool(SQLModel, table=True):
    """MCP Tool model."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str
    input_schema: str
    output_schema: str
    app_id: Optional[UUID] = Field(foreign_key="app.id")
    apps: Optional["App"] = Relationship(back_populates="tools")


class App(SQLModel, table=True):
    """Input model for creating an app."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    type: str
    name: str
    authorization_server_id: Optional[UUID] = Field(foreign_key="authorizationserver.id")
    authorization_server: Optional["AuthorizationServer"] = Relationship(back_populates="apps")
    client_credentials_id: Optional[UUID] = Field(foreign_key="clientcredentials.id")
    client_credentials: Optional["ClientCredentials"] = Relationship(back_populates="apps")
    tools: List["Tool"] = Relationship(back_populates="apps")


######### APP TYPES #########

######### AS TYPES #########


class AuthorizationServer(SQLModel, table=True):
    """SQLModel an authorization server.

    Represents an authorization server with a unique realm.
    """

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    realm: str
    client_credentials: List["ClientCredentials"] = Relationship(back_populates="authorization_server")
    apps: List[App] = Relationship(back_populates="authorization_server")


class ClientCredentials(SQLModel, table=True):
    """SQLModel for client credentials."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    authorization_server_id: Optional[UUID] = Field(foreign_key="authorizationserver.id")
    authorization_server: Optional["AuthorizationServer"] = Relationship(back_populates="client_credentials")
    client_id: str
    client_secret: Optional[str] = Field(default=None)
    tokens: List["Token"] = Relationship(back_populates="client_credential")
    apps: List[App] = Relationship(back_populates="client_credentials")


class Token(SQLModel, table=True):
    """Pydantic model for a token."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    client_credential_id: Optional[UUID] = Field(foreign_key="clientcredentials.id")
    client_credential: Optional["ClientCredentials"] = Relationship(back_populates="tokens")
    value: str  # This will be hashed
    expires_at: date


class TokenRequestParams(SQLModel):
    """Pydantic model for the token parameters."""

    app: App
    grant_type: str
    tools: List[Tool] = []
    act: App | None = None  # Act on behalf of another app
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


class AppMetadataResponse(SQLModel):
    """Pydantic model for app metadata response."""

    client_id: str
    client_name: str
    grant_types: list[str]
    response_types: list[str]
    token_endpoint_auth_method: str
    jwks_uri: str


######### AS TYPES #########
