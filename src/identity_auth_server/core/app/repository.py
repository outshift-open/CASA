"""Repository interface for App."""

from abc import ABC, abstractmethod

from identity_auth_server.core.app.types import App


class AppRepository(ABC):
    """Interface for AppRepository."""

    @abstractmethod
    def create(self, app: App) -> App:
        """Create a new app."""

    @abstractmethod
    def get_by_id(self, app_id: str) -> App | None:
        """Retrieve a app by app_id."""
