import os
from fastapi import Request
from litellm.proxy._types import UserAPIKeyAuth as BaseUserAPIKeyAuth
from pydantic import model_validator

from identity_auth_server import sdk


class UserAPIKeyAuth(BaseUserAPIKeyAuth):
    """Local instance of UserAPIKeyAuth that doesn't hash API keys.
    This overrides the check_api_key validator to prevent key hashing.
    """

    @model_validator(mode="before")
    @classmethod
    def check_api_key(cls, values):
        # Simply set the token to the api_key without hashing
        if values.get("api_key") is not None:
            values.update({"token": values.get("api_key")})
        return values


async def user_api_key_auth(_: Request, api_key: str) -> UserAPIKeyAuth:
    try:
        auth_client = sdk.IdentityAuthClient(
            base_url=os.getenv("AUTH_SERVER_URL", "http://localhost:8000"),
        )

        print("Validating API key:", api_key)

        valid_token = auth_client.validate_llm_app_call_token(
            token=api_key,
        )

        print("API key valid:", valid_token.valid)

        if valid_token.valid:
            return UserAPIKeyAuth(
                api_key=api_key,
            )
        else:
            raise Exception("Invalid API key")
    except Exception:
        raise Exception("Invalid API key")
