"""Data models for apps."""

from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from identityservice.badge.mcp import McpTool
from sqlmodel import Field, Relationship, SQLModel

from identity_auth_server.core.authorization_server.types import (
    AuthorizationServer, ClientCredentials)

# pylint: disable=too-few-public-methods


class AppType(str, Enum):
    """Enumeration of app types."""

    AGENT = "agent"
    MCP_SERVER = "mcp_server"


class App(SQLModel, table=True):
    """Input model for creating an app."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    type: AppType
    name: str
    tools: List[McpTool] = []
    authorization_server_id: str = Field(foreign_key="authorizationserver.id")
    authorization_server: Optional["AuthorizationServer"] = Relationship(back_populates="apps")
    client_credentials_id: str = Field(foreign_key="clientcredentials.id")
    client_credentials: Optional["ClientCredentials"] = Relationship(back_populates="apps")
