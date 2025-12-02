"""PostgreSQL implementation of AppRepository."""

from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from identity_auth_server.core.types import App


class AppRepository(ABC):
    """Interface for AppRepository."""

    @abstractmethod
    def create(self, app: App) -> App:
        """Create a new app."""

    @abstractmethod
    def get_by_id(self, app_id: str) -> App | None:
        """Retrieve a app by app_id."""


class AppPostgresRepository(AppRepository):
    """PostgreSQL implementation of AppRepository."""

    def __init__(self, session: Session):
        """Initialize the repository with a database session."""
        self.session = session

    def create(self, app: App) -> App:
        """Create a new app in the database."""
        try:
            self.session.add(app)
            self.session.flush()
            self.session.refresh(app)

            return app
        except IntegrityError as e:
            raise ValueError(f"App with app_id '{app.id}' already exists") from e
        except Exception as e:
            raise Exception(f"Error creating app: {e}") from e

    def get_by_id(self, app_id: str) -> App | None:
        """Retrieve an app by its ID."""
        try:
            app = self.session.get(App, app_id)
            return app
        except Exception as e:
            raise Exception(f"Error retrieving app with id '{app_id}': {e}") from e
