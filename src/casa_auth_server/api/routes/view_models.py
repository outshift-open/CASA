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

"""View models for API responses.

The reason for creating view models is because we want to include
relationships when serializing to JSON. By default SQLAlchemy doesn't
include relationships in the serialized model.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from casa_auth_server.telemetry.tracer_repository import MASTraceStat


class ScopeViewModelMinimal(BaseModel):
    """Minimal view model for Scope with only essential fields (used in Tool.scopes)."""

    id: UUID
    name: str

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class ToolViewModel(BaseModel):
    """View model for Tool including its scopes."""

    id: UUID
    name: str
    description: str
    input_schema: str
    output_schema: str
    app_id: UUID | None
    scopes: list[ScopeViewModelMinimal]

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class MultiAgentSystemViewModel(BaseModel):
    """View model for Multi-Agent System."""

    id: UUID
    name: str
    authorization_server_id: UUID | None
    created_at: datetime

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class AppViewModel(BaseModel):
    """View model for App including tools and MAS relationships."""

    id: UUID
    type: str
    name: str
    base_url: str
    tools: list[ToolViewModel]
    mas_id: UUID | None
    mas: MultiAgentSystemViewModel | None

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class AppSummaryViewModel(BaseModel):
    """Minimal app view model for embedding inside a MAS list entry."""

    id: UUID
    type: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class MASListItemViewModel(BaseModel):
    """View model for a MAS entry in the list response, including inline app summaries and trace counts."""

    id: UUID
    name: str
    namespace: str | None
    k8s_name: str | None
    enabled_tool_checks: int | None
    authorization_server_id: UUID | None
    created_at: datetime
    apps: list[AppSummaryViewModel]
    traces: MASTraceStat | None = None

    model_config = ConfigDict(from_attributes=True)


class MASDetailViewModel(BaseModel):
    """View model for a single MAS detail response, including inline app summaries and optional trace counts."""

    id: UUID
    name: str
    namespace: str | None
    k8s_name: str | None
    enabled_tool_checks: int | None
    authorization_server_id: UUID | None
    created_at: datetime
    apps: list[AppSummaryViewModel]
    traces: MASTraceStat | None = None

    model_config = ConfigDict(from_attributes=True)


class MASListResponse(BaseModel):
    """Paginated list of Multi-Agent Systems."""

    items: list[MASListItemViewModel]
    total: int
    page: int
    page_size: int


class ScopeViewModel(BaseModel):
    """Full view model for Scope including relationships."""

    id: UUID
    name: str
    mas_id: UUID | None
    mas: MultiAgentSystemViewModel | None
    tools: list[ToolViewModel]

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)
