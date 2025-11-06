"""PostgreSQL implementation of LlmAppCallRepository."""

import datetime
from uuid import uuid4

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.llm_app_call.postgres.models import LlmAppCallModel
from identity_auth_server.core.llm_app_call.repository import LlmAppCallRepository
from identity_auth_server.core.llm_app_call.types import LlmAppCall, LlmAppCallInput
from identity_auth_server.core.source_app_call.postgres.models import SourceAppCallModel
from identity_auth_server.database.postgres.postgres import PostgresDB


class LlmAppCallPostgresRepository(LlmAppCallRepository):
    """PostgreSQL implementation of LlmAppCallRepository."""

    def __init__(self, database: PostgresDB):
        """Initialize the repository with a database connection."""
        self.database = database

    def create(self, llm_app_call: LlmAppCallInput) -> LlmAppCall:
        """Create a new LLM app call in the database."""
        with self.database.session_scope() as session:
            source_app_call = (
                session.query(SourceAppCallModel)
                .filter(SourceAppCallModel.token == llm_app_call.source_app_call_token)
                .one_or_none()
            )

            if source_app_call is None:
                raise ResourceNotFoundError(
                    "Source app call not found for token: {token}".format(token=llm_app_call.source_app_call_token)
                )

            existing_llm_app_call = (
                session.query(LlmAppCallModel)
                .filter(LlmAppCallModel.proxy_call_id == llm_app_call.proxy_call_id)
                .one_or_none()
            )

            if existing_llm_app_call is not None:
                raise ValueError(
                    "LLM app call already exists for proxy call id: {proxy_call_id}".format(
                        proxy_call_id=llm_app_call.proxy_call_id
                    )
                )

            db_llm_app_call = LlmAppCallModel(
                id=uuid4(),
                source_app_call_id=source_app_call.id,
                token=llm_app_call.token,
                proxy_call_id=llm_app_call.proxy_call_id,
                messages=llm_app_call.messages,
                tools=llm_app_call.tools,
                created_at=datetime.datetime.now(datetime.timezone.utc),
            )

            session.add(db_llm_app_call)
            session.flush()
            session.refresh(db_llm_app_call)

            return LlmAppCall(
                id=db_llm_app_call.id,
                source_app_call_id=db_llm_app_call.source_app_call_id,
                token=db_llm_app_call.token,
                proxy_call_id=db_llm_app_call.proxy_call_id,
                messages=db_llm_app_call.messages,
                tools=db_llm_app_call.tools,
                created_at=db_llm_app_call.created_at,
            )
