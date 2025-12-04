"""PostgreSQL implementation of AppRepository."""

from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from identity_auth_server.core.types import App, Tool
from identity_auth_server.database.database import Database


class AppRepository(ABC):
    """Interface for AppRepository."""

    @abstractmethod
    def create_app(self, app: App) -> App:
        """Create a new app."""

    @abstractmethod
    def update_app(self, app: App) -> App:
        """Update an existing app."""
        pass

    @abstractmethod
    def get_app_by_id(self, app_id: str) -> App | None:
        """Retrieve a app by app_id."""

    @abstractmethod
    def create_tool(self, tool: Tool) -> Tool:
        """Create a new tool."""


class AppPostgresRepository(AppRepository):
    """PostgreSQL implementation of AppRepository."""

    def __init__(self, database: Database, session: Session | None = None):
        """Initialize the repository with a database session."""
        self.database = database
        self._session = session

    def _update_or_create_app(self, app: App) -> App:
        """Update or create app in the database."""
        if self._session:
            self._session.add(app)
            self._session.flush()
            self._session.refresh(app)

            return app

        with self.database.session_scope() as session:
            session.add(app)
            session.flush()
            session.refresh(app)
            session.expunge(app)  # This will detach the object from the session

            return app

    def create_app(self, app: App) -> App:
        """Create a new app in the database."""
        try:
            return self._update_or_create_app(app)
        except IntegrityError as e:
            raise ValueError(f"App with app_id '{app.id}' already exists") from e
        except Exception as e:
            raise Exception(f"Error creating app: {e}") from e

    def update_app(self, app: App) -> App:
        """Update an existing app in the database."""
        try:
            return self._update_or_create_app(app)
        except Exception as e:
            raise Exception(f"Error updating app with id '{app.id}': {e}") from e

    def get_app_by_id(self, app_id: str) -> App | None:
        """Retrieve an app by its ID."""
        try:
            if self._session:
                app = self._session.get(App, app_id)

                return app

            with self.database.session_scope() as session:
                app = session.get(App, app_id)
                session.expunge(app)

                return app
        except Exception as e:
            raise Exception(f"Error retrieving app with id '{app_id}': {e}") from e

    def create_tool(self, tool: Tool) -> Tool:
        """Create a new tool in the database."""
        try:
            if self._session:
                self._session.add(tool)
                self._session.flush()
                self._session.refresh(tool)

                return tool

            with self.database.session_scope() as session:
                session.add(tool)
                session.flush()
                session.refresh(tool)
                session.expunge(tool)

                return tool
        except IntegrityError as e:
            raise ValueError(f"Tool with tool_id '{tool.id}' already exists") from e
        except Exception as e:
            raise Exception(f"Error creating tool: {e}") from e
