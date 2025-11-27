"""PostgreSQL implementation of SessionRepository."""

from uuid import uuid4

from identity_auth_server.core.token.postgres.models import TokenModel
from identity_auth_server.database.postgres.postgres import PostgresDB


class AuthorizationServerPostgresRepository(AuthorizationServerRepository):
    """PostgreSQL-backed token repository implementation."""

    def __init__(self, database: PostgresDB):
        """Initialize the repository with a database session."""
        self.database = database

    def create_token(self, token: TokenModel) -> str:
        """Persist a source app session and return the generated token."""
        db_session = TokenModel(
            id=uuid4(), value=token.value, expires_at=token.expires_at, client_credential_id=token.client_credential_id
        )

        with self.database.session_scope() as session:
            session.add(db_session)
            session.flush()
            session.refresh(db_session)

            return db_session.token
