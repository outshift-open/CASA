# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Trace API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from casa_auth_server.api.dependencies import Container
from casa_auth_server.core.events import LLMCallEndedEvent, LLMCallStartedEvent
from casa_auth_server.services.authorization_server import AuthorizationServerService
from casa_auth_server.telemetry.tracer import Tracer

router = APIRouter(tags=["Traces"])
jwt_security = HTTPBearer()
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class LLMCallStartedRequest(BaseModel):
    """Request body for recording the start of an LLM call."""

    call_id: str
    prompt: str
    tools: str | None = None


class LLMCallEndedRequest(BaseModel):
    """Request body for recording the end of an LLM call."""

    call_id: str
    response: str
    tools: str | None = None


@router.post("/trace/llm/call_start", generate_unique_id_function=lambda _: "trace_llm_call_start")
def trace_llm_call_start(
    tracer: Annotated[Tracer, Depends(Container.get_tracer)],
    auth_server: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
    jwt: Annotated[HTTPAuthorizationCredentials, Depends(jwt_security)],
    request: LLMCallStartedRequest,
) -> LLMCallStartedEvent:
    """Record the start of an LLM call for the authenticated agent."""
    token = auth_server.introspect_token(jwt.credentials)
    if token is None or not token.active:
        raise credentials_exception

    event = LLMCallStartedEvent(
        app_id=token.app_id,
        call_id=request.call_id,
        token=jwt.credentials,
        user_input_id=token.user_input_id,
        mas_id=token.mas_id,
        prompt=request.prompt,
        tools=request.tools,
    )

    tracer.record_event(event)
    return event


@router.post("/trace/llm/call_end", generate_unique_id_function=lambda _: "trace_llm_call_end")
def trace_llm_call_end(
    tracer: Annotated[Tracer, Depends(Container.get_tracer)],
    auth_server: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
    jwt: Annotated[HTTPAuthorizationCredentials, Depends(jwt_security)],
    request: LLMCallEndedRequest,
) -> LLMCallEndedEvent:
    """Record the end of an LLM call for the authenticated agent."""
    token = auth_server.introspect_token(jwt.credentials)
    if token is None or not token.active:
        raise credentials_exception

    event = LLMCallEndedEvent(
        app_id=token.app_id,
        call_id=request.call_id,
        token=jwt.credentials,
        user_input_id=token.user_input_id,
        mas_id=token.mas_id,
        response=request.response,
        tools=request.tools,
    )

    tracer.record_event(event)
    return event


@router.get("/trace")
def get_traces(
    tracer: Annotated[Tracer, Depends(Container.get_tracer)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    mas_id: UUID | None = Query(None),
    all: bool = Query(False),
    sort_asc: bool = Query(False),
):
    """Retrieve paginated traces for all source app calls."""
    try:
        return tracer.get_traces(page, page_size, mas_id=mas_id, fetch_all=all, sort_asc=sort_asc)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    # except Exception as exc:
    #     raise HTTPException(
    #         status_code=500, detail="an unexpected error occurred while retrieving traces"
    #     ) from exc
