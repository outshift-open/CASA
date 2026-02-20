"""Data models for AS."""

# mypy: disable-error-code="call-arg"

from datetime import datetime, timezone
from enum import Enum, IntFlag
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy.orm import RelationshipProperty
from sqlmodel import Column, Field, Integer, Relationship, SQLModel

# pylint: disable=too-few-public-methods


class AppType(str, Enum):
    """Enumeration of app types."""

    # Untrusted agents
    AGENT = "agent"

    # Trusted clients
    CLIENT = "client"

    # Trusted MCP servers
    MCP_SERVER = "mcp_server"


class ToolScope(SQLModel, table=True):
    """Link table between Tool and Scope."""

    tool_id: UUID = Field(foreign_key="tool.id", primary_key=True)
    scope_id: UUID = Field(foreign_key="scope.id", primary_key=True)


class Tool(SQLModel, table=True):
    """MCP Tool model."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str
    input_schema: str
    output_schema: str
    app_id: Optional[UUID] = Field(foreign_key="app.id")
    app: Optional["App"] = Relationship(back_populates="tools")
    scopes: List["Scope"] = Relationship(
        back_populates="tools",
        link_model=ToolScope,
    )


class Scope(SQLModel, table=True):
    """Scope model."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)
    tools: List[Tool] = Relationship(
        back_populates="scopes",
        link_model=ToolScope,
    )


class ToolCheckFlags(IntFlag):
    NONE = 0
    DETERMINISTIC_TOOL_SELECTED = 1 << 0
    DETERMINISTIC_LLM_SELECTED_TOOLS = 1 << 1
    AI_POWERED_TOOL_MATCH = 1 << 2


class App(SQLModel, table=True):
    """Input model for creating an app."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    type: str
    name: str
    base_url: str
    client_credentials: Optional["ClientCredentials"] = Relationship(
        sa_relationship=RelationshipProperty(
            "ClientCredentials", back_populates="app", uselist=False, foreign_keys="ClientCredentials.app_id"
        )
    )
    tools: List["Tool"] = Relationship(back_populates="app")
    mas_id: Optional[UUID] = Field(foreign_key="multiagentsystem.id")
    mas: Optional["MultiAgentSystem"] = Relationship(back_populates="apps")


class MultiAgentSystem(SQLModel, table=True):
    """An entity describing a multi agent system, which is a set of apps."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    apps: List["App"] = Relationship(back_populates="mas")
    enabled_tool_checks: Optional[ToolCheckFlags] = Field(
        default=ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED
        | ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS
        | ToolCheckFlags.AI_POWERED_TOOL_MATCH,
        sa_column=Column(Integer, nullable=False),
    )
    authorization_server_id: Optional[UUID] = Field(foreign_key="authorizationserver.id")
    authorization_server: Optional["AuthorizationServer"] = Relationship(back_populates="multi_agent_systems")
    created_at: datetime = datetime.now(timezone.utc)


class UserInput(SQLModel, table=True):
    """User Input model containing the user input prompt."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    prompt: str
    created_at: datetime = datetime.now(timezone.utc)
    app_id: Optional[UUID] = Field(foreign_key="app.id")


class AuthorizationServer(SQLModel, table=True):
    """SQLModel an authorization server.

    Represents an authorization server with a unique realm.
    """

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    realm: str
    client_credentials: List["ClientCredentials"] = Relationship(
        back_populates="authorization_server", cascade_delete=True
    )
    multi_agent_systems: List[MultiAgentSystem] = Relationship(back_populates="authorization_server")


class ClientCredentials(SQLModel, table=True):
    """SQLModel for client credentials."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    authorization_server_id: Optional[UUID] = Field(foreign_key="authorizationserver.id")
    authorization_server: Optional["AuthorizationServer"] = Relationship(back_populates="client_credentials")
    app_id: Optional[UUID] = Field(foreign_key="app.id")
    app: Optional["App"] = Relationship(
        sa_relationship=RelationshipProperty("App", back_populates="client_credentials")
    )
    client_id: str
    client_secret: Optional[str] = Field(default=None)


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
