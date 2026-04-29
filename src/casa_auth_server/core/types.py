# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Data models for AS."""

# mypy: disable-error-code="call-arg"

from datetime import UTC, datetime
from enum import Enum, IntFlag
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import DateTime
from sqlalchemy.orm import RelationshipProperty
from sqlmodel import Column, Field, Integer, Relationship, SQLModel


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

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str
    input_schema: str
    output_schema: str
    app_id: UUID | None = Field(foreign_key="app.id")
    app: Optional["App"] = Relationship(back_populates="tools")
    scopes: list["Scope"] = Relationship(
        back_populates="tools",
        link_model=ToolScope,
    )


class Scope(SQLModel, table=True):
    """Scope model."""

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)
    mas_id: UUID | None = Field(foreign_key="multiagentsystem.id")
    mas: Optional["MultiAgentSystem"] = Relationship(back_populates="scopes")
    tools: list[Tool] = Relationship(
        back_populates="scopes",
        link_model=ToolScope,
    )


class ToolCheckFlags(IntFlag):
    """Bitmask flags controlling which tool authorization checks are enabled on a MAS."""

    NONE = 0
    DETERMINISTIC_TOOL_SELECTED = 1 << 0
    DETERMINISTIC_LLM_SELECTED_TOOLS = 1 << 1
    AI_POWERED_TOOL_MATCH = 1 << 2


class App(SQLModel, table=True):
    """ORM model representing a registered application."""

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    type: str
    name: str
    base_url: str
    client_credentials: Optional["ClientCredentials"] = Relationship(
        sa_relationship=RelationshipProperty(
            "ClientCredentials", back_populates="app", uselist=False, foreign_keys="ClientCredentials.app_id"
        )
    )
    tools: list["Tool"] = Relationship(back_populates="app")
    mas_id: UUID | None = Field(foreign_key="multiagentsystem.id")
    mas: Optional["MultiAgentSystem"] = Relationship(back_populates="apps")
    deleted_at: datetime | None = Field(default=None)


class MultiAgentSystem(SQLModel, table=True):
    """An entity describing a multi agent system, which is a set of apps."""

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str
    k8s_name: str | None = None  # Kubernetes metadata.name (lowercase with dashes)
    apps: list["App"] = Relationship(back_populates="mas")
    scopes: list["Scope"] = Relationship(back_populates="mas")
    enabled_tool_checks: ToolCheckFlags | None = Field(
        default=ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED
        | ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS
        | ToolCheckFlags.AI_POWERED_TOOL_MATCH,
        sa_column=Column(Integer, nullable=False),
    )
    authorization_server_id: UUID | None = Field(foreign_key="authorizationserver.id")
    authorization_server: Optional["AuthorizationServer"] = Relationship(back_populates="multi_agent_systems")
    namespace: str | None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    deleted_at: datetime | None = Field(default=None)


class UserInput(SQLModel, table=True):
    """User Input model containing the user input prompt."""

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    prompt: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    app_id: UUID | None = Field(foreign_key="app.id")
    tag: str | None = Field(index=True)


class AuthorizationServer(SQLModel, table=True):
    """SQLModel an authorization server.

    Represents an authorization server with a unique realm.
    """

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    realm: str
    client_credentials: list["ClientCredentials"] = Relationship(
        back_populates="authorization_server", cascade_delete=True
    )
    multi_agent_systems: list[MultiAgentSystem] = Relationship(back_populates="authorization_server")


class ClientCredentials(SQLModel, table=True):
    """SQLModel for client credentials."""

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str
    authorization_server_id: UUID | None = Field(foreign_key="authorizationserver.id")
    authorization_server: Optional["AuthorizationServer"] = Relationship(back_populates="client_credentials")
    app_id: UUID | None = Field(foreign_key="app.id")
    app: Optional["App"] = Relationship(
        sa_relationship=RelationshipProperty("App", back_populates="client_credentials")
    )
    client_id: str
    client_secret: str | None = Field(default=None)


class TokenRequestParams(SQLModel):
    """Pydantic model for the token parameters."""

    app: App
    grant_type: str
    tools: list[Tool] = []
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

    client_id: str | None = None
    scope: str | None = None
    sub: str | None = None
    act: ActorClaim | None = None
    other: dict | None = None
    exp: int | None = None
    user_input_id: str | None = None
    app_id: str | None = None
    mas_id: str | None = None
    tools: list[str] | None = None
    active: bool


class AppMetadataResponse(SQLModel):
    """Pydantic model for app metadata response."""

    client_id: str
    client_name: str
    grant_types: list[str]
    response_types: list[str]
    token_endpoint_auth_method: str
    jwks_uri: str
