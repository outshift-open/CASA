"""PostgreSQL implmentation of UserInputRepository."""

from abc import ABC, abstractmethod

from sqlmodel import Session

from identity_auth_server.core.types import UserInput


class UserInputRepository(ABC):
    """Interface defining the methods exposed by the UserInputRepository"""

    @abstractmethod
    def create(self, user_input: UserInput) -> UserInput:
        """Create a new UserInput in the database."""

    @abstractmethod
    def get_by_id(self, id: str) -> UserInput:
        """Get a UserInput by id."""


class UserInputPostgresRepository(UserInputRepository):
    """PostgreSQL implementation of the UserInputRepository"""

    def __init__(self, session: Session):
        """Initialize the repository with a then necessary dependencies."""
        self._session = session

    def create(self, user_input: UserInput) -> UserInput:
        """Create a new UserInput in the database."""
        self._session.add(user_input)
        return user_input

    def get_by_id(self, id: str) -> UserInput:
        """Get a UserInput by id."""
        try:
            user_input = self._session.get(UserInput, id)
            return user_input
        except Exception as e:
            raise Exception(f"Error retrieving user input with id '{id}': {e}") from e
