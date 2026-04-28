# Copyright 2025 Cisco Systems, Inc. and its affiliates
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

"""Repository layer for Multi-Agent System persistence."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlmodel import Session, select

from casa_auth_server.core.types import MultiAgentSystem


class MultiAgentSystemRepository(ABC):
    """Interface defining the methods exposed for the MAS repository."""

    @abstractmethod
    def create(self, mas: MultiAgentSystem) -> MultiAgentSystem:
        """Store a new multi agent system instance in the database."""

    @abstractmethod
    def update(self, mas: MultiAgentSystem) -> MultiAgentSystem:
        """Update an existing multi agent system instance in the database."""

    @abstractmethod
    def delete(self, mas: MultiAgentSystem):
        """Delete an existing multi agent system instance from the database."""

    @abstractmethod
    def get_by_id(self, id: str) -> MultiAgentSystem:
        """Fetch a multi agent system by ID from the database."""

    @abstractmethod
    def get_all(self) -> list[MultiAgentSystem]:
        """Fetch all the mutli agent systems stored in the database."""

    @abstractmethod
    def get_by_name_and_namespace(self, name: str, namespace: str) -> MultiAgentSystem:
        """Fetch a multi agent system by name and namespace from the database."""


class MultiAgentSystemPostgresRepository(MultiAgentSystemRepository):
    """PostgreSQL implementation of the MultiAgentSystemRepository interface."""

    def __init__(self, session: Session):
        """Initialize a new MultiAgentSystemPostgresRepository instance."""
        self._session = session

    def create(self, mas: MultiAgentSystem) -> MultiAgentSystem:
        """Store a new multi agent system instance in the database."""
        self._session.add(mas)

        return mas

    def update(self, mas: MultiAgentSystem) -> MultiAgentSystem:
        """Update an existing multi agent system instance in the database."""
        self._session.add(mas)

        return mas

    def delete(self, mas: MultiAgentSystem):
        """Soft-delete a multi agent system by setting deleted_at."""
        mas.deleted_at = datetime.now(UTC)
        self._session.add(mas)

    def get_by_id(self, id: str) -> MultiAgentSystem:
        """Fetch a multi agent system by ID from the database."""
        try:
            mas = self._session.exec(
                select(MultiAgentSystem).where(MultiAgentSystem.id == id).where(MultiAgentSystem.deleted_at == None)
            ).first()
            return mas
        except Exception as e:
            raise Exception(f"Error retrieving MAS with id '{id}': {e}") from e

    def get_all(self) -> list[MultiAgentSystem]:
        """Fetch all the mutli agent systems stored in the database."""
        try:
            mas_list = self._session.exec(select(MultiAgentSystem).where(MultiAgentSystem.deleted_at == None)).all()
            return list(mas_list)
        except Exception as e:
            raise Exception(f"Error retrieving MAS list: {e}") from e

    def get_by_name_and_namespace(self, name: str, namespace: str) -> MultiAgentSystem:
        """Fetch a multi agent system by k8s_name and namespace from the database."""
        try:
            # Search by k8s_name first (for CRD-created MAS), fallback to name
            statement = (
                select(MultiAgentSystem)
                .where(MultiAgentSystem.namespace == namespace)
                .where((MultiAgentSystem.k8s_name == name) | (MultiAgentSystem.name == name))
                .where(MultiAgentSystem.deleted_at == None)
            )
            mas = self._session.exec(statement).first()
            if not mas:
                raise ValueError(f"MultiAgentSystem with name '{name}' in namespace '{namespace}' not found")
            return mas
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Error retrieving MAS by name and namespace: {e}") from e
