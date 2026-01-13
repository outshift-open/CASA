import os
from fastapi import Request
from litellm.proxy._types import UserAPIKeyAuth as BaseUserAPIKeyAuth
from pydantic import model_validator

import identity_auth_sdk


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
        sdk_config = identity_auth_sdk.Configuration(
            host = os.getenv("AUTH_SERVER_URL", "http://localhost:8000"),
        )

        print("Validating API key:", api_key)

        with identity_auth_sdk.ApiClient(sdk_config) as api_client:
            api_instance = identity_auth_sdk.DefaultApi(api_client)
            introspect_resp = api_instance.introspect(api_key)

            print("API key valid:", introspect_resp.active)

            if introspect_resp.active:
                return UserAPIKeyAuth(
                    api_key=api_key,
                )
            else:
                raise Exception("Invalid API key -> " + api_key)
    except Exception:
        raise Exception("Invalid API key")
