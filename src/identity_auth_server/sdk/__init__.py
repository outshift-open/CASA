"""SDK export surface for the Identity Auth Server."""

from identity_auth_server.sdk import types as types
from identity_auth_server.sdk.client import IdentityAuthClient, IdentityAuthSDKError

__all__ = ["IdentityAuthClient", "IdentityAuthSDKError", "types"]
