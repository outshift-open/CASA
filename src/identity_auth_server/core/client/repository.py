"""Repository interface for Client."""

from abc import ABC, abstractmethod

from identity_auth_server.core.client.types import Client, ClientInput


class ClientRepository(ABC):
    """Interface for ClientRepository."""

    @abstractmethod
    def create(self, client: ClientInput) -> Client:
        """Create a new client."""
        pass

    @abstractmethod
    def get_by_client_id(self, client_id: str) -> Client | None:
        """Retrieve a client by client_id."""
        pass

    @abstractmethod
    def update(self, client: Client) -> Client:
        """Update an existing client."""
        pass
