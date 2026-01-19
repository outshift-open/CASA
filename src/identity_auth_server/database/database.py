"""Database interface."""

from abc import ABC, abstractmethod
from contextlib import contextmanager


class Database(ABC):
    """Interface for SourceAppCallRepository."""

    @contextmanager
    @abstractmethod
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        pass
