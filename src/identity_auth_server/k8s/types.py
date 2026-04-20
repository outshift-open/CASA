from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Enum as SAEnum, Field, Integer, Relationship, SQLModel

from identity_auth_server.core.types import AppType, ToolCheckFlags


class K8sAppSpec(SQLModel, table=True):
    """Application specification within a MultiAgentSystem."""

    __tablename__ = "K8sAppSpec"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(description="Name of the application")
    type: AppType = Field(description="Type of the application", sa_column=Column(
        SAEnum(
            AppType,
            name="app_type",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    ))
    url_host: str = Field(description="The host of the app base url", index=True)
    url_scheme: str = Field(description="The scheme of the app base url")
    prompt_field_json_path: Optional[str] = Field(description="The prompt field JSON path in the HTTP request schema")
    kubernetes_workload_name: Optional[str] = Field(description="Name of the Kubernetes workload running the app.")
    mas_crd_id: Optional[UUID] = Field(foreign_key="K8sMultiAgentSystemCRD.id")
    mas_crd: Optional["K8sMultiAgentSystemCRD"] = Relationship(back_populates="app_specs")
    app_id: Optional[UUID] = Field(foreign_key="app.id")


class K8sMultiAgentSystemMetadata(SQLModel, table=True):
    """Metadata for MultiAgentSystem CRD."""

    __tablename__ = "K8sMultiAgentSystemMetadata"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(description="Resource name")
    uid: Optional[str] = Field(default=None, description="Kubernetes UID")
    resource_version: Optional[str] = Field(default=None, description="Resource version", alias="resourceVersion")
    generation: Optional[int] = Field(default=None, description="Generation number")
    mas_crd_id: Optional[UUID] = Field(foreign_key="K8sMultiAgentSystemCRD.id")
    mas_crd: Optional["K8sMultiAgentSystemCRD"] = Relationship(back_populates="mas_metadata")


class K8sMultiAgentSystemCRD(SQLModel, table=True):
    """Complete MultiAgentSystem Custom Resource Definition."""

    __tablename__ = "K8sMultiAgentSystemCRD"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    api_version: str = Field(default="zta.io/v1alpha1", description="API version", alias="apiVersion")
    kind: str = Field(default="MultiAgentSystem", description="Resource kind")
    namespace: str = Field(description="Kubernetes namespace", index=True)
    mas_metadata: Optional[K8sMultiAgentSystemMetadata] = Relationship(back_populates="mas_crd")
    name: str = Field(description="Display name of the Multi-Agent System", unique=True)
    enabled_tool_checks: Optional[ToolCheckFlags] = Field(
        default=ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED
        | ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS
        | ToolCheckFlags.AI_POWERED_TOOL_MATCH,
        sa_column=Column(Integer, nullable=False),
    )
    llm_host: Optional[str] = Field(default=None)
    app_specs: List[K8sAppSpec] = Relationship(back_populates="mas_crd")
    mas_id: Optional[UUID] = Field(foreign_key="multiagentsystem.id")


class K8sTokenCache(SQLModel, table=True):
    __tablename__ = "K8sTokenCache"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    namespace: str = Field(description="Kubernetes namespace")
    trace_id: str = Field(index=True)
    app_host: str = Field()
    app_type: AppType = Field(description="Type of the app", sa_column=Column(
        SAEnum(
            AppType,
            name="app_type",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    ))
    access_token: str = Field()
    tool: Optional[str] = Field(default=None)
    created_at: datetime = datetime.now(timezone.utc)


class K8sLlmCallMapping(SQLModel, table=True):
    __tablename__ = "K8sLlmCallMapping"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    namespace: str
    trace_id: str
    mas_id: Optional[UUID] = Field(foreign_key="multiagentsystem.id")
    app_id: Optional[UUID] = Field(foreign_key="app.id")
    user_input_id: Optional[UUID] = Field(foreign_key="userinput.id")
    token: Optional[str] = Field(default=None)
    created_at: datetime = datetime.now(timezone.utc)
