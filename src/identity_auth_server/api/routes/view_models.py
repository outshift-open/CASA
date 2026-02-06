from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from identity_auth_server.core.types import Tool

# The reason for creating view models for the App is
# because we want to include the MAS when serializing
# the App to JSON. By default SQLAlchemy doesn't include
# relationships in the serialized model.


class MultiAgentSystemViewModel(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)


class AppViewModel(BaseModel):
    id: UUID
    type: str
    name: str
    base_url: str
    authorization_server_id: Optional[UUID]
    client_credentials_id: Optional[UUID]
    tools: List[Tool]
    mas_id: Optional[UUID]
    mas: Optional[MultiAgentSystemViewModel]

    # To be able to create an instance from a SQLModel
    model_config = ConfigDict(from_attributes=True)
