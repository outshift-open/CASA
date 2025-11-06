"""Database interface."""

from abc import ABC, abstractmethod
from contextlib import contextmanager


class Database(ABC):
    """Interface for SourceAppCallRepository."""

    @abstractmethod
    def run_startup_migrations(self):
        """Run database migrations on startup."""
        pass

    @contextmanager
    @abstractmethod
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        pass
