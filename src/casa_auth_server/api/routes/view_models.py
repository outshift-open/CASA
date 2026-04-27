# Copyright 2026 Google LLC
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
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
    app_id: Optional[UUID]
    scopes: List[ScopeViewModelMinimal]

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class MultiAgentSystemViewModel(BaseModel):
    """View model for Multi-Agent System."""

    id: UUID
    name: str
    authorization_server_id: Optional[UUID]
    created_at: datetime

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class AppViewModel(BaseModel):
    """View model for App including tools and MAS relationships."""

    id: UUID
    type: str
    name: str
    base_url: str
    tools: List[ToolViewModel]
    mas_id: Optional[UUID]
    mas: Optional[MultiAgentSystemViewModel]

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class ScopeViewModel(BaseModel):
    """Full view model for Scope including relationships."""

    id: UUID
    name: str
    mas_id: Optional[UUID]
    mas: Optional[MultiAgentSystemViewModel]
    tools: List[ToolViewModel]

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)
