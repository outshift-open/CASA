"""Kubernetes CRD models for CASA Multi-Agent System."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from casa_auth_server.core.types import AppType


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


class AppSpecBaseUrl(BaseModel):
    """Base URL split into host and scheme, matching the CRD schema."""

    host: str = Field(description="Host (and optional port) of the URL, e.g. my-app:8080")
    scheme: str = Field(description="URL scheme: http or https")

    def to_url(self) -> str:
        """Reconstruct the full URL string."""
        return f"{self.scheme}://{self.host}"

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class HttpRequestSchema(BaseModel):
    """HTTP request schema for extracting the prompt field."""

    prompt_field_json_path: str = Field(
        description="JSONPath to the prompt field in the HTTP request body", alias="promptFieldJsonPath"
    )

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class AppSpec(BaseModel):
    """Application specification within a MultiAgentSystem."""

    name: str = Field(description="Name of the application")
    type: AppType = Field(description="Type of the application")
    base_url: "AppSpecBaseUrl" = Field(description="Base URL of the application", alias="baseUrl")
    kubernetes_workload_name: Optional[str] = Field(
        default=None, description="Name of the Kubernetes workload running the app", alias="kubernetesWorkloadName"
    )
    http_request_schema: Optional[HttpRequestSchema] = Field(
        default=None, description="HTTP request schema for extracting the prompt field", alias="httpRequestSchema"
    )

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class MultiAgentSystemSpec(BaseModel):
    """Specification for MultiAgentSystem CRD."""

    name: str = Field(description="Display name of the Multi-Agent System")
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
    llm_host: Optional[str] = Field(default=None, description="LLM proxy host for outbound LLM call tracking")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class AppCredentials(BaseModel):
    """OAuth2 credentials for an application."""

    app_name: str = Field(description="Name of the application", alias="appName")
    app_id: str = Field(description="Application UUID", alias="appId")
    client_id: str = Field(description="OAuth2 client ID", alias="clientId")
    client_secret: str = Field(description="OAuth2 client secret", alias="clientSecret")
    secret_name: str = Field(description="Name of the K8s secret to create", alias="secretName")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class MultiAgentSystemStatus(BaseModel):
    """Status of MultiAgentSystem CRD."""

    phase: MASPhase = Field(default=MASPhase.PENDING, description="Current phase of the MAS")
    apps_ready: int = Field(default=0, description="Number of apps successfully registered", alias="appsReady")
    last_sync_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: Optional[str] = Field(default=None, description="Human-readable status message")
    credentials: Optional[List[AppCredentials]] = Field(
        default=None, description="OAuth2 credentials for each app (used by operator to create secrets)"
    )

    class Config:
        """Pydantic model configuration."""

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
        """Pydantic model configuration."""

        populate_by_name = True


class MultiAgentSystemCRD(BaseModel):
    """Complete MultiAgentSystem Custom Resource Definition."""

    api_version: str = Field(default="casa.io/v1alpha1", description="API version", alias="apiVersion")
    kind: Literal["MultiAgentSystem"] = Field(default="MultiAgentSystem", description="Resource kind")
    metadata: MultiAgentSystemMetadata
    spec: MultiAgentSystemSpec
    status: Optional[MultiAgentSystemStatus] = Field(default=None, description="Resource status")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class MASCreateRequest(BaseModel):
    """Request model for creating a MultiAgentSystem via API."""

    metadata: MultiAgentSystemMetadata
    spec: MultiAgentSystemSpec
