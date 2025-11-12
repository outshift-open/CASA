"""Convenience client for interacting with the Identity Auth Server HTTP API."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Type, TypeVar
from uuid import UUID

import httpx
from pydantic import BaseModel

from identity_auth_server.sdk.types import (
    LlmAppCall,
    LlmAppCallInput,
    LlmAppResponse,
    LlmAppResponseInput,
    McpAppToolCall,
    McpAppToolCallInput,
    SessionLlmAppOutput,
    SessionMcpAppOutput,
    SessionSourceAppOutput,
    SourceAppCall,
    SourceAppCallInput,
    SourceAppResponse,
    SourceAppResponseInput,
    Trace,
    TraceList,
)

TModel = TypeVar("TModel", bound=BaseModel)


class IdentityAuthSDKError(RuntimeError):
    """Wrap HTTP errors raised while talking to the Identity Auth Server."""

    __slots__ = ("response", "status_code")

    def __init__(self, message: str, *, status_code: int, response: httpx.Response) -> None:
        """Initialize the SDK error with HTTP response details."""
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class IdentityAuthClient(AbstractContextManager["IdentityAuthClient"]):
    """Minimal synchronous client for the Identity Auth Server API."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        headers: Mapping[str, str] | None = None,
        client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        """Create a new client.

        Args:
            base_url: Root URL of the deployed Identity Auth Server (e.g. ``http://localhost:8000``).
            timeout: Default request timeout in seconds when the client manages its own session.
            headers: Optional default headers to send with every request (e.g. auth tokens).
            client: Pre-configured ``httpx.Client``. When supplied the caller remains responsible for closing it.
            transport: Optional custom transport (useful for testing with ``httpx.MockTransport``).
        """
        if client is not None:
            self._client = client
            self._owns_client = False
        else:
            self._client = httpx.Client(
                base_url=base_url,
                timeout=timeout,
                headers=dict(headers) if headers else None,
                transport=transport,
            )
            self._owns_client = True

        self._base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Context / lifecycle helpers
    # ------------------------------------------------------------------
    def __enter__(self) -> "IdentityAuthClient":
        """Enter context manager and return self."""
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        """Exit context manager and close the client if we own it."""
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client when we own it."""
        if self._owns_client:
            self._client.close()

    # ------------------------------------------------------------------
    # High-level API wrappers
    # ------------------------------------------------------------------
    def create_source_app_call(self, payload: SourceAppCallInput | Mapping[str, Any]) -> SourceAppCall:
        """Create a new source app call record."""
        response = self._post("/source-app-call", payload)
        return self._parse_model(response, SourceAppCall)

    def create_source_app_response(self, payload: SourceAppResponseInput | Mapping[str, Any]) -> SourceAppResponse:
        """Create a new source app response record."""
        response = self._post("/source-app-response", payload)
        return self._parse_model(response, SourceAppResponse)

    def create_llm_app_call(self, payload: LlmAppCallInput | Mapping[str, Any]) -> LlmAppCall:
        """Create a new LLM app call record."""
        response = self._post("/llm-app-call", payload)
        return self._parse_model(response, LlmAppCall)

    def create_llm_app_response(self, payload: LlmAppResponseInput | Mapping[str, Any]) -> LlmAppResponse:
        """Create a new LLM app response record."""
        response = self._post("/llm-app-response", payload)
        return self._parse_model(response, LlmAppResponse)

    def create_mcp_app_tool_call(self, payload: McpAppToolCallInput | Mapping[str, Any]) -> McpAppToolCall:
        """Create a new MCP app tool call record."""
        response = self._post("/mcp-app-tool-call", payload)
        return self._parse_model(response, McpAppToolCall)

    def get_source_app_call_token(
        self, *, input: str, grant_type: str, client_id: str, client_assertion_type: str, client_assertion: str
    ) -> str:
        """Generate a token for source app call session using OAuth2 client credentials flow.

        Args:
            input: Input data for the source app call session
            grant_type: OAuth2 grant type (e.g., 'client_credentials')
            client_id: OAuth2 client identifier
            client_assertion_type: Type of client assertion (e.g., 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer')
            client_assertion: JWT assertion for client authentication
        """
        # Build form data - all parameters as form fields
        data = {
            "input": input,
            "grant_type": grant_type,
            "client_id": client_id,
            "client_assertion_type": client_assertion_type,
            "client_assertion": client_assertion,
        }

        # Use form-encoded data with proper content-type header
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = self._post_form("/session/get_source_app_call_token", data=data, headers=headers)
        return self._parse_token(response)

    def get_llm_app_call_token(
        self,
        *,
        source_app_call_token: str,
        grant_type: str,
        client_id: str,
        client_assertion_type: str,
        client_assertion: str,
    ) -> str:
        """Generate a token for LLM app call session using OAuth2 client credentials flow.

        Args:
            source_app_call_token: Token from the source app call session
            grant_type: OAuth2 grant type (e.g., 'client_credentials')
            client_id: OAuth2 client identifier
            client_assertion_type: Type of client assertion (e.g., 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer')
            client_assertion: JWT assertion for client authentication
        """
        # Build form data - all parameters as form fields
        data = {
            "source_app_call_token": source_app_call_token,
            "grant_type": grant_type,
            "client_id": client_id,
            "client_assertion_type": client_assertion_type,
            "client_assertion": client_assertion,
        }

        # Use form-encoded data with proper content-type header
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = self._post_form("/session/get_llm_app_call_token", data=data, headers=headers)
        return self._parse_token(response)

    def get_mcp_app_call_token(
        self,
        *,
        source_app_call_token: str,
        llm_app_call_token: str,
        mcp_server_url: str,
        grant_type: str,
        client_id: str,
        client_assertion_type: str,
        client_assertion: str,
    ) -> str:
        """Generate a token for MCP app call session using OAuth2 client credentials flow.

        Args:
            source_app_call_token: Token from the source app call session
            llm_app_call_token: Token from the LLM app call session
            mcp_server_url: URL of the MCP server
            grant_type: OAuth2 grant type (e.g., 'client_credentials')
            client_id: OAuth2 client identifier
            client_assertion_type: Type of client assertion (e.g., 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer')
            client_assertion: JWT assertion for client authentication
        """
        # Build form data - all parameters as form fields
        data = {
            "source_app_call_token": source_app_call_token,
            "llm_app_call_token": llm_app_call_token,
            "mcp_server_url": mcp_server_url,
            "grant_type": grant_type,
            "client_id": client_id,
            "client_assertion_type": client_assertion_type,
            "client_assertion": client_assertion,
        }

        # Use form-encoded data with proper content-type header
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = self._post_form("/session/get_mcp_app_call_token", data=data, headers=headers)
        return self._parse_token(response)

    def validate_source_app_call_token(self, token: str) -> SessionSourceAppOutput:
        """Validate a source app call token and return session data."""
        response = self._post("/session/validate_source_app_call_token", {"source_app_call_token": token})
        return self._parse_model(response, SessionSourceAppOutput)

    def validate_llm_app_call_token(self, token: str) -> SessionLlmAppOutput:
        """Validate an LLM app call token and return session data."""
        response = self._post("/session/validate_llm_app_call_token", {"llm_app_call_token": token})
        return self._parse_model(response, SessionLlmAppOutput)

    def validate_mcp_app_call_token(self, token: str) -> SessionMcpAppOutput:
        """Validate an MCP app call token and return session data."""
        response = self._post("/session/validate_mcp_app_call_token", {"mcp_app_call_token": token})
        return self._parse_model(response, SessionMcpAppOutput)

    def get_trace(self, source_app_call_id: UUID) -> Trace:
        """Retrieve a trace by source app call ID."""
        response = self._get(f"/trace/{source_app_call_id}")
        return self._parse_model(response, Trace)

    def get_traces(self, *, page: int = 1, page_size: int = 20) -> TraceList:
        """Retrieve a paginated list of traces."""
        response = self._get("/trace", params={"page": page, "page_size": page_size})
        return self._parse_model(response, TraceList)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get(self, path: str, *, params: Mapping[str, Any] | None = None) -> httpx.Response:
        return self._request("GET", path, params=params)

    def _post(self, path: str, payload: BaseModel | Mapping[str, Any]) -> httpx.Response:
        json_payload = self._to_json(payload)
        return self._request("POST", path, json=json_payload)

    def _post_form(
        self,
        path: str,
        *,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        """Post with form-encoded data."""
        kwargs: dict[str, Any] = {"data": data}
        if headers is not None:
            kwargs["headers"] = headers
        return self._request("POST", path, **kwargs)

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        response = self._client.request(method, path, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:  # pragma: no cover - exercised via dedicated test
            detail: Any
            try:
                detail = exc.response.json()
            except ValueError:  # pragma: no cover - fallback for non-JSON errors
                detail = exc.response.text

            message = f"HTTP {exc.response.status_code} {exc.response.reason_phrase}"
            if isinstance(detail, dict) and detail.get("detail"):
                message = f"{message}: {detail['detail']}"
            elif isinstance(detail, str) and detail:
                message = f"{message}: {detail}"

            raise IdentityAuthSDKError(message, status_code=exc.response.status_code, response=exc.response) from exc
        return response

    @staticmethod
    def _to_json(payload: BaseModel | Mapping[str, Any]) -> Mapping[str, Any]:
        if isinstance(payload, BaseModel):
            return payload.model_dump(mode="json", by_alias=True)
        return dict(payload)

    @staticmethod
    def _parse_model(response: httpx.Response, model: Type[TModel]) -> TModel:
        return model.model_validate(response.json())

    @staticmethod
    def _parse_token(response: httpx.Response) -> str:
        token = response.json()
        if not isinstance(token, str):
            raise IdentityAuthSDKError(
                "Expected token response to be a JSON string",
                status_code=response.status_code,
                response=response,
            )
        return token


class AsyncIdentityAuthClient(AbstractAsyncContextManager["AsyncIdentityAuthClient"]):
    """Async client for the Identity Auth Server API."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        headers: Mapping[str, str] | None = None,
        client: httpx.AsyncClient | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Create a new async client.

        Args:
            base_url: Root URL of the deployed Identity Auth Server (e.g. ``http://localhost:8000``).
            timeout: Default request timeout in seconds when the client manages its own session.
            headers: Optional default headers to send with every request (e.g. auth tokens).
            client: Pre-configured ``httpx.AsyncClient``. When supplied the caller remains responsible for closing it.
            transport: Optional custom transport (useful for testing with ``httpx.MockTransport``).
        """
        if client is not None:
            self._client = client
            self._owns_client = False
        else:
            self._client = httpx.AsyncClient(
                base_url=base_url,
                timeout=timeout,
                headers=dict(headers) if headers else None,
                transport=transport,
            )
            self._owns_client = True

        self._base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Context / lifecycle helpers
    # ------------------------------------------------------------------
    async def __aenter__(self) -> "AsyncIdentityAuthClient":
        """Enter async context manager and return self."""
        return self

    async def __aexit__(self, exc_type, exc, exc_tb) -> None:
        """Exit async context manager and close the client if we own it."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP client when we own it."""
        if self._owns_client:
            await self._client.aclose()

    # ------------------------------------------------------------------
    # High-level API wrappers
    # ------------------------------------------------------------------
    async def create_source_app_call(self, payload: SourceAppCallInput | Mapping[str, Any]) -> SourceAppCall:
        """Create a new source app call record."""
        response = await self._post("/source-app-call", payload)
        return self._parse_model(response, SourceAppCall)

    async def create_source_app_response(
        self, payload: SourceAppResponseInput | Mapping[str, Any]
    ) -> SourceAppResponse:
        """Create a new source app response record."""
        response = await self._post("/source-app-response", payload)
        return self._parse_model(response, SourceAppResponse)

    async def create_llm_app_call(self, payload: LlmAppCallInput | Mapping[str, Any]) -> LlmAppCall:
        """Create a new LLM app call record."""
        response = await self._post("/llm-app-call", payload)
        return self._parse_model(response, LlmAppCall)

    async def create_llm_app_response(self, payload: LlmAppResponseInput | Mapping[str, Any]) -> LlmAppResponse:
        """Create a new LLM app response record."""
        response = await self._post("/llm-app-response", payload)
        return self._parse_model(response, LlmAppResponse)

    async def create_mcp_app_tool_call(self, payload: McpAppToolCallInput | Mapping[str, Any]) -> McpAppToolCall:
        """Create a new MCP app tool call record."""
        response = await self._post("/mcp-app-tool-call", payload)
        return self._parse_model(response, McpAppToolCall)

    async def get_source_app_call_token(
        self, *, input: str, grant_type: str, client_id: str, client_assertion_type: str, client_assertion: str
    ) -> str:
        """Generate a token for source app call session using OAuth2 client credentials flow.

        Args:
            input: Input data for the source app call session
            grant_type: OAuth2 grant type (e.g., 'client_credentials')
            client_id: OAuth2 client identifier
            client_assertion_type: Type of client assertion (e.g., 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer')
            client_assertion: JWT assertion for client authentication
        """
        # Build form data - all parameters as form fields
        data = {
            "input": input,
            "grant_type": grant_type,
            "client_id": client_id,
            "client_assertion_type": client_assertion_type,
            "client_assertion": client_assertion,
        }

        # Use form-encoded data with proper content-type header
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = await self._post_form("/session/get_source_app_call_token", data=data, headers=headers)
        return self._parse_token(response)

    async def get_llm_app_call_token(
        self,
        *,
        source_app_call_token: str,
        grant_type: str,
        client_id: str,
        client_assertion_type: str,
        client_assertion: str,
    ) -> str:
        """Generate a token for LLM app call session using OAuth2 client credentials flow.

        Args:
            source_app_call_token: Token from the source app call session
            grant_type: OAuth2 grant type (e.g., 'client_credentials')
            client_id: OAuth2 client identifier
            client_assertion_type: Type of client assertion (e.g., 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer')
            client_assertion: JWT assertion for client authentication
        """
        # Build form data - all parameters as form fields
        data = {
            "source_app_call_token": source_app_call_token,
            "grant_type": grant_type,
            "client_id": client_id,
            "client_assertion_type": client_assertion_type,
            "client_assertion": client_assertion,
        }

        # Use form-encoded data with proper content-type header
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = await self._post_form("/session/get_llm_app_call_token", data=data, headers=headers)
        return self._parse_token(response)

    async def get_mcp_app_call_token(
        self,
        *,
        source_app_call_token: str,
        llm_app_call_token: str,
        mcp_server_url: str,
        grant_type: str,
        client_id: str,
        client_assertion_type: str,
        client_assertion: str,
    ) -> str:
        """Generate a token for MCP app call session using OAuth2 client credentials flow.

        Args:
            source_app_call_token: Token from the source app call session
            llm_app_call_token: Token from the LLM app call session
            mcp_server_url: URL of the MCP server
            grant_type: OAuth2 grant type (e.g., 'client_credentials')
            client_id: OAuth2 client identifier
            client_assertion_type: Type of client assertion (e.g., 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer')
            client_assertion: JWT assertion for client authentication
        """
        # Build form data - all parameters as form fields
        data = {
            "source_app_call_token": source_app_call_token,
            "llm_app_call_token": llm_app_call_token,
            "mcp_server_url": mcp_server_url,
            "grant_type": grant_type,
            "client_id": client_id,
            "client_assertion_type": client_assertion_type,
            "client_assertion": client_assertion,
        }

        # Use form-encoded data with proper content-type header
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = await self._post_form("/session/get_mcp_app_call_token", data=data, headers=headers)
        return self._parse_token(response)

    async def validate_source_app_call_token(self, token: str) -> SessionSourceAppOutput:
        """Validate a source app call token and return session data."""
        response = await self._post("/session/validate_source_app_call_token", {"source_app_call_token": token})
        return self._parse_model(response, SessionSourceAppOutput)

    async def validate_llm_app_call_token(self, token: str) -> SessionLlmAppOutput:
        """Validate an LLM app call token and return session data."""
        response = await self._post("/session/validate_llm_app_call_token", {"llm_app_call_token": token})
        return self._parse_model(response, SessionLlmAppOutput)

    async def validate_mcp_app_call_token(self, token: str) -> SessionMcpAppOutput:
        """Validate an MCP app call token and return session data."""
        response = await self._post("/session/validate_mcp_app_call_token", {"mcp_app_call_token": token})
        return self._parse_model(response, SessionMcpAppOutput)

    async def get_trace(self, source_app_call_id: UUID) -> Trace:
        """Retrieve a trace by source app call ID."""
        response = await self._get(f"/trace/{source_app_call_id}")
        return self._parse_model(response, Trace)

    async def get_traces(self, *, page: int = 1, page_size: int = 20) -> TraceList:
        """Retrieve a paginated list of traces."""
        response = await self._get("/trace", params={"page": page, "page_size": page_size})
        return self._parse_model(response, TraceList)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    async def _get(self, path: str, *, params: Mapping[str, Any] | None = None) -> httpx.Response:
        return await self._request("GET", path, params=params)

    async def _post(self, path: str, payload: BaseModel | Mapping[str, Any]) -> httpx.Response:
        json_payload = self._to_json(payload)
        return await self._request("POST", path, json=json_payload)

    async def _post_form(
        self,
        path: str,
        *,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        """Post with form-encoded data."""
        kwargs: dict[str, Any] = {"data": data}
        if headers is not None:
            kwargs["headers"] = headers
        return await self._request("POST", path, **kwargs)

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        response = await self._client.request(method, path, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:  # pragma: no cover - exercised via dedicated test
            detail: Any
            try:
                detail = exc.response.json()
            except ValueError:  # pragma: no cover - fallback for non-JSON errors
                detail = exc.response.text

            message = f"HTTP {exc.response.status_code} {exc.response.reason_phrase}"
            if isinstance(detail, dict) and detail.get("detail"):
                message = f"{message}: {detail['detail']}"
            elif isinstance(detail, str) and detail:
                message = f"{message}: {detail}"

            raise IdentityAuthSDKError(message, status_code=exc.response.status_code, response=exc.response) from exc
        return response

    @staticmethod
    def _to_json(payload: BaseModel | Mapping[str, Any]) -> Mapping[str, Any]:
        if isinstance(payload, BaseModel):
            return payload.model_dump(mode="json", by_alias=True)
        return dict(payload)

    @staticmethod
    def _parse_model(response: httpx.Response, model: Type[TModel]) -> TModel:
        return model.model_validate(response.json())

    @staticmethod
    def _parse_token(response: httpx.Response) -> str:
        token = response.json()
        if not isinstance(token, str):
            raise IdentityAuthSDKError(
                "Expected token response to be a JSON string",
                status_code=response.status_code,
                response=response,
            )
        return token


__all__ = ["AsyncIdentityAuthClient", "IdentityAuthClient", "IdentityAuthSDKError"]
