"""PostgreSQL implmentation of UserInputRepository."""

from abc import ABC, abstractmethod

from sqlmodel import Session, select

from identity_auth_server.core.types import UserInput


class UserInputRepository(ABC):
    """Interface defining the methods exposed by the UserInputRepository."""

    @abstractmethod
    def create(self, user_input: UserInput) -> UserInput:
        """Create a new UserInput in the database."""

    @abstractmethod
    def get_by_id(self, id: str) -> UserInput:
        """Get a UserInput by id."""

    @abstractmethod
    def get_by_tag(self, tag: str) -> UserInput:
        """Get a UserInput by tag."""


class UserInputPostgresRepository(UserInputRepository):
    """PostgreSQL implementation of the UserInputRepository."""

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

    def get_by_tag(self, tag: str) -> UserInput:
        """Get a UserInput by tag."""
        try:
            statement = select(UserInput).where(UserInput.tag == tag).order_by(UserInput.created_at.desc())
            user_input = self._session.exec(statement).first()
            return user_input
        except Exception as e:
            raise Exception(f"Error retrieving user input with tag '{tag}': {e}") from e
