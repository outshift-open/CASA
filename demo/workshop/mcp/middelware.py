"""Authentication and authorization middleware for FastAPI MCP app"""

import json
import logging
import time
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from identity_auth_server import sdk

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP methods that require authentication and authorization
MCP_PROTECTED_CALLS = ["tools/call", "resources/read"]


def get_mcp_request_method(body: bytes) -> str | None:
    """Extract the method from the JSON RPC request body."""
    try:
        jsonrpc_request = json.loads(body)
        return jsonrpc_request.get("method")
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Failed to extract method from request: {e}")
        return None


def is_protected_method(method: str | None) -> bool:
    """Check if the MCP method requires authentication."""
    return method in MCP_PROTECTED_CALLS


class ToolCallBlockedException(Exception):
    """Exception raised when a tool call is blocked by policy"""

    pass


class AuthenticationError(Exception):
    """Exception raised for authentication failures"""

    pass


def extract_bearer_token(auth_header: str) -> str:
    """Extract and validate bearer token from Authorization header.

    Args:
        auth_header: Authorization header value

    Returns:
        Extracted token string

    Raises:
        AuthenticationError: If header format is invalid
    """
    try:
        token_type, token = auth_header.split(" ", 1)
        if token_type.lower() != "bearer":
            raise AuthenticationError("Invalid token type, expected Bearer")
        return token.strip()
    except ValueError:
        raise AuthenticationError("Invalid Authorization header format")


def validate_tool_call(
    tool_name: str,
    token: str,
    auth_client: sdk.IdentityAuthClient,
    validation_response: sdk.types.SessionMcpAppOutput,
    mcp_server: sdk.types.McpServer,
) -> None:
    """Validate and authorize a tool call request.

    Args:
        tool_name: Name of the tool being called
        token: Bearer token for authentication
        auth_client: Identity auth client instance
        validation_response: Previous token validation response
        mcp_server: MCP server information

    Raises:
        ToolCallBlockedException: If tool call is blocked by policy
    """
    logger.info(f"Validating tool call: {tool_name}")

    tool_call_response = auth_client.create_mcp_app_tool_call(
        payload=sdk.types.McpAppToolCallInput(
            source_app_call_token=validation_response.source_app_call_token,
            llm_app_call_token=validation_response.llm_app_call_token,
            token=token,
            tool=tool_name,
            mcp_server=mcp_server,
        )
    )

    if tool_call_response.blocked:
        logger.warning(f"Tool call blocked by policy: {tool_name}")
        raise ToolCallBlockedException(f"Tool call blocked by policy: {tool_name}")


def handle_call_tool_request(
    request_data: dict, auth_header: str, auth_client: sdk.IdentityAuthClient, mcp_server: sdk.types.McpServer
) -> None:
    """Process and authorize MCP tool call requests.

    Args:
        request_data: Parsed JSON request body
        auth_header: Authorization header value
        auth_client: Identity auth client instance

    Raises:
        ToolCallBlockedException: If tool call is blocked
        AuthenticationError: If authentication fails
    """
    tool_name = request_data.get("params", {}).get("name", "unknown")
    tool_args = request_data.get("params", {}).get("arguments", {})

    logger.info(f"CallToolRequest detected - Tool: {tool_name}, Args: {tool_args}")

    token = extract_bearer_token(auth_header)
    logger.info(f"Tool call authenticated with token: {token[:10]}...")

    # Validate token and get validation response
    validation_response = auth_client.validate_mcp_app_call_token(token=token)

    # Validate tool call authorization
    validate_tool_call(tool_name, token, auth_client, validation_response, mcp_server)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication and authorization middleware for MCP requests.

    Validates bearer tokens and enforces tool call policies.
    """

    AUTH_BASE_URL = "http://localhost:8000"

    def __init__(self, app: ASGIApp, auth_base_url: Optional[str] = None, mcp_instance=None):
        """Initialize the authentication middleware.

        Args:
            app: ASGI application
            auth_base_url: Optional override for auth service URL
            mcp_instance: FastMCP instance to access available tools
        """
        super().__init__(app)
        self.auth_base_url = auth_base_url or self.AUTH_BASE_URL
        self.mcp_instance = mcp_instance

    def _create_auth_client(self) -> sdk.IdentityAuthClient:
        """Create and return an auth client instance."""
        return sdk.IdentityAuthClient(base_url=self.auth_base_url)

    async def get_available_tools(self) -> list:
        """Get list of available tools from MCP instance.

        Returns:
            List of available tools or empty list if MCP instance not provided
        """
        if self.mcp_instance:
            tools = await self.mcp_instance.list_tools()
            return tools
        return []

    def _create_error_response(self, message: str, status_code: int, is_json: bool = False) -> Response:
        """Create a standardized error response.

        Args:
            message: Error message
            status_code: HTTP status code
            is_json: Whether to format as JSON

        Returns:
            Response object
        """
        if is_json:
            content = json.dumps({"error": "Forbidden" if status_code == 403 else "Unauthorized", "message": message})
            return Response(content=content, status_code=status_code, media_type="application/json")

        headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else {}
        return Response(content=message, status_code=status_code, headers=headers)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch logic.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response
        """
        logger.info(f"Incoming request: {request.method} {request.url}")

        # Read body to check if this is a protected MCP method
        body = await request.body()
        method = get_mcp_request_method(body) if body else None

        # Only apply auth protection for protected methods
        if is_protected_method(method):
            logger.info(f"Protected method detected: {method}")

            # Validate authorization header presence
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                logger.warning("Missing Authorization header")
                return self._create_error_response("Authorization header required", 401)

            # Validate token
            auth_client = self._create_auth_client()
            try:
                token = extract_bearer_token(auth_header)
                if not self._validate_token(token, auth_client):
                    logger.warning("Invalid token provided")
                    return self._create_error_response("Invalid or expired token", 401)
            except AuthenticationError as e:
                logger.warning(f"Authentication error: {e!s}")
                return self._create_error_response(str(e), 401)

            # Validate tool call authorization for tools/call
            try:
                if body:
                    await self._analyze_request_body(body, auth_header, auth_client)
            except ToolCallBlockedException as e:
                logger.error(f"Tool call blocked: {e!s}")
                return self._create_error_response(str(e), 403, is_json=True)
        else:
            logger.info(f"Unprotected method, skipping auth: {method}")

        # Recreate the request with the consumed body
        if body:
            self._recreate_request_with_body(request, body)

        # Process request with timing
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add headers and log
        self._add_response_headers(response, request, process_time)
        logger.info(f"Request processed in {process_time:.4f}s with status {response.status_code}")

        return response

    def _recreate_request_with_body(self, request: Request, body: bytes) -> None:
        """Recreate request with consumed body so it can be read again by the handler.

        Args:
            request: Original request
            body: Body bytes that were consumed
        """
        # Store original receive for disconnect messages
        original_receive = request._receive
        body_sent = False

        async def receive():
            nonlocal body_sent

            # First call: return the body
            if not body_sent:
                body_sent = True
                return {"type": "http.request", "body": body, "more_body": False}

            # Subsequent calls: delegate to original receive for disconnect handling
            return await original_receive()

    def _add_response_headers(self, response: Response, request: Request, process_time: float) -> None:
        """Add custom headers to response.

        Args:
            response: Response object to modify
            request: Original request
            process_time: Request processing time in seconds
        """
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")

    async def _analyze_request_body(self, body: bytes, auth_header: str, auth_client: sdk.IdentityAuthClient) -> None:
        """Analyze request body for tool call requests and validate authorization.

        Args:
            body: Request body bytes
            auth_header: Authorization header value
            auth_client: Auth client instance

        Raises:
            ToolCallBlockedException: If tool call is blocked by policy
        """
        if not body:
            return

        logger.info(f"Request body: {body}")

        try:
            request_data = json.loads(body.decode("utf-8"))
            if self._is_tool_call_request(request_data):
                mcp_server = sdk.types.McpServer(
                    name=self.mcp_instance.name if self.mcp_instance else "unknown",
                    tools=await self.get_available_tools(),
                    resources=[],
                )
                handle_call_tool_request(request_data, auth_header, auth_client, mcp_server)
        except ToolCallBlockedException:
            raise
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse request body as JSON: {e}")

    def _is_tool_call_request(self, request_data: dict) -> bool:
        """Check if request is a tool call request.

        Args:
            request_data: Parsed request body

        Returns:
            True if this is a tool call request
        """
        return isinstance(request_data, dict) and request_data.get("method") == "tools/call"

    def _validate_token(self, token: str, auth_client: sdk.IdentityAuthClient) -> bool:
        """Validate bearer token with auth service.

        Args:
            token: Bearer token to validate
            auth_client: Auth client instance

        Returns:
            True if token is valid
        """
        try:
            response = auth_client.validate_mcp_app_call_token(token=token)
            logger.debug(f"Token validation response: {response}")
            return response.valid
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False
