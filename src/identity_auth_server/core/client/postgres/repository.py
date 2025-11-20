"""PostgreSQL implementation of ClientRepository."""

import datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from identity_auth_server.core.client.postgres.models import ClientModel
from identity_auth_server.core.client.repository import ClientRepository
from identity_auth_server.core.client.types import Client, ClientInput
from identity_auth_server.database.postgres.postgres import PostgresDB


class ClientPostgresRepository(ClientRepository):
    """PostgreSQL implementation of ClientRepository."""

    def __init__(self, database: PostgresDB):
        """Initialize the repository with a database session."""
        self.database = database

    def create(self, client: ClientInput) -> Client:
        """Create a new client in the database."""
        now = datetime.datetime.now(datetime.timezone.utc)
        db_client = ClientModel(
            id=uuid4(),
            client_id=client.client_id,
            name=client.name,
            secret=client.secret,
            created_at=now,
            updated_at=now,
        )

        try:
            with self.database.session_scope() as session:
                session.add(db_client)
                session.flush()
                session.refresh(db_client)

                return Client(
                    id=db_client.id,
                    client_id=db_client.client_id,
                    name=db_client.name,
                    secret=db_client.secret,
                    created_at=db_client.created_at,
                    updated_at=db_client.updated_at,
                )
        except IntegrityError as e:
            raise ValueError(f"Client with client_id '{client.client_id}' already exists") from e
        except Exception as e:
            raise Exception(f"Error creating client: {e}") from e

    def get_by_client_id(self, client_id: str) -> Client | None:
        """Retrieve a client by client_id."""
        with self.database.session_scope() as session:
            db_client = session.query(ClientModel).filter(ClientModel.client_id == client_id).first()

            if db_client is None:
                return None

            return Client(
                id=db_client.id,
                client_id=db_client.client_id,
                name=db_client.name,
                secret=db_client.secret,
                created_at=db_client.created_at,
                updated_at=db_client.updated_at,
            )

    def update(self, client: Client) -> Client:
        """Update an existing client in the database."""
        with self.database.session_scope() as session:
            db_client = session.query(ClientModel).filter(ClientModel.id == client.id).first()

            if db_client is None:
                raise ValueError(f"Client with id '{client.id}' not found")

            # Update fields
            db_client.client_id = client.client_id
            db_client.name = client.name
            db_client.secret = client.secret
            db_client.updated_at = datetime.datetime.now(datetime.timezone.utc)

            session.flush()
            session.refresh(db_client)

            return Client(
                id=db_client.id,
                client_id=db_client.client_id,
                name=db_client.name,
                secret=db_client.secret,
                created_at=db_client.created_at,
                updated_at=db_client.updated_at,
            )
