"""API for Identity Service ZTA."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from identity_auth_server.api.routes.llm_app_call.route import LlmAppCallRouteImpl
from identity_auth_server.api.routes.llm_app_response.route import LlmAppResponseRouteImpl
from identity_auth_server.api.routes.mcp_app_tool_call.route import McpAppToolCallRouteImpl
from identity_auth_server.api.routes.session.route import SessionRouteImpl
from identity_auth_server.api.routes.source_app_call.route import SourceAppCallRouteImpl
from identity_auth_server.api.routes.source_app_response.route import SourceAppResponseRouteImpl
from identity_auth_server.api.routes.trace.route import TraceRouteImpl
from identity_auth_server.api.types import (
    IntentMcpBadgeToolMatchRequest,
    IntentMcpBadgeToolMatchResult,
    IntentMcpToolMatchRequest,
    IntentMcpToolMatchResult,
)
from identity_auth_server.api.utils import decode_badge_extract_mcp_server
from identity_auth_server.core.llm_app_call.postgres.repository import LlmAppCallPostgresRepository
from identity_auth_server.core.llm_app_response.postgres.repository import LlmAppResponsePostgresRepository
from identity_auth_server.core.mcp_app_tool_call.postgres.repository import McpAppToolCallPostgresRepository
from identity_auth_server.core.session.postgres.repository import SessionPostgresRepository
from identity_auth_server.core.source_app_call.postgres.repository import SourceAppCallPostgresRepository
from identity_auth_server.core.source_app_response.postgres.repository import SourceAppResponsePostgresRepository
from identity_auth_server.core.trace.postgres.repository import TracePostgresRepository
from identity_auth_server.database.postgres.postgres import PostgresDB
from identity_auth_server.pipelines.exceptions import PipelineValidationError
from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import (
    TaskToolMatcherFactory,
    TaskToolMatcherType,
)
from identity_auth_server.services.llm_app_call import LlmAppCallServiceImpl
from identity_auth_server.services.llm_app_response import LlmAppResponseServiceImpl
from identity_auth_server.services.mcp_app_tool_call import McpAppToolCallServiceImpl
from identity_auth_server.services.session import SessionServiceImpl
from identity_auth_server.services.source_app_call import SourceAppCallServiceImpl
from identity_auth_server.services.source_app_response import SourceAppResponseServiceImpl
from identity_auth_server.services.trace import TraceServiceImpl

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s  [%(name)s] %(message)s")
logger = logging.getLogger(__name__)

database = PostgresDB()

# initialize the task tool matcher factory - no state needed
task_tool_matcher_factory = TaskToolMatcherFactory()
task_tool_matcher = task_tool_matcher_factory.create(TaskToolMatcherType.LLM_VERIFIER)

# initialize the source app call service
source_app_call_repository = SourceAppCallPostgresRepository(database)
source_app_call_service = SourceAppCallServiceImpl(source_app_call_repository)

# initialize the source app response service
source_app_response_repository = SourceAppResponsePostgresRepository(database)
source_app_response_service = SourceAppResponseServiceImpl(source_app_response_repository)

# initialize the llm app call service
llm_app_call_repository = LlmAppCallPostgresRepository(database)
llm_app_call_service = LlmAppCallServiceImpl(llm_app_call_repository)

# initialize the llm app response service
llm_app_response_repository = LlmAppResponsePostgresRepository(database)
llm_app_response_service = LlmAppResponseServiceImpl(llm_app_response_repository)

# initialize the mcp app tool call service
mcp_app_tool_call_repository = McpAppToolCallPostgresRepository(database)
mcp_app_tool_call_service = McpAppToolCallServiceImpl(
    mcp_app_tool_call_repository,
    llm_app_response_repository,
    source_app_call_repository,
    task_tool_matcher,
)

# initialize the trace service
trace_repository = TracePostgresRepository(database)
trace_service = TraceServiceImpl(trace_repository)

# initialize the session service
session_repository = SessionPostgresRepository(database)
session_service = SessionServiceImpl(session_repository)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan manager that runs migrations on startup."""
    logger.info("Application starting up...")
    database.run_startup_migrations()
    yield


app = FastAPI(lifespan=lifespan)

source_app_call_route = SourceAppCallRouteImpl(source_app_call_service)
source_app_response_route = SourceAppResponseRouteImpl(source_app_response_service)
llm_app_call_route = LlmAppCallRouteImpl(llm_app_call_service)
llm_app_response_route = LlmAppResponseRouteImpl(llm_app_response_service)
mcp_app_tool_call_route = McpAppToolCallRouteImpl(mcp_app_tool_call_service)
trace_route = TraceRouteImpl(trace_service)
session_route = SessionRouteImpl(session_service)

app.include_router(source_app_call_route.router)
app.include_router(source_app_response_route.router)
app.include_router(llm_app_call_route.router)
app.include_router(llm_app_response_route.router)
app.include_router(mcp_app_tool_call_route.router)
app.include_router(trace_route.router)
app.include_router(session_route.router)

# Allow all origins (for local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/task/intent/mcp/badge/tool-match")
def task_intent_mcp_badge_tool_match(
    request: IntentMcpBadgeToolMatchRequest, task_tool_matcher: TaskToolMatcherType = TaskToolMatcherType.RANDOM
) -> IntentMcpBadgeToolMatchResult:
    """Endpoint to match tools based on MCP badge."""
    mcp_server = decode_badge_extract_mcp_server(request.mcp_badge)

    input = IntentMcpToolMatchRequest(task=request.task, requested_tool=request.requested_tool, mcp_server=mcp_server)

    # Create the TaskToolMatcher using the factory
    matcher = TaskToolMatcherFactory.create(task_tool_matcher)

    try:
        # Get the result - validation exceptions will be caught and converted to HTTP 400
        result = matcher.match(input)
        return result
    except PipelineValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@app.post("/task/intent/mcp/tool-match")
def task_intent_mcp_tool_match(
    request: IntentMcpToolMatchRequest, task_tool_matcher: TaskToolMatcherType = TaskToolMatcherType.RANDOM
) -> IntentMcpToolMatchResult:
    """Endpoint to match tools based on MCP tool objects."""
    # Create the TaskToolMatcher using the factory
    matcher = TaskToolMatcherFactory.create(task_tool_matcher)

    try:
        # Get the result - validation exceptions will be caught and converted to HTTP 400
        result = matcher.match(input=request)
        return result
    except PipelineValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
