"""Data models for AS."""

from datetime import date, datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

# pylint: disable=too-few-public-methods

######### APP TYPES #########


class AppType(str, Enum):
    """Enumeration of app types."""

    # Untrusted agents
    AGENT = "agent"

    # Trusted clients
    CLIENT = "client"

    # Trusted MCP servers
    MCP_SERVER = "mcp_server"


class Tool(SQLModel, table=True):  # type: ignore[call-arg]
    """MCP Tool model."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str
    input_schema: str
    output_schema: str
    app_id: Optional[UUID] = Field(foreign_key="app.id")
    app: Optional["App"] = Relationship(back_populates="tools")


class App(SQLModel, table=True):  # type: ignore[call-arg]
    """Input model for creating an app."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    type: str
    name: str
    base_url: str
    authorization_server_id: Optional[UUID] = Field(foreign_key="authorizationserver.id")
    authorization_server: Optional["AuthorizationServer"] = Relationship(back_populates="apps")
    client_credentials_id: Optional[UUID] = Field(foreign_key="clientcredentials.id")
    client_credentials: Optional["ClientCredentials"] = Relationship(back_populates="apps")
    tools: List["Tool"] = Relationship(back_populates="app")


######### APP TYPES #########


######### User Input TYPES #########
class UserInput(SQLModel, table=True):  # type: ignore[call-arg]
    """User Input model containing the user input prompt."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    prompt: str
    created_at: datetime = datetime.now(timezone.utc)
    app_id: Optional[UUID] = Field(foreign_key="app.id")


######### AS TYPES #########


class AuthorizationServer(SQLModel, table=True):  # type: ignore[call-arg]
    """SQLModel an authorization server.

    Represents an authorization server with a unique realm.
    """

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    realm: str
    client_credentials: List["ClientCredentials"] = Relationship(back_populates="authorization_server")
    apps: List[App] = Relationship(back_populates="authorization_server")


class ClientCredentials(SQLModel, table=True):  # type: ignore[call-arg]
    """SQLModel for client credentials."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    authorization_server_id: Optional[UUID] = Field(foreign_key="authorizationserver.id")
    authorization_server: Optional["AuthorizationServer"] = Relationship(back_populates="client_credentials")
    client_id: str
    client_secret: Optional[str] = Field(default=None)
    tokens: List["Token"] = Relationship(back_populates="client_credential")
    apps: List[App] = Relationship(back_populates="client_credentials")


class Token(SQLModel, table=True):  # type: ignore[call-arg]
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


class ActorClaim(BaseModel):
    """Pydantic model for the JWT 'act' (actor) claim.

    Represents an actor in a delegation chain. Can be nested to represent
    a chain of delegation where the outermost act claim represents the
    current actor and nested act claims represent prior actors.

    As per RFC 8693, for access control decisions, only the top-level
    claims and the current actor (outermost act claim) should be considered.
    """

    sub: str  # Subject identifier of the actor
    act: Optional["ActorClaim"] = None  # Nested actor claim for delegation chains


class TokenResponse(SQLModel):
    """Pydantic model for the token response."""

    access_token: str


class TokenIntrospectResponse(BaseModel):
    """Pydantic model for the token introspection response."""

    client_id: Optional[str] = None
    scope: Optional[str] = None
    sub: Optional[str] = None
    act: Optional[ActorClaim] = None
    other: Optional[dict] = None
    exp: Optional[int] = None
    user_input_id: Optional[str] = None
    app_id: Optional[str] = None
    tools: Optional[list[str]] = None
    active: bool


class AppMetadataResponse(SQLModel):
    """Pydantic model for app metadata response."""

    client_id: str
    client_name: str
    grant_types: list[str]
    response_types: list[str]
    token_endpoint_auth_method: str
    jwks_uri: str


######### AS TYPES #########
