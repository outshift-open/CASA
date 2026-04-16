"""Unit tests for K8s CRD service layer."""

from unittest.mock import Mock

import pytest

from identity_auth_server.core.types import AppType, ToolCheckFlags
from identity_auth_server.k8s.k8s_crd_service import K8sCRDService
from identity_auth_server.k8s.k8s_types import (
    ToolCheckType,
)


@pytest.fixture
def crd_service():
    """Create K8sCRDService with mock service dependencies."""
    return K8sCRDService(
        mas_service=Mock(),
        app_service=Mock(),
        idp_client=Mock(),
    )


class TestK8sCRDService:
    """Tests for K8sCRDService."""

    def test_convert_tool_checks_to_flags(self, crd_service):
        """Test conversion of tool checks list to flags."""
        checks = [
            ToolCheckType.DETERMINISTIC_TOOL_SELECTED,
            ToolCheckType.AI_POWERED_TOOL_MATCH,
        ]

        flags = crd_service._convert_tool_checks_to_flags(checks)

        assert flags & ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED
        assert flags & ToolCheckFlags.AI_POWERED_TOOL_MATCH
        assert not (flags & ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS)

    def test_convert_flags_to_tool_checks(self, crd_service):
        """Test conversion of flags to tool checks list."""
        flags = ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED | ToolCheckFlags.AI_POWERED_TOOL_MATCH

        checks = crd_service._convert_flags_to_tool_checks(flags)

        assert ToolCheckType.DETERMINISTIC_TOOL_SELECTED in checks
        assert ToolCheckType.AI_POWERED_TOOL_MATCH in checks
        assert ToolCheckType.DETERMINISTIC_LLM_SELECTED_TOOLS not in checks

    def test_convert_app_type(self, crd_service):
        """Test app type conversion."""
        assert crd_service._convert_app_type(AppType.AGENT) == "agent"
        assert crd_service._convert_app_type(AppType.CLIENT) == "client"
        assert crd_service._convert_app_type(AppType.MCP_SERVER) == "mcp_server"

    def test_convert_empty_flags(self, crd_service):
        """Test that NONE flags produce an empty list."""
        checks = crd_service._convert_flags_to_tool_checks(ToolCheckFlags.NONE)
        assert checks == []

    def test_convert_all_flags(self, crd_service):
        """Test that all flags are round-tripped correctly."""
        all_checks = [
            ToolCheckType.DETERMINISTIC_TOOL_SELECTED,
            ToolCheckType.DETERMINISTIC_LLM_SELECTED_TOOLS,
            ToolCheckType.AI_POWERED_TOOL_MATCH,
        ]
        flags = crd_service._convert_tool_checks_to_flags(all_checks)
        result = crd_service._convert_flags_to_tool_checks(flags)

        assert set(result) == set(all_checks)
