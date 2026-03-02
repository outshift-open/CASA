"""Database models for storing Kubernetes CRD metadata and state."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, String
from sqlmodel import Field, Relationship, SQLModel


class K8sMultiAgentSystemCRD(SQLModel, table=True):
    """Database model for MultiAgentSystem CRD metadata.
    
    Stores Kubernetes-specific metadata for MAS resources to enable
    proper namespace isolation, labeling, and status tracking.
    """

    __tablename__ = "k8s_multiagentsystem_crd"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    
    # Kubernetes metadata
    name: str = Field(index=True)
    namespace: str = Field(index=True, default="default")
    uid: str = Field(unique=True, index=True)  # Kubernetes UID
    resource_version: str = Field(default="1")
    labels: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    annotations: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    
    # Link to internal MAS
    mas_id: Optional[UUID] = Field(foreign_key="multiagentsystem.id", unique=True)
    
    # CRD status
    phase: str = Field(default="Pending")  # Pending, Active, Failed
    apps_ready: int = Field(default=0)
    message: Optional[str] = None
    last_sync_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class K8sZTAPolicyCRD(SQLModel, table=True):
    """Database model for ZTAPolicy CRD metadata.
    
    Stores Kubernetes-specific metadata for ZTAPolicy resources to enable
    proper namespace isolation, target references, and Cilium policy generation tracking.
    """

    __tablename__ = "k8s_ztapolicy_crd"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    
    # Kubernetes metadata
    name: str = Field(index=True)
    namespace: str = Field(index=True, default="default")
    uid: str = Field(unique=True, index=True)
    resource_version: str = Field(default="1")
    labels: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    annotations: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    
    # Policy spec (stored as JSON for flexibility)
    target_kind: str  # Deployment, StatefulSet, Pod
    target_name: str
    spec_json: dict = Field(sa_column=Column(JSON))  # Full policy spec
    
    # CRD status
    phase: str = Field(default="Pending")  # Pending, Active, Failed
    cilium_policy_name: Optional[str] = None  # Name of generated CiliumNetworkPolicy
    message: Optional[str] = None
    last_sync_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class K8sCRDMetadataModel(SQLModel):
    """Base model for K8s CRD metadata (for Pydantic validation)."""
    
    name: str
    namespace: str
    uid: str
    resource_version: str
    labels: dict = {}
    annotations: dict = {}
