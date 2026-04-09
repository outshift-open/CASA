"""Unit tests for K8s CRD service layer."""

from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import uuid4

import pytest

from identity_auth_server.core.k8s_types import (
    AppSpec,
    AppTypeK8s,
    MASCreateRequest,
    MASPhase,
    MASStatusUpdateRequest,
    MultiAgentSystemCRD,
    MultiAgentSystemMetadata,
    MultiAgentSystemSpec,
    MultiAgentSystemStatus,
    PolicyCreateRequest,
    TargetRef,
    ToolCheckType,
    ZTAPolicyCRD,
    ZTAPolicyMetadata,
    ZTAPolicySpec,
)
from identity_auth_server.core.types import (
    App,
    AppType,
    AuthorizationServer,
    MultiAgentSystem,
    ToolCheckFlags,
)
from identity_auth_server.services.k8s_crd_service import K8sCRDService


@pytest.fixture
def mock_repositories():
    """Create mock repositories."""
    mas_repo = Mock()
    app_repo = Mock()
    auth_srv_repo = Mock()
    idp_client = Mock()

    return {
        "mas_repo": mas_repo,
        "app_repo": app_repo,
        "auth_srv_repo": auth_srv_repo,
        "idp_client": idp_client,
    }


@pytest.fixture
def crd_service(mock_repositories):
    """Create K8sCRDService with mock dependencies."""
    return K8sCRDService(
        mas_repository=mock_repositories["mas_repo"],
        app_repository=mock_repositories["app_repo"],
        auth_srv_repository=mock_repositories["auth_srv_repo"],
        idp_client=mock_repositories["idp_client"],
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
        assert crd_service._convert_app_type(AppTypeK8s.AGENT) == "agent"
        assert crd_service._convert_app_type(AppTypeK8s.CLIENT) == "client"
        assert crd_service._convert_app_type(AppTypeK8s.MCP_SERVER) == "mcp_server"

    def test_create_mas_from_crd(self, crd_service, mock_repositories):
        """Test creating MAS from CRD."""
        # Setup
        mas_id = uuid4()
        auth_srv_id = uuid4()

        mock_auth_server = AuthorizationServer(id=auth_srv_id, realm="test-realm")
        mock_mas = MultiAgentSystem(
            id=mas_id,
            name="Test MAS",
            authorization_server_id=auth_srv_id,
            authorization_server=mock_auth_server,
        )

        mock_repositories["auth_srv_repo"].create_authorization_server.return_value = mock_auth_server
        mock_repositories["mas_repo"].create.return_value = mock_mas
        mock_repositories["app_repo"].get_mas_apps.return_value = []

        # Create CRD request
        request = MASCreateRequest(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(name="test-mas", namespace="default"),
            spec=MultiAgentSystemSpec(
                name="Test MAS",
                authorization_server="test-realm",
                apps=[
                    AppSpec(
                        name="test-app",
                        type=AppTypeK8s.CLIENT,
                        base_url="http://test:8000",
                    )
                ],
            ),
        )

        # Execute
        result = crd_service.create_mas_from_crd(request)

        # Verify
        assert result.metadata.name == "test-mas"
        assert result.metadata.namespace == "default"
        assert result.spec.name == "Test MAS"
        assert mock_repositories["auth_srv_repo"].create_authorization_server.called
        assert mock_repositories["idp_client"].create_authorization_server.called
        assert mock_repositories["mas_repo"].create.called

    def test_get_mas_crd(self, crd_service, mock_repositories):
        """Test retrieving MAS as CRD."""
        # Setup
        mas_id = uuid4()
        auth_srv_id = uuid4()

        mock_auth_server = AuthorizationServer(id=auth_srv_id, realm="test-realm")
        MultiAgentSystem(
            id=mas_id,
            name="Test MAS",
            authorization_server_id=auth_srv_id,
            authorization_server=mock_auth_server,
            enabled_tool_checks=ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED,
        )

        App(
            id=uuid4(),
            name="test-app",
            type=AppType.CLIENT,
            base_url="http://test:8000",
            mas_id=mas_id,
        )

        # Mock cache - store the MAS CRD
        crd_service._mas_cache["default/test-mas"] = MultiAgentSystemCRD(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(name="test-mas", namespace="default"),
            spec=MultiAgentSystemSpec(
                name="Test MAS",
                authorization_server="test-realm",
                apps=[],
            ),
        )

        # Execute
        result = crd_service.get_mas_crd("default", "test-mas")

        # Verify
        assert result is not None
        assert result.metadata.name == "test-mas"
        assert result.metadata.namespace == "default"

    def test_list_mas_crds_all_namespaces(self, crd_service):
        """Test listing all MAS CRDs across namespaces."""
        # Setup cache with multiple MAS in different namespaces
        crd_service._mas_cache["default/mas1"] = MultiAgentSystemCRD(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(name="mas1", namespace="default"),
            spec=MultiAgentSystemSpec(name="MAS 1", authorization_server="realm1", apps=[]),
        )
        crd_service._mas_cache["prod/mas2"] = MultiAgentSystemCRD(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(name="mas2", namespace="prod"),
            spec=MultiAgentSystemSpec(name="MAS 2", authorization_server="realm2", apps=[]),
        )

        # Execute
        result = crd_service.list_mas_crds()

        # Verify
        assert len(result) == 2
        assert any(mas.metadata.name == "mas1" for mas in result)
        assert any(mas.metadata.name == "mas2" for mas in result)

    def test_list_mas_crds_filtered_by_namespace(self, crd_service):
        """Test listing MAS CRDs filtered by namespace."""
        # Setup cache
        crd_service._mas_cache["default/mas1"] = MultiAgentSystemCRD(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(name="mas1", namespace="default"),
            spec=MultiAgentSystemSpec(name="MAS 1", authorization_server="realm1", apps=[]),
        )
        crd_service._mas_cache["prod/mas2"] = MultiAgentSystemCRD(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(name="mas2", namespace="prod"),
            spec=MultiAgentSystemSpec(name="MAS 2", authorization_server="realm2", apps=[]),
        )

        # Execute
        result = crd_service.list_mas_crds(namespace="default")

        # Verify
        assert len(result) == 1
        assert result[0].metadata.name == "mas1"
        assert result[0].metadata.namespace == "default"

    def test_update_mas_status(self, crd_service):
        """Test updating MAS status."""
        # Setup cache
        crd_service._mas_cache["default/test-mas"] = MultiAgentSystemCRD(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(name="test-mas", namespace="default"),
            spec=MultiAgentSystemSpec(name="Test MAS", authorization_server="test-realm", apps=[]),
            status=MultiAgentSystemStatus(
                phase=MASPhase.PENDING,
                apps_ready=0,
                last_sync_time=datetime.now(timezone.utc),
            ),
        )

        # Create status update
        now = datetime.now(timezone.utc)
        update = MASStatusUpdateRequest(
            status=MultiAgentSystemStatus(
                phase=MASPhase.ACTIVE,
                apps_ready=3,
                last_sync_time=now,
            )
        )

        # Execute
        result = crd_service.update_mas_status("default", "test-mas", update)

        # Verify
        assert result.status.phase == MASPhase.ACTIVE
        assert result.status.apps_ready == 3
        assert result.status.last_sync_time == now

    def test_delete_mas_crd(self, crd_service, mock_repositories):
        """Test deleting MAS CRD."""
        # Setup cache
        crd_service._mas_cache["default/test-mas"] = MultiAgentSystemCRD(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(name="test-mas", namespace="default"),
            spec=MultiAgentSystemSpec(name="Test MAS", authorization_server="test-realm", apps=[]),
        )

        # Execute
        crd_service.delete_mas_crd("default", "test-mas")

        # Verify
        assert "default/test-mas" not in crd_service._mas_cache

    def test_create_policy_from_crd(self, crd_service):
        """Test creating ZTAPolicy from CRD."""
        # Create policy request
        request = PolicyCreateRequest(
            api_version="zta.io/v1alpha1",
            kind="ZTAPolicy",
            metadata=ZTAPolicyMetadata(name="agent-policy", namespace="default"),
            spec=ZTAPolicySpec(
                target_ref=TargetRef(kind="Deployment", name="agent"),
                allowed_protocols=["mcp", "a2a"],
                allowed_endpoints=[],
            ),
        )

        # Execute
        result = crd_service.create_policy_from_crd(request)

        # Verify
        assert result.metadata.name == "agent-policy"
        assert result.metadata.namespace == "default"
        assert "mcp" in result.spec.allowed_protocols
        assert "a2a" in result.spec.allowed_protocols
        assert "default/agent-policy" in crd_service._policy_cache

    def test_get_policy_crd(self, crd_service):
        """Test retrieving ZTAPolicy as CRD."""
        # Setup cache
        crd_service._policy_cache["default/test-policy"] = ZTAPolicyCRD(
            api_version="zta.io/v1alpha1",
            kind="ZTAPolicy",
            metadata=ZTAPolicyMetadata(name="test-policy", namespace="default"),
            spec=ZTAPolicySpec(
                target_ref=TargetRef(kind="Deployment", name="test"),
                allowed_protocols=["mcp"],
                allowed_endpoints=[],
            ),
        )

        # Execute
        result = crd_service.get_policy_crd("default", "test-policy")

        # Verify
        assert result is not None
        assert result.metadata.name == "test-policy"
        assert result.metadata.namespace == "default"

    def test_list_policies_all_namespaces(self, crd_service):
        """Test listing all policies across namespaces."""
        # Setup cache
        crd_service._policy_cache["default/policy1"] = ZTAPolicyCRD(
            api_version="zta.io/v1alpha1",
            kind="ZTAPolicy",
            metadata=ZTAPolicyMetadata(name="policy1", namespace="default"),
            spec=ZTAPolicySpec(
                target_ref=TargetRef(kind="Deployment", name="test1"),
                allowed_protocols=["mcp"],
                allowed_endpoints=[],
            ),
        )
        crd_service._policy_cache["prod/policy2"] = ZTAPolicyCRD(
            api_version="zta.io/v1alpha1",
            kind="ZTAPolicy",
            metadata=ZTAPolicyMetadata(name="policy2", namespace="prod"),
            spec=ZTAPolicySpec(
                target_ref=TargetRef(kind="Deployment", name="test2"),
                allowed_protocols=["mcp"],
                allowed_endpoints=[],
            ),
        )

        # Execute
        result = crd_service.list_policy_crds()

        # Verify
        assert len(result) == 2

    def test_delete_policy_crd(self, crd_service):
        """Test deleting ZTAPolicy CRD."""
        # Setup cache
        crd_service._policy_cache["default/test-policy"] = ZTAPolicyCRD(
            api_version="zta.io/v1alpha1",
            kind="ZTAPolicy",
            metadata=ZTAPolicyMetadata(name="test-policy", namespace="default"),
            spec=ZTAPolicySpec(
                target_ref=TargetRef(kind="Deployment", name="test"),
                allowed_protocols=["mcp"],
                allowed_endpoints=[],
            ),
        )

        # Execute
        crd_service.delete_policy_crd("default", "test-policy")

        # Verify
        assert "default/test-policy" not in crd_service._policy_cache
