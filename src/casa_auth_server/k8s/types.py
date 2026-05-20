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

# mypy: disable-error-code="call-arg"

from datetime import UTC, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, Integer, Relationship, SQLModel
from sqlmodel import Enum as SAEnum

from casa_auth_server.core.types import AppType, ToolCheckFlags


class K8sAppSpec(SQLModel, table=True):
    """Application specification within a MultiAgentSystem."""

    __tablename__ = "K8sAppSpec"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(description="Name of the application")
    type: AppType = Field(
        description="Type of the application",
        sa_column=Column(
            SAEnum(
                AppType,
                name="app_type",
                values_callable=lambda enum_cls: [e.value for e in enum_cls],
            ),
            nullable=False,
        ),
    )
    url_host: str = Field(description="The host of the app base url", index=True)
    url_scheme: str = Field(description="The scheme of the app base url")
    prompt_field_json_path: str | None = Field(description="The prompt field JSON path in the HTTP request schema")
    kubernetes_workload_name: str | None = Field(description="Name of the Kubernetes workload running the app.")
    mas_crd_id: UUID | None = Field(foreign_key="K8sMultiAgentSystemCRD.id")
    mas_crd: Optional["K8sMultiAgentSystemCRD"] = Relationship(back_populates="app_specs")
    app_id: UUID | None = Field(foreign_key="app.id")


class K8sMultiAgentSystemMetadata(SQLModel, table=True):
    """Metadata for MultiAgentSystem CRD."""

    __tablename__ = "K8sMultiAgentSystemMetadata"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(description="Resource name")
    uid: str | None = Field(default=None, description="Kubernetes UID")
    resource_version: str | None = Field(default=None, description="Resource version", alias="resourceVersion")
    generation: int | None = Field(default=None, description="Generation number")
    mas_crd_id: UUID | None = Field(foreign_key="K8sMultiAgentSystemCRD.id")
    mas_crd: Optional["K8sMultiAgentSystemCRD"] = Relationship(back_populates="mas_metadata")


class K8sMultiAgentSystemCRD(SQLModel, table=True):
    """Complete MultiAgentSystem Custom Resource Definition."""

    __tablename__ = "K8sMultiAgentSystemCRD"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    api_version: str = Field(default="casa.io/v1alpha1", description="API version", alias="apiVersion")
    kind: str = Field(default="MultiAgentSystem", description="Resource kind")
    namespace: str = Field(description="Kubernetes namespace", index=True)
    mas_metadata: K8sMultiAgentSystemMetadata | None = Relationship(back_populates="mas_crd")
    name: str = Field(description="Display name of the Multi-Agent System", unique=True)
    enabled_tool_checks: ToolCheckFlags | None = Field(
        default=ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED
        | ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS
        | ToolCheckFlags.AI_POWERED_TOOL_MATCH,
        sa_column=Column(Integer, nullable=False),
    )
    llm_host: str | None = Field(default=None)
    app_specs: list[K8sAppSpec] = Relationship(back_populates="mas_crd")
    mas_id: UUID | None = Field(foreign_key="multiagentsystem.id")


class K8sTokenCache(SQLModel, table=True):
    __tablename__ = "K8sTokenCache"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    namespace: str = Field(description="Kubernetes namespace")
    trace_id: str = Field(index=True)
    app_host: str = Field()
    app_type: AppType = Field(
        description="Type of the app",
        sa_column=Column(
            SAEnum(
                AppType,
                name="app_type",
                values_callable=lambda enum_cls: [e.value for e in enum_cls],
            ),
            nullable=False,
        ),
    )
    access_token: str = Field()
    tool: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class K8sLlmCallMapping(SQLModel, table=True):
    __tablename__ = "K8sLlmCallMapping"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    namespace: str
    trace_id: str
    mas_id: UUID | None = Field(foreign_key="multiagentsystem.id")
    app_id: UUID | None = Field(foreign_key="app.id")
    user_input_id: UUID | None = Field(foreign_key="userinput.id")
    token: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class K8sCASAPolicyAllowedEndpoint(SQLModel, table=True):
    """Allowed egress endpoint for a CASAPolicy."""

    __tablename__ = "K8sCASAPolicyAllowedEndpoint"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(description="Target service name")
    namespace: str = Field(description="Target service namespace")
    port: int = Field(description="Target port number")
    policy_id: UUID | None = Field(foreign_key="K8sCASAPolicy.id")
    policy: Optional["K8sCASAPolicy"] = Relationship(back_populates="allowed_endpoints")


class K8sCASAPolicy(SQLModel, table=True):
    """CASAPolicy Custom Resource Definition stored in the database."""

    __tablename__ = "K8sCASAPolicy"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    namespace: str = Field(description="Kubernetes namespace", index=True)
    name: str = Field(description="CR metadata.name", index=True)
    target_ref_kind: str = Field(description="Workload kind: Deployment, StatefulSet, or Pod")
    target_ref_name: str = Field(description="Name of the target workload", index=True)
    allowed_protocols: str = Field(default="[]", description="JSON-encoded list of allowed protocols")
    llm_endpoint_fqdn: str | None = Field(default=None, description="FQDN of the allowed external LLM service")
    llm_endpoint_port: int | None = Field(default=None, description="Port for the LLM service")
    allowed_endpoints: list[K8sCASAPolicyAllowedEndpoint] = Relationship(back_populates="policy")
