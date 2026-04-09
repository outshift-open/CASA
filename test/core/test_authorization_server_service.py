"""Unit tests for AuthorizationServerService."""

from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest

from identity_auth_server.core.types import App, AppType
from identity_auth_server.services.authorization_server import AuthorizationServerService


def _make_service(app_repository):
    return AuthorizationServerService(
        authorization_server_repository=MagicMock(),
        app_repository=app_repository,
        idp_client=MagicMock(),
        mcp_discover=MagicMock(),
        user_input_repository=MagicMock(),
        tracer=MagicMock(),
        tool_check_factory=MagicMock(),
    )


def _mock_app(mas_id: UUID | None = None) -> App:
    return App(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        name="Test App",
        type=AppType.CLIENT,
        base_url="http://localhost",
        mas_id=mas_id,
    )


@pytest.fixture
def mas_id() -> UUID:
    """Return a fixed MAS UUID for use in tests."""
    return UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def token_claims():
    """Return minimal JWT claims for a client app token."""
    return {
        "sub": "http://localhost/my-app/client",
        "uiid": "some-user-input-id",
    }


def test_introspect_token_includes_mas_id(mas_id, token_claims):
    """mas_id is derived from the DB app record and included in the response."""
    app_repository = MagicMock()
    app_repository.get_app_by_id.return_value = _mock_app(mas_id=mas_id)

    service = _make_service(app_repository)

    with patch("identity_auth_server.services.authorization_server.jwt.decode", return_value=token_claims):
        result = service._introspect_token("fake-token")

    assert result.active is True
    assert result.mas_id == str(mas_id)


def test_introspect_token_mas_id_none_when_app_has_no_mas(token_claims):
    """mas_id is None when the app is not linked to a MAS."""
    app_repository = MagicMock()
    app_repository.get_app_by_id.return_value = _mock_app(mas_id=None)

    service = _make_service(app_repository)

    with patch("identity_auth_server.services.authorization_server.jwt.decode", return_value=token_claims):
        result = service._introspect_token("fake-token")

    assert result.active is True
    assert result.mas_id is None


def test_introspect_token_inactive_when_app_not_found(token_claims):
    """Token is marked inactive when the app referenced in sub does not exist."""
    app_repository = MagicMock()
    app_repository.get_app_by_id.return_value = None

    service = _make_service(app_repository)

    with patch("identity_auth_server.services.authorization_server.jwt.decode", return_value=token_claims):
        result = service._introspect_token("fake-token")

    assert result.active is False


def test_introspect_token_inactive_when_app_not_client(mas_id, token_claims):
    """Token is marked inactive when the app in sub is not a CLIENT type."""
    app_repository = MagicMock()
    app_repository.get_app_by_id.return_value = App(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        name="Agent App",
        type=AppType.AGENT,
        base_url="http://localhost",
        mas_id=mas_id,
    )

    service = _make_service(app_repository)

    with patch("identity_auth_server.services.authorization_server.jwt.decode", return_value=token_claims):
        result = service._introspect_token("fake-token")

    assert result.active is False
