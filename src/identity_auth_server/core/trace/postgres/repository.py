"""PostgreSQL implementation of TraceRepository."""

from typing import Dict, List
from uuid import UUID

from sqlalchemy import func

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.llm_app_call.postgres.models import LlmAppCallModel
from identity_auth_server.core.llm_app_call.types import LlmAppCall
from identity_auth_server.core.llm_app_response.postgres.models import LlmAppResponseModel
from identity_auth_server.core.llm_app_response.types import LlmAppResponse
from identity_auth_server.core.mcp_app_tool_call.postgres.models import BlockedByTypeModel, McpAppToolCallModel
from identity_auth_server.core.mcp_app_tool_call.types import McpAppToolCall
from identity_auth_server.core.source_app_call.postgres.models import SourceAppCallModel
from identity_auth_server.core.source_app_call.types import SourceAppCall
from identity_auth_server.core.source_app_response.postgres.models import SourceAppResponseModel
from identity_auth_server.core.source_app_response.types import SourceAppResponse
from identity_auth_server.core.trace.repository import TraceRepository
from identity_auth_server.core.trace.types import Trace, TraceList, TraceLlmAppCall, TraceMcpAppToolCall
from identity_auth_server.database.postgres.postgres import PostgresDB


class TracePostgresRepository(TraceRepository):
    """PostgreSQL-backed trace repository."""

    def __init__(self, database: PostgresDB):
        """Initialize the repository with a database connection."""
        self.database = database

    def get(self, source_app_call_id: UUID) -> Trace:
        """Retrieve a single trace by the source app call id."""
        with self.database.session_scope() as session:
            source_model = (
                session.query(SourceAppCallModel).filter(SourceAppCallModel.id == source_app_call_id).one_or_none()
            )

            if source_model is None:
                raise ResourceNotFoundError("Source app call not found for id: {id}".format(id=source_app_call_id))

            return self._build_trace(session, source_model)

    def get_all(self, page: int, page_size: int) -> TraceList:
        """Retrieve all traces in a paginated fashion."""
        if page < 1:
            raise ValueError("page must be greater than 0")
        if page_size < 1:
            raise ValueError("page_size must be greater than 0")

        with self.database.session_scope() as session:
            total = session.query(func.count(SourceAppCallModel.id)).scalar() or 0

            if total == 0:
                return TraceList(items=[], total=0, page=page, page_size=page_size)

            source_models = (
                session.query(SourceAppCallModel)
                .order_by(SourceAppCallModel.created_at.desc())
                .limit(page_size)
                .offset((page - 1) * page_size)
                .all()
            )

            traces = [self._build_trace(session, model) for model in source_models]

            return TraceList(items=traces, total=total, page=page, page_size=page_size)

    def _build_trace(self, session, source_model: SourceAppCallModel) -> Trace:
        source = self._to_source_app_call(source_model)

        source_app_response_model = (
            session.query(SourceAppResponseModel)
            .filter(SourceAppResponseModel.source_app_call_id == source_model.id)
            .order_by(SourceAppResponseModel.created_at.desc())
            .first()
        )

        source_app_response = (
            self._to_source_app_response(source_app_response_model) if source_app_response_model else None
        )

        llm_call_models: List[LlmAppCallModel] = (
            session.query(LlmAppCallModel)
            .filter(LlmAppCallModel.source_app_call_id == source_model.id)
            .order_by(LlmAppCallModel.created_at.asc())
            .all()
        )

        llm_call_map: Dict[UUID, LlmAppCall] = {}
        for call_model in llm_call_models:
            llm_call_map[call_model.id] = self._to_llm_app_call(call_model)

        response_map: Dict[UUID, LlmAppResponse] = {}
        if llm_call_models:
            llm_call_ids = [call_model.id for call_model in llm_call_models]
            response_models: List[LlmAppResponseModel] = (
                session.query(LlmAppResponseModel)
                .filter(LlmAppResponseModel.llm_app_call_id.in_(llm_call_ids))
                .order_by(LlmAppResponseModel.created_at.desc())
                .all()
            )
            for response_model in response_models:
                if response_model.llm_app_call_id in response_map:
                    continue
                response_map[response_model.llm_app_call_id] = self._to_llm_app_response(response_model)

        trace_llm_calls = [
            TraceLlmAppCall(
                llm_app_call=llm_call_map[call_model.id],
                llm_app_response=response_map.get(call_model.id),
            )
            for call_model in llm_call_models
        ]

        mcp_models: List[McpAppToolCallModel] = (
            session.query(McpAppToolCallModel)
            .filter(McpAppToolCallModel.source_app_call_id == source_model.id)
            .order_by(McpAppToolCallModel.created_at.asc())
            .all()
        )

        blocked_description_map: Dict[UUID, str] = {}
        blocked_type_map: Dict[UUID, str] = {}
        if mcp_models:
            blocked_type_ids = {model.blocked_by_type_id for model in mcp_models if model.blocked_by_type_id}
            if blocked_type_ids:
                blocked_type_models = (
                    session.query(BlockedByTypeModel).filter(BlockedByTypeModel.id.in_(blocked_type_ids)).all()
                )
                blocked_description_map = {
                    blocked_type_model.id: blocked_type_model.description for blocked_type_model in blocked_type_models
                }
                blocked_type_map = {
                    blocked_type_model.id: blocked_type_model.type for blocked_type_model in blocked_type_models
                }

        trace_mcp_calls = [
            TraceMcpAppToolCall(
                tool_call=self._to_mcp_app_tool_call(mcp_model),
                blocked_by_description=blocked_description_map.get(mcp_model.blocked_by_type_id),
                blocked_by_type=blocked_type_map.get(mcp_model.blocked_by_type_id),
            )
            for mcp_model in mcp_models
        ]

        return Trace(
            source_app_call=source,
            source_app_response=source_app_response,
            llm_app_calls=trace_llm_calls,
            mcp_app_tool_calls=trace_mcp_calls,
        )

    @staticmethod
    def _to_source_app_call(model: SourceAppCallModel) -> SourceAppCall:
        return SourceAppCall(
            id=model.id,
            token=model.token,
            input=model.input,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_llm_app_call(model: LlmAppCallModel) -> LlmAppCall:
        return LlmAppCall(
            id=model.id,
            source_app_call_id=model.source_app_call_id,
            token=model.token,
            proxy_call_id=model.proxy_call_id,
            messages=model.messages,
            tools=model.tools,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_llm_app_response(model: LlmAppResponseModel) -> LlmAppResponse:
        return LlmAppResponse(
            id=model.id,
            llm_app_call_id=model.llm_app_call_id,
            token=model.token,
            proxy_call_id=model.proxy_call_id,
            message=model.message,
            tool_calls=model.tool_calls,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_mcp_app_tool_call(model: McpAppToolCallModel) -> McpAppToolCall:
        return McpAppToolCall(
            id=model.id,
            source_app_call_id=model.source_app_call_id,
            llm_app_call_id=model.llm_app_call_id,
            llm_app_response_id=model.llm_app_response_id,
            token=model.token,
            tool=model.tool,
            blocked=model.blocked,
            blocked_by_type_id=model.blocked_by_type_id,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_source_app_response(model: SourceAppResponseModel) -> SourceAppResponse:
        return SourceAppResponse(
            id=model.id,
            source_app_call_id=model.source_app_call_id,
            token=model.token,
            output=model.output,
            created_at=model.created_at,
        )
