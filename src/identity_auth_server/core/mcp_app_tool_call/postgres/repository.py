"""PostgreSQL implementation of the McpAppToolCall repository."""

import datetime
import logging
from uuid import uuid4

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.mcp_app_tool_call.postgres.models import BlockedByTypeModel, McpAppToolCallModel
from identity_auth_server.core.mcp_app_tool_call.repository import McpAppToolCallRepository
from identity_auth_server.core.mcp_app_tool_call.types import (
    BlockedByType,
    BlockedByTypeName,
    McpAppToolCall,
    McpAppToolCallInput,
)
from identity_auth_server.core.source_app_call.postgres.models import SourceAppCallModel
from identity_auth_server.database.postgres.postgres import PostgresDB

logger = logging.getLogger(__name__)


class McpAppToolCallPostgresRepository(McpAppToolCallRepository):
    """PostgreSQL-backed repository for MCP app tool calls."""

    def __init__(self, database: PostgresDB):
        """Initialize the repository with a database connection."""
        self.database = database

    def create(
        self,
        mcp_app_tool_call: McpAppToolCallInput,
        blocked: bool = False,
        blocked_by_type_id: str | None = None,
    ) -> McpAppToolCall:
        """Persist a new MCP app tool call."""
        try:
            with self.database.session_scope() as session:
                source_app_call = (
                    session.query(SourceAppCallModel)
                    .filter(SourceAppCallModel.token == mcp_app_tool_call.source_app_call_token)
                    .one_or_none()
                )
                if source_app_call is None:
                    logger.warning(
                        "Source app call missing for MCP tool call creation",
                        extra={
                            "source_app_call_token": mcp_app_tool_call.source_app_call_token,
                            "mcp_app_tool_call_token": mcp_app_tool_call.token,
                        },
                    )
                    raise ResourceNotFoundError(
                        "Source app call not found for token: {token}".format(
                            token=mcp_app_tool_call.source_app_call_token
                        )
                    )

                llm_app_call = None
                llm_app_response = None

                db_mcp_app_tool_call = McpAppToolCallModel(
                    id=uuid4(),
                    source_app_call_id=source_app_call.id,
                    llm_app_call_id=llm_app_call.id if llm_app_call else None,
                    llm_app_response_id=llm_app_response.id if llm_app_response else None,
                    token=mcp_app_tool_call.token,
                    tool=mcp_app_tool_call.tool,
                    blocked=blocked,
                    blocked_by_type_id=blocked_by_type_id,
                    created_at=datetime.datetime.now(datetime.timezone.utc),
                )

                session.add(db_mcp_app_tool_call)
                session.flush()
                session.refresh(db_mcp_app_tool_call)

                return McpAppToolCall(
                    id=db_mcp_app_tool_call.id,
                    source_app_call_id=db_mcp_app_tool_call.source_app_call_id,
                    llm_app_call_id=db_mcp_app_tool_call.llm_app_call_id,
                    llm_app_response_id=db_mcp_app_tool_call.llm_app_response_id,
                    token=db_mcp_app_tool_call.token,
                    tool=db_mcp_app_tool_call.tool,
                    blocked=db_mcp_app_tool_call.blocked,
                    blocked_by_type_id=db_mcp_app_tool_call.blocked_by_type_id,
                    created_at=db_mcp_app_tool_call.created_at,
                )
        except ResourceNotFoundError:
            raise
        except Exception:
            logger.exception(
                "Failed to create MCP app tool call",
                extra={
                    "mcp_app_tool_call_token": mcp_app_tool_call.token,
                    "source_app_call_token": mcp_app_tool_call.source_app_call_token,
                    "llm_app_call_token": mcp_app_tool_call.llm_app_call_token,
                    "tool": mcp_app_tool_call.tool,
                },
            )
            raise

    def get_blocked_by_type_by_name(self, *, name: BlockedByTypeName) -> BlockedByType:
        """Fetch a blocked-by type definition by its canonical name."""
        with self.database.session_scope() as session:
            blocked_by = session.query(BlockedByTypeModel).filter(BlockedByTypeModel.name == name.value).one_or_none()

            if blocked_by is None:
                logger.warning(
                    "Blocked-by type lookup failed",
                    extra={"blocked_by_type_name": name.value},
                )
                raise ResourceNotFoundError("Blocked-by type not found for name: {name}".format(name=name.value))

            return BlockedByType(
                id=blocked_by.id, name=blocked_by.name, description=blocked_by.description, type=blocked_by.type
            )
