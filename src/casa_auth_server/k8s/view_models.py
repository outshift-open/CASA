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

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from casa_auth_server.core.types import AppType, ToolCheckFlags


class K8sAppSpecViewModel(BaseModel):
    """View model for application specification data."""

    id: Optional[UUID] = None
    name: str
    type: AppType
    url_host: str
    url_scheme: str
    prompt_field_json_path: Optional[str] = None
    kubernetes_workload_name: Optional[str] = None
    mas_crd_id: Optional[UUID] = None
    app_id: Optional[UUID] = None

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class K8sMultiAgentSystemMetadataViewModel(BaseModel):
    """View model for MultiAgentSystem metadata."""

    id: Optional[UUID] = None
    name: str
    uid: Optional[str] = None
    resource_version: Optional[str] = None
    generation: Optional[int] = None
    mas_crd_id: Optional[UUID] = None

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class K8sMultiAgentSystemCRDViewModel(BaseModel):
    """View model for a complete MultiAgentSystem CRD."""

    id: Optional[UUID] = None
    api_version: str
    kind: str
    namespace: str
    mas_metadata: Optional[K8sMultiAgentSystemMetadataViewModel] = None
    name: str
    enabled_tool_checks: Optional[List[str]]
    llm_host: Optional[str]
    app_specs: List[K8sAppSpecViewModel] = []
    mas_id: Optional[UUID] = None

    @field_validator("enabled_tool_checks", mode="before")
    @classmethod
    def convert_enabled_tool_checks(cls, v):
        checks = []
        if (v & ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED) == ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED:
            checks.append(ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED.name)
        if (v & ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS) == ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS:
            checks.append(ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS.name)
        if (v & ToolCheckFlags.AI_POWERED_TOOL_MATCH) == ToolCheckFlags.AI_POWERED_TOOL_MATCH:
            checks.append(ToolCheckFlags.AI_POWERED_TOOL_MATCH.name)
        return checks

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)
