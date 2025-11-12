"""Repository interface for Session."""

from abc import ABC, abstractmethod

# from identity_auth_server.core.token.types import


class TokenRepository(ABC):
    """Interface for TokenRepository."""

    @abstractmethod
    def create_token(self, string) -> str:
        """Create a new token and return its value."""
        pass
