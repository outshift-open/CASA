"""Basic middleware for FastAPI app"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Basic authentication middleware for identity verification"""

    # Routes that should bypass authentication
    EXCLUDED_PATHS = {"/oauth/client-metadata.json"}

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log incoming request
        logger.info(f"Incoming request: {request.method} {request.url}")

        # Skip authentication for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            logger.info(f"Skipping authentication for excluded path: {request.url.path}")
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning("Missing Authorization header")
            return Response(
                content="Authorization header required", status_code=401, headers={"WWW-Authenticate": "Bearer"}
            )

        # Basic token validation and extract token
        token = self._validate_and_extract_token(auth_header)
        if not token:
            logger.warning("Invalid token provided")
            return Response(content="Invalid or expired token", status_code=401, headers={"WWW-Authenticate": "Bearer"})

        # Store the token in request state for use in endpoints
        request.state.bearer_token = token

        # Process the request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")

        logger.info(f"Request processed in {process_time:.4f}s with status {response.status_code}")

        return response

    def _validate_and_extract_token(self, auth_header: str) -> str:
        """Validate and extract the bearer token from Authorization header
        Returns the token if valid, None otherwise
        """
        try:
            # Expected format: "Bearer <token>"
            token_type, token = auth_header.split(" ", 1)
            if token_type.lower() != "bearer":
                return None

            # Add your token validation logic here
            # For now, just check if token is not empty
            token = token.strip()
            if not token:
                return None

            return token

        except ValueError:
            return None
