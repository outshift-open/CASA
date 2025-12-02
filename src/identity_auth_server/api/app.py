"""API for Identity Service ZTA."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from identity_auth_server.api.routes.authorization_service.authorization_service import AuthorizationServiceRouteImpl
from identity_auth_server.core.repositories.app import AppPostgresRepository
from identity_auth_server.core.repositories.authorization_server import AuthorizationServerPostgresRepository
from identity_auth_server.database.postgres.postgres import PostgresDB
from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import (
    TaskToolMatcherFactory,
    TaskToolMatcherType,
)
from identity_auth_server.services.authorization_server import AuthorizationServerServiceImpl
from identity_auth_server.thirdparty.idp.keycloak.keycloak import KeycloakManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s  [%(name)s] %(message)s")
logger = logging.getLogger(__name__)

database = PostgresDB()

# initialize the task tool matcher factory - no state needed
task_tool_matcher_factory = TaskToolMatcherFactory()
task_tool_matcher = task_tool_matcher_factory.create(TaskToolMatcherType.LLM_VERIFIER)

# # initialize the source app call service
# source_app_call_repository = SourceAppCallPostgresRepository(database)
# source_app_call_service = SourceAppCallServiceImpl(source_app_call_repository)
#
# # initialize the source app response service
# source_app_response_repository = SourceAppResponsePostgresRepository(database)
# source_app_response_service = SourceAppResponseServiceImpl(source_app_response_repository)
#
# # initialize the llm app call service
# llm_app_call_repository = LlmAppCallPostgresRepository(database)
# llm_app_call_service = LlmAppCallServiceImpl(llm_app_call_repository)
#
# # initialize the llm app response service
# llm_app_response_repository = LlmAppResponsePostgresRepository(database)
# llm_app_response_service = LlmAppResponseServiceImpl(llm_app_response_repository)
#
# # initialize the mcp app tool call service
# mcp_app_tool_call_repository = McpAppToolCallPostgresRepository(database)
# mcp_app_tool_call_service = McpAppToolCallServiceImpl(
#     mcp_app_tool_call_repository,
#     llm_app_response_repository,
#     source_app_call_repository,
#     task_tool_matcher,
# )

# initialize the trace service
# trace_repository = TracePostgresRepository(database)
# trace_service = TraceServiceImpl(trace_repository)

with database.session_scope() as session:
    # initialize the authorization service
    authorization_server_repository = AuthorizationServerPostgresRepository(session)
    app_repository = AppPostgresRepository(session)
    keycloak_manager = KeycloakManager()
    authorization_server_service = AuthorizationServerServiceImpl(
        authorization_server_repository,
        app_repository,
        keycloak_manager,
        api_url="http://localhost:3000",
    )

    # initialize the session service
    # session_repository = SessionPostgresRepository(database)
    # mcp_discover_service = McpDiscoverServiceImpl()
    # session_service = SessionServiceImpl(
    #     session_repository,
    #     llm_app_response_repository,
    #     mcp_discover_service,
    #     task_tool_matcher,
    #     source_app_call_repository,
    # )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        """Application lifespan manager that runs migrations on startup."""
        logger.info("Application starting up...")
        # database.run_startup_migrations()
        yield

    app = FastAPI(lifespan=lifespan)

    # source_app_call_route = SourceAppCallRouteImpl(source_app_call_service)
    # source_app_response_route = SourceAppResponseRouteImpl(source_app_response_service)
    # llm_app_call_route = LlmAppCallRouteImpl(llm_app_call_service)
    # llm_app_response_route = LlmAppResponseRouteImpl(llm_app_response_service)
    # mcp_app_tool_call_route = McpAppToolCallRouteImpl(mcp_app_tool_call_service)
    # trace_route = TraceRouteImpl(trace_service)
    # session_route = SessionRouteImpl(session_service)

    authorization_server_route = AuthorizationServiceRouteImpl(authorization_server_service)

    app.include_router(authorization_server_route.router)
    # app.include_router(source_app_call_route.router)
    # app.include_router(source_app_response_route.router)
    # app.include_router(llm_app_call_route.router)
    # app.include_router(llm_app_response_route.router)
    # app.include_router(mcp_app_tool_call_route.router)
    # app.include_router(trace_route.router)
    # app.include_router(session_route.router)

    # Allow all origins (for local development)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # or ["http://localhost:3000"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
