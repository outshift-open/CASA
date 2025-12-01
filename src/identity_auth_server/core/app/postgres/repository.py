"""PostgreSQL implementation of AppRepository."""

from sqlalchemy.exc import IntegrityError

from identity_auth_server.core.app.repository import AppRepository
from identity_auth_server.core.app.types import App
from identity_auth_server.database.postgres.postgres import PostgresDB


class AppPostgresRepository(AppRepository):
    """PostgreSQL implementation of AppRepository."""

    def __init__(self, database: PostgresDB):
        """Initialize the repository with a database session."""
        self.database = database

    def create(self, app: App) -> App:
        """Create a new app in the database."""
        try:
            with self.database.session_scope() as session:
                session.add(app)
                session.flush()
                session.refresh(app)

                return app
        except IntegrityError as e:
            raise ValueError(f"App with app_id '{app.id}' already exists") from e
        except Exception as e:
            raise Exception(f"Error creating app: {e}") from e

    def get_by_id(self, app_id: str) -> App | None:
        """Retrieve an app by its ID."""
        try:
            with self.database.session_scope() as session:
                app = session.get(App, app_id)
                return app
        except Exception as e:
            raise Exception(f"Error retrieving app with id '{app_id}': {e}") from e
