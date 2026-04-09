"""Kubernetes CRD models for ZTA Multi-Agent System."""

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AppTypeK8s(str, Enum):
    """Enumeration of app types for K8s CRD."""

    AGENT = "agent"
    CLIENT = "client"
    MCP_SERVER = "mcp_server"


class ToolCheckType(str, Enum):
    """Tool check types supported in MAS."""

    DETERMINISTIC_TOOL_SELECTED = "DETERMINISTIC_TOOL_SELECTED"
    DETERMINISTIC_LLM_SELECTED_TOOLS = "DETERMINISTIC_LLM_SELECTED_TOOLS"
    AI_POWERED_TOOL_MATCH = "AI_POWERED_TOOL_MATCH"


class MASPhase(str, Enum):
    """Phase of MAS resource lifecycle."""

    PENDING = "Pending"
    ACTIVE = "Active"
    FAILED = "Failed"


class AppSpec(BaseModel):
    """Application specification within a MultiAgentSystem."""

    name: str = Field(description="Name of the application")
    type: AppTypeK8s = Field(description="Type of the application")
    base_url: str = Field(description="Base URL of the application", alias="baseUrl")

    class Config:
        populate_by_name = True


class MultiAgentSystemSpec(BaseModel):
    """Specification for MultiAgentSystem CRD."""

    name: str = Field(description="Display name of the Multi-Agent System")
    authorization_server: str = Field(description="Keycloak realm name for this MAS", alias="authorizationServer")
    enabled_tool_checks: List[ToolCheckType] = Field(
        default_factory=lambda: [
            ToolCheckType.DETERMINISTIC_TOOL_SELECTED,
            ToolCheckType.DETERMINISTIC_LLM_SELECTED_TOOLS,
            ToolCheckType.AI_POWERED_TOOL_MATCH,
        ],
        description="List of enabled tool check types",
        alias="enabledToolChecks",
    )
    apps: List[AppSpec] = Field(default_factory=list, description="List of applications in this MAS")

    class Config:
        populate_by_name = True


class AppCredentials(BaseModel):
    """OAuth2 credentials for an application."""

    app_name: str = Field(description="Name of the application", alias="appName")
    client_id: str = Field(description="OAuth2 client ID", alias="clientId")
    client_secret: str = Field(description="OAuth2 client secret", alias="clientSecret")
    secret_name: str = Field(description="Name of the K8s secret to create", alias="secretName")

    class Config:
        populate_by_name = True


class MultiAgentSystemStatus(BaseModel):
    """Status of MultiAgentSystem CRD."""

    phase: MASPhase = Field(default=MASPhase.PENDING, description="Current phase of the MAS")
    apps_ready: int = Field(default=0, description="Number of apps successfully registered", alias="appsReady")
    last_sync_time: Optional[datetime] = Field(
        default=None, description="Last time the MAS was reconciled", alias="lastSyncTime"
    )
    message: Optional[str] = Field(default=None, description="Human-readable status message")
    credentials: Optional[List[AppCredentials]] = Field(
        default=None, description="OAuth2 credentials for each app (used by operator to create secrets)"
    )

    class Config:
        populate_by_name = True


class MultiAgentSystemMetadata(BaseModel):
    """Metadata for MultiAgentSystem CRD."""

    name: str = Field(description="Resource name")
    namespace: str = Field(description="Kubernetes namespace")
    uid: Optional[str] = Field(default=None, description="Kubernetes UID")
    resource_version: Optional[str] = Field(default=None, description="Resource version", alias="resourceVersion")
    generation: Optional[int] = Field(default=None, description="Generation number")
    labels: Optional[dict] = Field(default=None, description="Resource labels")
    annotations: Optional[dict] = Field(default=None, description="Resource annotations")

    class Config:
        populate_by_name = True


class MultiAgentSystemCRD(BaseModel):
    """Complete MultiAgentSystem Custom Resource Definition."""

    api_version: str = Field(default="zta.io/v1alpha1", description="API version", alias="apiVersion")
    kind: Literal["MultiAgentSystem"] = Field(default="MultiAgentSystem", description="Resource kind")
    metadata: MultiAgentSystemMetadata
    spec: MultiAgentSystemSpec
    status: Optional[MultiAgentSystemStatus] = Field(default=None, description="Resource status")

    class Config:
        populate_by_name = True


class ProtocolType(str, Enum):
    """Allowed protocol types."""

    MCP = "mcp"
    A2A = "a2a"
    HTTP = "http"


class TargetRefKind(str, Enum):
    """Kubernetes resource kinds that can be targeted."""

    DEPLOYMENT = "Deployment"
    STATEFULSET = "StatefulSet"
    POD = "Pod"


class TargetRef(BaseModel):
    """Reference to a Kubernetes resource."""

    kind: TargetRefKind = Field(description="Kind of Kubernetes resource")
    name: str = Field(description="Name of the resource")

    class Config:
        populate_by_name = True


class AllowedEndpoint(BaseModel):
    """Specification for an allowed network endpoint."""

    name: str = Field(description="Name of the service")
    namespace: str = Field(description="Namespace of the service")
    port: int = Field(description="Port number")

    class Config:
        populate_by_name = True


class LLMEndpoint(BaseModel):
    """External LLM endpoint configuration."""

    fqdn: str = Field(description="Fully qualified domain name of the LLM endpoint")
    port: int = Field(description="Port number")

    class Config:
        populate_by_name = True


class MASCreateRequest(BaseModel):
    """Request model for creating a MultiAgentSystem via API."""

    metadata: MultiAgentSystemMetadata
    spec: MultiAgentSystemSpec


class MASUpdateRequest(BaseModel):
    """Request model for updating a MultiAgentSystem via API."""

    spec: MultiAgentSystemSpec


class MASStatusUpdateRequest(BaseModel):
    """Request model for updating MAS status (used by operator)."""

    status: MultiAgentSystemStatus


class MASListResponse(BaseModel):
    """Response model for listing MultiAgentSystems."""

    api_version: str = Field(default="zta.io/v1alpha1", alias="apiVersion")
    kind: Literal["MultiAgentSystemList"] = Field(default="MultiAgentSystemList")
    items: List[MultiAgentSystemCRD]

    class Config:
        populate_by_name = True
