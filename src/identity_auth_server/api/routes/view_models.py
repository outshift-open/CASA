from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# The reason for creating view models for the App is
# because we want to include the MAS when serializing
# the App to JSON. By default SQLAlchemy doesn't include
# relationships in the serialized model.


class ScopeViewModel(BaseModel):
    """View model for Scope with only essential fields."""

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
    scopes: List[ScopeViewModel]

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class MultiAgentSystemViewModel(BaseModel):
    id: UUID
    name: str
    authorization_server_id: Optional[UUID]
    created_at: datetime

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class AppViewModel(BaseModel):
    id: UUID
    type: str
    name: str
    base_url: str
    tools: List[ToolViewModel]
    mas_id: Optional[UUID]
    mas: Optional[MultiAgentSystemViewModel]

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)
