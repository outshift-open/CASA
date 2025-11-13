"""A FastAPI application that implements an OAuth2 token endpoint."""

import json
import logging

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.requests import Request
from idp import create_keycloak_client, get_keycloak_token
from pydantic import BaseModel

# pylint:disable=logging-fstring-interpolation

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


# --- Pydantic Models ---
class TokenRequestParams(BaseModel):
    """Pydantic model for the token query parameters."""

    client_id: str
    grant_type: str
    client_assertion_type: str
    client_assertion: str
    state: str | None = None


class TokenIntrospectParams(BaseModel):
    """Pydantic model for the token introspection parameters."""

    client_id: str
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


# --- Temp Persistence ---
clients_db = {}
token_db = {}

# --- FastAPI App ---
app = FastAPI()


# --- Token Endpoint ---
@app.post("/oauth2/default/v1/token")
async def token(req: Request):
    """
    Token endpoint to issue tokens based on client assertions.

    This endpoint expects query parameters with:
    - client_id: The client_id.
    - grant_type: The type of grant being requested.
    - client_assertion_type: The type of client assertion.
    - client_assertion: The client assertion itself.
    - state: An optional custom state parameter.
    """
    # FastAPI automatically parses the form data into the Pydantic model.
    # The data is now validated and available in `data`.

    # Extract form data
    form = await req.form()
    data = TokenRequestParams(**form)

    logger.debug(f"Parsed token request parameters: {data}")

    # Check if client exists in our temp DB
    if data.client_id in clients_db:
        client = clients_db[data.client_id]
        logger.debug(f"Found existing client in DB: {client}")
    else:
        # Create client
        keycloak_client = create_keycloak_client(data.client_id)

        # Store client in temp DB
        client = Client(
            client_id=keycloak_client["clientId"],
            name=keycloak_client["name"],
            secret=keycloak_client.get("secret"),
        )
        clients_db[data.client_id] = client

    logger.debug(f"Created or retrieved Keycloak client: {client}")

    # Check if token exists
    state = json.loads(data.state) if data.state else {}
    if client.client_id in token_db:
        # It needs to be sent in the state
        existing_token = token_db[client.client_id]["access_token"]
        provided_token = state.get("access_token")

        logger.debug(
            f"Existing token found for client {client.client_id}: {existing_token}"
        )
        logger.debug(f"Provided token in state: {provided_token}")

        if "access_token" not in state or existing_token != provided_token:
            logger.debug("Invalid access token provided.")

            # Return unauthorized
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not permitted",
            )

    # Get a access_token from keycloak
    keycloak_token = get_keycloak_token(
        client_id=client.client_id,
        client_secret=client.secret,
        tools=state.get("tools", []),
        input=state.get("input", ""),
        act=state.get("act", {}),
        sub=state.get("sub", ""),
        scopes=state.get("scopes", []),
    )

    # Add to temp token DB
    token_db[client.client_id] = keycloak_token

    # For demonstration purposes, we'll just return a dummy token.
    return TokenResponse(access_token=keycloak_token["access_token"],
                         token_type="Bearer")


@app.post("/oauth2/default/v1/introspect")
async def introspect_token(req: Request):
    """Introspect the given token."""

    # Extract form data
    form = await req.form()
    data = TokenIntrospectParams(**form)

    for client_id, token_data in token_db.items():
        if token_data["access_token"] == data.token:
            return {
                "active": True,
                "client_id": client_id,
                "scope": token_data.get("scope", ""),
                "exp": token_data.get("expires_in", 0),
            }

    return {"active": False}


@app.post("/oauth2/default/v1/revoke")
async def revoke(_: Request):
    """Revoke the given token."""

    # Clear the token database for demonstration purposes
    token_db.clear()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
