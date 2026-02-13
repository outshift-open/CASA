"""FastAPI dependency providers and lightweight DI helpers.

This module defines small provider helpers (`singleton`, `scoped`) and a `Container`
class exposing dependency callables used with FastAPI's `Depends`.
"""

import os
from abc import ABC, abstractmethod
from typing import Annotated, Any, Callable, Generator, Generic, TypeVar

from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from identity_auth_server.core.repositories.app import AppPostgresRepository, AppRepository
from identity_auth_server.core.repositories.authorization_server import (
    AuthorizationServerPostgresRepository,
    AuthorizationServerRepository,
)
from identity_auth_server.core.repositories.multi_agent_system import (
    MultiAgentSystemPostgresRepository,
    MultiAgentSystemRepository,
)
from identity_auth_server.core.repositories.scope import ScopePostgresRepository, ScopeRepository
from identity_auth_server.core.repositories.user_input import UserInputPostgresRepository
from identity_auth_server.database.postgres.postgres import PostgresDB
from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import TaskToolMatcher, TaskToolMatcherFactory
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatcherType
from identity_auth_server.services.app_service import AppService
from identity_auth_server.services.authorization_server import AuthorizationServerService
from identity_auth_server.services.mas_service import MultiAgentSystemService
from identity_auth_server.services.mcp_discover import McpDiscoverService
from identity_auth_server.services.scope_service import ScopeService
from identity_auth_server.telemetry.tracer import Tracer
from identity_auth_server.telemetry.tracer_repository import TracerPostgresRepository, TracerRepository
from identity_auth_server.thirdparty.idp.keycloak import KeycloakManager

T = TypeVar("T")


class Provider(ABC, Generic[T]):
    """Provider interface for non-scoped dependencies."""

    @abstractmethod
    def provide(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Provide an instance of `T` using `func` as a factory."""
        raise NotImplementedError


def singleton(factory: Callable[..., T]) -> Callable[..., T]:
    """Creates a singleton lifetime service, one instance is available throughout the whole lifetime of the application."""

    class SingletonBase(Provider[T]):
        """Provider implementation caching a single instance."""

        def __init__(self) -> None:
            self._instance: T | None = None

        def provide(self, func: Callable[..., T], *args, **kwargs) -> T:
            """Return the cached instance, creating it once if needed."""
            if func is not None and self._instance is None:
                self._instance = func(*args, **kwargs)
            return self._instance

    singleton_type = type("Singleton", (SingletonBase,), {"__call__": factory})
    return singleton_type()


class ScopedProvider(ABC, Generic[T]):
    """Provider interface for request-scoped dependencies."""

    @abstractmethod
    def provide(self, func: Callable[..., T], *args, **kwargs) -> Generator[T, Any, None]:
        """Provide a scoped instance of `T` using `func` as a factory."""
        raise NotImplementedError


def scoped(
    factory: Callable[..., T],
    after_yield_callback: Callable[[T], None] | None = None,
    on_error_callback: Callable[[T, Exception], None] | None = None,
    on_exit_callback: Callable[[T], None] | None = None,
) -> Callable[..., T]:
    """Creates a scoped lifetime service, it is created once per client request."""

    class ScopedBase(ScopedProvider[T]):
        """Provider implementation yielding an instance per scope."""

        def __init__(self) -> None:
            """Initialize the scoped provider."""

        def provide(self, func: Callable[..., T], *args, **kwargs):
            """Yield an instance and run lifecycle callbacks."""
            instance = func(*args, **kwargs)
            try:
                yield instance
                if after_yield_callback:
                    after_yield_callback(instance)
            except Exception as e:
                if on_error_callback:
                    on_error_callback(instance, e)
                raise e
            finally:
                if on_exit_callback is not None:
                    on_exit_callback(instance)

    scoped_type = type("Scoped", (ScopedBase,), {"__call__": factory})
    return scoped_type()


# TODO: think of a better way to create factories
# mypy: disable-error-code="misc"
class Container:
    """Dependency container exposing FastAPI `Depends` callables."""

    def provide_database(self: Provider[PostgresDB]):
        """Create a Postgres database handle."""
        return self.provide(lambda: PostgresDB())

    get_database = singleton(factory=provide_database)

    def provide_sessionmaker(self: Provider[sessionmaker], db: Annotated[PostgresDB, Depends(get_database)]):
        """Create a SQLAlchemy/SQLModel session factory."""
        return self.provide(lambda: sessionmaker(db.engine, class_=Session, expire_on_commit=False))

    get_sessionmaker = singleton(factory=provide_sessionmaker)

    def provide_session(
        self: ScopedProvider[Session], session_maker: Annotated[sessionmaker, Depends(get_sessionmaker)]
    ):
        """Provide a request-scoped session."""
        yield from self.provide(lambda: session_maker())

    @staticmethod
    def session_commit(session: Session):
        """Commit the session after a successful request."""
        session.commit()

    @staticmethod
    def session_rollback(session: Session, ex: Exception):
        """Rollback the session if the request errors."""
        session.rollback()

    @staticmethod
    def exit_session(session: Session):
        """Close the session at the end of the request."""
        session.close()

    get_session = scoped(
        factory=provide_session,
        after_yield_callback=session_commit,
        on_error_callback=session_rollback,
        on_exit_callback=exit_session,
    )

    def provide_task_tool_matcher(self: Provider[TaskToolMatcher]):
        """Provide the task/tool matcher implementation."""
        factory = TaskToolMatcherFactory()
        return factory.create(TaskToolMatcherType.LLM_VERIFIER)

    get_task_tool_matcher = singleton(factory=provide_task_tool_matcher)

    @staticmethod
    def get_app_repository(session: Annotated[Session, Depends(get_session)]):
        """Provide the App repository."""
        return AppPostgresRepository(session)

    @staticmethod
    def get_auth_server_repository(session: Annotated[Session, Depends(get_session)]):
        """Provide the Authorization Server repository."""
        return AuthorizationServerPostgresRepository(session=session)

    @staticmethod
    def get_scope_repository(session: Annotated[Session, Depends(get_session)]):
        """Provide the Scope repository."""
        return ScopePostgresRepository(session=session)

    @staticmethod
    def get_user_input_repository(session: Annotated[Session, Depends(get_session)]):
        """Provide the UserInput repository."""
        return UserInputPostgresRepository(session=session)

    @staticmethod
    def get_tracer_repository(session: Annotated[Session, Depends(get_session)]):
        """Provide the Tracer repository."""
        return TracerPostgresRepository(session=session)

    @staticmethod
    def get_mas_repository(session: Annotated[Session, Depends(get_session)]):
        """Provide the MultiAgentSystem repository."""
        return MultiAgentSystemPostgresRepository(session=session)

    @staticmethod
    def get_keycloak_manager():
        """Provide a Keycloak manager instance."""
        return KeycloakManager(
            server_url=os.getenv("IDP_SERVER_URL", "http://localhost:8080/"),
            username=os.getenv("IDP_ADMIN_USERNAME", "admin"),
            password=os.getenv("IDP_ADMIN_PASSWORD", "admin"),
        )

    @staticmethod
    def get_mcp_discover():
        """Provide the MCP discovery service."""
        return McpDiscoverService()

    @staticmethod
    def get_tracer(tracer_repository: Annotated[TracerRepository, Depends(get_tracer_repository)]):
        """Provide the tracer service."""
        return Tracer(tracer_repository=tracer_repository)

    @staticmethod
    def get_authorization_service(
        authorization_server_repository: Annotated[AuthorizationServerRepository, Depends(get_auth_server_repository)],
        app_repository: Annotated[AppRepository, Depends(get_app_repository)],
        keycloak_manager: Annotated[KeycloakManager, Depends(get_keycloak_manager)],
        mcp_discover: Annotated[McpDiscoverService, Depends(get_mcp_discover)],
        task_tool_matcher: Annotated[TaskToolMatcher, Depends(get_task_tool_matcher)],
        user_input_repository: Annotated[UserInputPostgresRepository, Depends(get_user_input_repository)],
        tracer: Annotated[Tracer, Depends(get_tracer)],
    ):
        """Provide the authorization server service."""
        return AuthorizationServerService(
            authorization_server_repository,
            app_repository,
            keycloak_manager,
            api_url=os.getenv("AUTH_SERVER_URL", "http://localhost:3000"),
            mcp_discover=mcp_discover,
            task_tool_matcher=task_tool_matcher,
            user_input_repository=user_input_repository,
            tracer=tracer,
        )

    @staticmethod
    def get_app_service(
        app_repository: Annotated[AppRepository, Depends(get_app_repository)],
        scope_repository: Annotated[ScopeRepository, Depends(get_scope_repository)],
        keycloak_manager: Annotated[KeycloakManager, Depends(get_keycloak_manager)],
        authorization_server_repository: Annotated[AuthorizationServerRepository, Depends(get_auth_server_repository)],
    ):
        """Provide the app service."""
        return AppService(app_repository, scope_repository, keycloak_manager, authorization_server_repository)

    @staticmethod
    def get_scope_service(
        scope_repository: Annotated[ScopeRepository, Depends(get_scope_repository)],
    ):
        """Provide the scope service."""
        return ScopeService(scope_repository)

    @staticmethod
    def get_mas_service(
        mas_repository: Annotated[MultiAgentSystemRepository, Depends(get_mas_repository)],
        app_repository: Annotated[AppRepository, Depends(get_app_repository)],
    ):
        """Provide the MultiAgentSystem service."""
        return MultiAgentSystemService(mas_repository, app_repository)
