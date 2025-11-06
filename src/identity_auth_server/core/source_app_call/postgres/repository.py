"""PostgreSQL implementation of SourceAppCallRepository."""

import datetime
from uuid import uuid4

from identity_auth_server.core.source_app_call.postgres.models import SourceAppCallModel
from identity_auth_server.core.source_app_call.repository import SourceAppCallRepository
from identity_auth_server.core.source_app_call.types import SourceAppCall, SourceAppCallInput
from identity_auth_server.database.postgres.postgres import PostgresDB


class SourceAppCallPostgresRepository(SourceAppCallRepository):
    """PostgreSQL implementation of SourceAppCallRepository."""

    def __init__(self, database: PostgresDB):
        """Initialize the repository with a database session."""
        self.database = database

    def create(self, source_app_call: SourceAppCallInput) -> SourceAppCall:
        """Create a new source app call in the database."""
        db_source_app_call = SourceAppCallModel(
            id=uuid4(),
            token=source_app_call.token,
            input=source_app_call.input,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )

        try:
            with self.database.session_scope() as session:
                session.add(db_source_app_call)
                session.flush()
                session.refresh(db_source_app_call)

                return SourceAppCall(
                    id=db_source_app_call.id,
                    token=db_source_app_call.token,
                    input=db_source_app_call.input,
                    created_at=db_source_app_call.created_at,
                )
        except Exception as e:
            print("Error creating source app call:", e)
            raise e

    def get_by_source_app_call_token(self, token: str) -> list[SourceAppCall]:
        """Retrieve all source app calls by source_app_call_token."""
        with self.database.session_scope() as session:
            db_source_app_calls = session.query(SourceAppCallModel).filter(SourceAppCallModel.token == token).all()

            return [
                SourceAppCall(
                    id=db_source_app_call.id,
                    token=db_source_app_call.token,
                    input=db_source_app_call.input,
                    created_at=db_source_app_call.created_at,
                )
                for db_source_app_call in db_source_app_calls
            ]
