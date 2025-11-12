"""Routing module for Session operations."""

from abc import ABC
from typing import Annotated

from fastapi import APIRouter, Body, Form, HTTPException
from sqlalchemy.exc import IntegrityError

from identity_auth_server.core.exceptions import ResourceNotFoundError
from identity_auth_server.core.session.types import (
    SessionLlmAppInput,
    SessionLlmAppOutput,
    SessionMcpAppInput,
    SessionMcpAppOutput,
    SessionSourceAppInput,
    SessionSourceAppOutput,
)
from identity_auth_server.core.token.types import TokenRequestParams
from identity_auth_server.services.session import SessionService


class SessionRoute(ABC):
    """Interface for SessionRoute."""

    router: APIRouter


class SessionRouteImpl:
    """Expose session routes backed by the postgres implementation."""

    def __init__(self, session_service: SessionService):
        """Initialize the SessionRoute with a service."""
        self.router = APIRouter()
        self.service = session_service

        @self.router.post("/session/get_source_app_call_token")
        def get_source_app_token(
            # session_source_app_input: SessionSourceAppInput,
            client_id: Annotated[str, Form()],
            grant_type: Annotated[str, Form()],
            client_assertion_type: Annotated[str, Form()],
            client_assertion: Annotated[str, Form()],
            input: Annotated[str, Form()] = "",
        ) -> str:
            """Create a source session token for subsequent calls."""
            # prepare token request data
            data = TokenRequestParams(
                client_id=client_id,
                grant_type=grant_type,
                client_assertion_type=client_assertion_type,
                client_assertion=client_assertion,
                input=input,
            )

            session_source_app_input = SessionSourceAppInput(input=input)

            try:
                return self.service.create_source_app_session(session_source_app_input, data)
            except IntegrityError as exc:  # pragma: no cover - extremely unlikely with UUID tokens
                raise HTTPException(status_code=409, detail="Source session token already exists") from exc
            except Exception as exc:  # pragma: no cover - safety net
                raise HTTPException(status_code=500, detail="Failed to create source session token: ") from exc

        @self.router.post("/session/get_llm_app_call_token")
        def get_llm_app_token(
            client_id: Annotated[str, Form()],
            grant_type: Annotated[str, Form()],
            client_assertion_type: Annotated[str, Form()],
            client_assertion: Annotated[str, Form()],
            source_app_call_token: Annotated[str | None, Form()] = None,
        ) -> str:
            """Create an LLM session token associated with a source token."""
            # prepare token request data
            data = TokenRequestParams(
                client_id=client_id,
                grant_type=grant_type,
                client_assertion_type=client_assertion_type,
                client_assertion=client_assertion,
            )

            session_llm_app_input = SessionLlmAppInput(source_app_call_token=source_app_call_token)

            try:
                return self.service.create_llm_app_session(session_llm_app_input, data)
            except ResourceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except IntegrityError as exc:  # pragma: no cover - extremely unlikely with UUID tokens
                raise HTTPException(status_code=409, detail="LLM session token already exists") from exc
            except Exception as exc:  # pragma: no cover - safety net
                raise HTTPException(status_code=500, detail="Failed to create LLM session token") from exc

        @self.router.post("/session/get_mcp_app_call_token")
        def get_mcp_app_token(
            client_id: Annotated[str, Form()],
            grant_type: Annotated[str, Form()],
            client_assertion_type: Annotated[str, Form()],
            client_assertion: Annotated[str, Form()],
            source_app_call_token: Annotated[str | None, Form()] = None,
            llm_app_call_token: Annotated[str | None, Form()] = None,
            mcp_server_url: Annotated[str | None, Form()] = None,
        ) -> str:
            """Create an MCP session token tied to source and LLM sessions."""
            # prepare token request data
            data = TokenRequestParams(
                client_id=client_id,
                grant_type=grant_type,
                client_assertion_type=client_assertion_type,
                client_assertion=client_assertion,
            )

            session_mcp_app_input = SessionMcpAppInput(
                source_app_call_token=source_app_call_token,
                llm_app_call_token=llm_app_call_token,
                mcp_server_url=mcp_server_url,
            )

            try:
                return self.service.create_mcp_app_session(session_mcp_app_input, data)
            except ResourceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except IntegrityError as exc:  # pragma: no cover - extremely unlikely with UUID tokens
                raise HTTPException(status_code=409, detail="MCP session token already exists") from exc
            except Exception as exc:  # pragma: no cover - safety net
                print()
                print()
                print()
                print(exc)
                print()
                print()
                print()
                raise HTTPException(status_code=500, detail="Failed to create MCP session token") from exc

        @self.router.post("/session/validate_source_app_call_token")
        def validate_source_app_call_token(
            source_app_call_token: str = Body(..., embed=True, alias="source_app_call_token"),
        ) -> SessionSourceAppOutput:
            """Validate that the supplied source session token exists."""
            try:
                return self.service.validate_source_app_call_token(source_app_call_token)
            except ResourceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except Exception as exc:  # pragma: no cover - safety net
                raise HTTPException(status_code=500, detail="Failed to validate source session token") from exc

        @self.router.post("/session/validate_llm_app_call_token")
        def validate_llm_app_call_token(
            llm_app_call_token: str = Body(..., embed=True, alias="llm_app_call_token"),
        ) -> SessionLlmAppOutput:
            """Validate that the supplied LLM session token exists."""
            try:
                return self.service.validate_llm_app_call_token(llm_app_call_token)
            except ResourceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except Exception as exc:  # pragma: no cover - safety net
                raise HTTPException(status_code=500, detail="Failed to validate LLM session token") from exc

        @self.router.post("/session/validate_mcp_app_call_token")
        def validate_mcp_app_call_token(
            mcp_app_call_token: str = Body(..., embed=True, alias="mcp_app_call_token"),
        ) -> SessionMcpAppOutput:
            """Validate that the supplied MCP session token exists."""
            try:
                return self.service.validate_mcp_app_call_token(mcp_app_call_token)
            except ResourceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except Exception as exc:  # pragma: no cover - safety net
                raise HTTPException(status_code=500, detail="Failed to validate MCP session token") from exc
