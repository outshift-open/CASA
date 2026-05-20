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

"""Kubernetes CRD models for CASA (MultiAgentSystem and CASAPolicy)."""

from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from casa_auth_server.core.types import AppType


class ToolCheckType(str, Enum):
    """Tool check types supported in MAS."""

    DETERMINISTIC_TOOL_SELECTED = "DETERMINISTIC_TOOL_SELECTED"
    DETERMINISTIC_LLM_SELECTED_TOOLS = "DETERMINISTIC_LLM_SELECTED_TOOLS"
    AI_POWERED_TOOL_MATCH = "AI_POWERED_TOOL_MATCH"


class CRDPhase(str, Enum):
    """Phase of a CASA CRD resource lifecycle."""

    PENDING = "Pending"
    ACTIVE = "Active"
    FAILED = "Failed"


class AppSpecBaseUrl(BaseModel):
    """Base URL split into host and scheme, matching the CRD schema."""

    model_config = ConfigDict(populate_by_name=True)

    host: str = Field(description="Host (and optional port) of the URL, e.g. my-app:8080")
    scheme: str = Field(description="URL scheme: http or https")

    def to_url(self) -> str:
        """Reconstruct the full URL string."""
        return f"{self.scheme}://{self.host}"


class HttpRequestSchema(BaseModel):
    """HTTP request schema for extracting the prompt field."""

    model_config = ConfigDict(populate_by_name=True)

    prompt_field_json_path: str = Field(
        description="JSONPath to the prompt field in the HTTP request body", alias="promptFieldJsonPath"
    )


class AppSpec(BaseModel):
    """Application specification within a MultiAgentSystem."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(description="Name of the application")
    type: AppType = Field(description="Type of the application")
    base_url: "AppSpecBaseUrl" = Field(description="Base URL of the application", alias="baseUrl")
    kubernetes_workload_name: str | None = Field(
        default=None, description="Name of the Kubernetes workload running the app", alias="kubernetesWorkloadName"
    )
    http_request_schema: HttpRequestSchema | None = Field(
        default=None, description="HTTP request schema for extracting the prompt field", alias="httpRequestSchema"
    )


class MultiAgentSystemSpec(BaseModel):
    """Specification for MultiAgentSystem CRD."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(description="Display name of the Multi-Agent System")
    enabled_tool_checks: list[ToolCheckType] = Field(
        default_factory=lambda: [
            ToolCheckType.DETERMINISTIC_TOOL_SELECTED,
            ToolCheckType.DETERMINISTIC_LLM_SELECTED_TOOLS,
            ToolCheckType.AI_POWERED_TOOL_MATCH,
        ],
        description="List of enabled tool check types",
        alias="enabledToolChecks",
    )
    apps: list[AppSpec] = Field(default_factory=list, description="List of applications in this MAS")
    llm_host: str | None = Field(default=None, description="LLM proxy host for outbound LLM call tracking")


class AppCredentials(BaseModel):
    """OAuth2 credentials for an application."""

    model_config = ConfigDict(populate_by_name=True)

    app_name: str = Field(description="Name of the application", alias="appName")
    app_id: str = Field(description="Application UUID", alias="appId")
    client_id: str = Field(description="OAuth2 client ID", alias="clientId")
    client_secret: str = Field(description="OAuth2 client secret", alias="clientSecret")
    secret_name: str = Field(description="Name of the K8s secret to create", alias="secretName")


class MultiAgentSystemStatus(BaseModel):
    """Status of MultiAgentSystem CRD."""

    model_config = ConfigDict(populate_by_name=True)

    phase: CRDPhase = Field(default=CRDPhase.PENDING, description="Current phase of the MAS")
    apps_ready: int = Field(default=0, description="Number of apps successfully registered", alias="appsReady")
    last_sync_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    message: str | None = Field(default=None, description="Human-readable status message")
    credentials: list[AppCredentials] | None = Field(
        default=None, description="OAuth2 credentials for each app (used by operator to create secrets)"
    )


class MultiAgentSystemMetadata(BaseModel):
    """Metadata for MultiAgentSystem CRD."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(description="Resource name")
    namespace: str = Field(description="Kubernetes namespace")
    uid: str | None = Field(default=None, description="Kubernetes UID")
    resource_version: str | None = Field(default=None, description="Resource version", alias="resourceVersion")
    generation: int | None = Field(default=None, description="Generation number")
    labels: dict | None = Field(default=None, description="Resource labels")
    annotations: dict | None = Field(default=None, description="Resource annotations")


class MultiAgentSystemCRD(BaseModel):
    """Complete MultiAgentSystem Custom Resource Definition."""

    model_config = ConfigDict(populate_by_name=True)

    api_version: str = Field(default="casa.io/v1alpha1", description="API version", alias="apiVersion")
    kind: Literal["MultiAgentSystem"] = Field(default="MultiAgentSystem", description="Resource kind")
    metadata: MultiAgentSystemMetadata
    spec: MultiAgentSystemSpec
    status: MultiAgentSystemStatus | None = Field(default=None, description="Resource status")


class MASCreateRequest(BaseModel):
    """Request model for creating a MultiAgentSystem via API."""

    metadata: MultiAgentSystemMetadata
    spec: MultiAgentSystemSpec


# CASAPolicy types


class CASAPolicyTargetRef(BaseModel):
    """Reference to the workload this policy applies to."""

    model_config = ConfigDict(populate_by_name=True)

    kind: str = Field(description="Workload kind: Deployment, StatefulSet, or Pod")
    name: str = Field(description="Name of the target workload")


class CASAPolicyAllowedEndpoint(BaseModel):
    """A Kubernetes service this workload is allowed to reach."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(description="Target service name")
    namespace: str = Field(description="Target service namespace")
    port: int = Field(description="Target port number")


class CASAPolicyLlmEndpoint(BaseModel):
    """External LLM endpoint this workload is allowed to reach."""

    model_config = ConfigDict(populate_by_name=True)

    fqdn: str = Field(description="FQDN of the allowed external LLM service")
    port: int = Field(description="Port for the LLM service")


class CASAPolicySpec(BaseModel):
    """Specification for CASAPolicy CRD."""

    model_config = ConfigDict(populate_by_name=True)

    target_ref: CASAPolicyTargetRef = Field(description="Workload this policy applies to", alias="targetRef")
    allowed_protocols: list[str] = Field(
        default_factory=list,
        description="Protocols allowed for this workload: mcp, a2a, http",
        alias="allowedProtocols",
    )
    allowed_endpoints: list[CASAPolicyAllowedEndpoint] = Field(
        default_factory=list,
        description="K8s services this workload may communicate with",
        alias="allowedEndpoints",
    )
    llm_endpoint: CASAPolicyLlmEndpoint | None = Field(
        default=None, description="Allowed external LLM endpoint", alias="llmEndpoint"
    )


class CASAPolicyStatus(BaseModel):
    """Status of CASAPolicy CRD."""

    model_config = ConfigDict(populate_by_name=True)

    phase: CRDPhase = Field(default=CRDPhase.PENDING, description="Current phase of the policy")
    last_sync_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    message: str | None = Field(default=None, description="Human-readable status message")


class CASAPolicyCRD(BaseModel):
    """Complete CASAPolicy Custom Resource Definition."""

    model_config = ConfigDict(populate_by_name=True)

    api_version: str = Field(default="casa.io/v1alpha1", description="API version", alias="apiVersion")
    kind: Literal["CASAPolicy"] = Field(default="CASAPolicy", description="Resource kind")
    metadata: MultiAgentSystemMetadata
    spec: CASAPolicySpec
    status: CASAPolicyStatus | None = Field(default=None, description="Resource status")


class CASAPolicyCreateRequest(BaseModel):
    """Request model for creating a CASAPolicy via API."""

    metadata: MultiAgentSystemMetadata
    spec: CASAPolicySpec
