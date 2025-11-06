"""PostgreSQL implementation of LlmAppResponseRepository."""

import datetime
from uuid import uuid4

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.llm_app_call.postgres.models import LlmAppCallModel
from identity_auth_server.core.llm_app_response.postgres.models import LlmAppResponseModel
from identity_auth_server.core.llm_app_response.repository import LlmAppResponseRepository
from identity_auth_server.core.llm_app_response.types import LlmAppResponse, LlmAppResponseInput
from identity_auth_server.core.source_app_call.postgres.models import SourceAppCallModel
from identity_auth_server.database.postgres.postgres import PostgresDB


class LlmAppResponsePostgresRepository(LlmAppResponseRepository):
    """PostgreSQL-backed repository for LLM app responses."""

    def __init__(self, database: PostgresDB):
        """Initialize the repository with a database connection."""
        self.database = database

    def create(self, llm_app_response: LlmAppResponseInput) -> LlmAppResponse:
        """Create a new LLM app response."""
        with self.database.session_scope() as session:
            source_app_call = (
                session.query(SourceAppCallModel)
                .filter(SourceAppCallModel.token == llm_app_response.source_app_call_token)
                .one_or_none()
            )

            if source_app_call is None:
                raise ResourceNotFoundError(
                    "Source app call not found for token: {token}".format(token=llm_app_response.source_app_call_token)
                )

            llm_app_call = (
                session.query(LlmAppCallModel)
                .filter(LlmAppCallModel.proxy_call_id == llm_app_response.proxy_call_id)
                .one_or_none()
            )

            if llm_app_call is None:
                raise ResourceNotFoundError(
                    "LLM app call not found for proxy call id: {proxy_call_id}".format(
                        proxy_call_id=llm_app_response.proxy_call_id
                    )
                )

            if llm_app_call.source_app_call_id != source_app_call.id:
                raise ValueError(
                    "Proxy call id does not belong to the provided source token: {token}".format(
                        token=llm_app_response.source_app_call_token
                    )
                )

            db_llm_app_response = LlmAppResponseModel(
                id=uuid4(),
                llm_app_call_id=llm_app_call.id,
                token=llm_app_response.token,
                proxy_call_id=llm_app_response.proxy_call_id,
                message=llm_app_response.message,
                tool_calls=llm_app_response.tool_calls,
                created_at=datetime.datetime.now(datetime.timezone.utc),
            )

            session.add(db_llm_app_response)
            session.flush()
            session.refresh(db_llm_app_response)

            return LlmAppResponse(
                id=db_llm_app_response.id,
                llm_app_call_id=db_llm_app_response.llm_app_call_id,
                token=db_llm_app_response.token,
                proxy_call_id=db_llm_app_response.proxy_call_id,
                message=db_llm_app_response.message,
                tool_calls=db_llm_app_response.tool_calls,
                created_at=db_llm_app_response.created_at,
            )

    def get_by_llm_app_response_by_token(self, token: str) -> list[LlmAppResponse]:
        """Retrieve all LLM app responses by token."""
        with self.database.session_scope() as session:
            db_llm_app_responses = (
                session.query(LlmAppResponseModel)
                .filter(LlmAppResponseModel.token == token)
                .order_by(LlmAppResponseModel.created_at.desc())
                .all()
            )

            return [
                LlmAppResponse(
                    id=db_response.id,
                    llm_app_call_id=db_response.llm_app_call_id,
                    token=db_response.token,
                    proxy_call_id=db_response.proxy_call_id,
                    message=db_response.message,
                    tool_calls=db_response.tool_calls,
                    created_at=db_response.created_at,
                )
                for db_response in db_llm_app_responses
            ]
