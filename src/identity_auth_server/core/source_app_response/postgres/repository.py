"""PostgreSQL implementation of SourceAppResponseRepository."""

import datetime
from uuid import uuid4

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.source_app_call.postgres.models import SourceAppCallModel
from identity_auth_server.core.source_app_response.postgres.models import SourceAppResponseModel
from identity_auth_server.core.source_app_response.repository import SourceAppResponseRepository
from identity_auth_server.core.source_app_response.types import SourceAppResponse, SourceAppResponseInput
from identity_auth_server.database.postgres.postgres import PostgresDB


class SourceAppResponsePostgresRepository(SourceAppResponseRepository):
    """PostgreSQL-backed repository for source app responses."""

    def __init__(self, database: PostgresDB):
        """Initialize the repository with a database connection."""
        self.database = database

    def create(self, source_app_response: SourceAppResponseInput) -> SourceAppResponse:
        """Persist a new source app response linked to a source app call."""
        with self.database.session_scope() as session:
            source_app_call = (
                session.query(SourceAppCallModel)
                .filter(SourceAppCallModel.token == source_app_response.source_app_call_token)
                .one_or_none()
            )

            if source_app_call is None:
                raise ResourceNotFoundError(
                    "Source app call not found for token: {token}".format(
                        token=source_app_response.source_app_call_token
                    )
                )

            db_source_app_response = SourceAppResponseModel(
                id=uuid4(),
                source_app_call_id=source_app_call.id,
                token=source_app_response.token,
                output=source_app_response.output,
                created_at=datetime.datetime.now(datetime.timezone.utc),
            )

            session.add(db_source_app_response)
            session.flush()
            session.refresh(db_source_app_response)

            return SourceAppResponse(
                id=db_source_app_response.id,
                source_app_call_id=db_source_app_response.source_app_call_id,
                token=db_source_app_response.token,
                output=db_source_app_response.output,
                created_at=db_source_app_response.created_at,
            )
