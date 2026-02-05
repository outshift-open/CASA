from abc import ABC, abstractmethod
from typing import List

from sqlmodel import Session, select

from identity_auth_server.core.types import MultiAgentSystem


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
    def get_all(self) -> List[MultiAgentSystem]:
        """Fetch all the mutli agent systems stored in the database."""


class MultiAgentSystemPostgresRepository(MultiAgentSystemRepository):
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
        """Delete an existing multi agent system instance from the database."""
        self._session.delete(mas)

    def get_by_id(self, id: str) -> MultiAgentSystem:
        """Fetch a multi agent system by ID from the database."""
        try:
            mas = self._session.get(MultiAgentSystem, id)
            return mas
        except Exception as e:
            raise Exception(f"Error retrieving MAS with id '{id}': {e}") from e

    def get_all(self) -> List[MultiAgentSystem]:
        """Fetch all the mutli agent systems stored in the database."""
        try:
            masList = self._session.exec(select(MultiAgentSystem)).all()
            return list(masList)
        except Exception as e:
            raise Exception(f"Error retrieving MAS list: {e}") from e
