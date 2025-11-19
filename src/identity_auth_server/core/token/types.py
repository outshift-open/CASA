"""Data models for tokens."""

from typing import Optional

from pydantic import BaseModel


class ActorClaim(BaseModel):
    """Pydantic model for the JWT 'act' (actor) claim.

    Represents an actor in a delegation chain. Can be nested to represent
    a chain of delegation where the outermost act claim represents the
    current actor and nested act claims represent prior actors.

    As per RFC 8693, for access control decisions, only the top-level
    claims and the current actor (outermost act claim) should be considered.
    """

    sub: str  # Subject identifier of the actor
    act: Optional["ActorClaim"] = None  # Nested actor claim for delegation chains


class TokenRequestParams(BaseModel):
    """Pydantic model for the token query parameters."""

    client_id: str
    grant_type: str
    client_assertion_type: str
    client_assertion: str
    input: str | None = None
    tools: list[str] | None = None
    act: ActorClaim | None = None
    input_id: str | None = None
    sub: str | None = None
    scopes: list[str] | None = None
    type: str | None = None


class TokenIntrospectParams(BaseModel):
    """Pydantic model for the token introspection parameters."""

    # client_id: str
    token: str


class Client(BaseModel):
    """Pydantic model for a client."""

    client_id: str
    name: str
    secret: str | None = None


class TokenResponse(BaseModel):
    """Pydantic model for the token response."""

    access_token: str
    token_type: str


class TokenIntrospectResponse(BaseModel):
    """Pydantic model for the token introspection response."""

    sub: str | None = None
    client_id: str | None = None
    scope: str | None = None
    exp: int | None = None
    tools: str | None = None
    input: str | None = None
    act: str | None = None
    input_id: str | None = None
