"""Repository interface for Session."""

from abc import ABC, abstractmethod


class AuthorizationServerRepository(ABC):
    """Interface for AuthorizationServerRepository."""

    @abstractmethod
    def create_token(self, TokenModel) -> str:
        """Create a new token and return its value."""
        pass
