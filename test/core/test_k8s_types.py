"""Unit tests for Kubernetes CRD types."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from identity_auth_server.core.k8s_types import (
    AllowedEndpoint,
    AppSpec,
    AppTypeK8s,
    LLMEndpoint,
    MASCreateRequest,
    MASPhase,
    MASStatusUpdateRequest,
    MultiAgentSystemCRD,
    MultiAgentSystemMetadata,
    MultiAgentSystemSpec,
    MultiAgentSystemStatus,
    PolicyCreateRequest,
    PolicyPhase,
    TargetRef,
    ToolCheckType,
    ZTAPolicyCRD,
    ZTAPolicyMetadata,
    ZTAPolicySpec,
    ZTAPolicyStatus,
)


class TestMultiAgentSystemCRD:
    """Tests for MultiAgentSystem CRD models."""

    def test_create_minimal_mas_crd(self):
        """Test creating a minimal MultiAgentSystem CRD."""
        crd = MultiAgentSystemCRD(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(
                name="test-mas",
                namespace="default",
            ),
            spec=MultiAgentSystemSpec(
                name="Test MAS",
                authorization_server="test-realm",
                apps=[],
            ),
        )

        assert crd.api_version == "zta.io/v1alpha1"
        assert crd.kind == "MultiAgentSystem"
        assert crd.metadata.name == "test-mas"
        assert crd.metadata.namespace == "default"
        assert crd.spec.name == "Test MAS"
        assert crd.spec.authorization_server == "test-realm"
        assert len(crd.spec.apps) == 0

    def test_create_mas_with_apps(self):
        """Test creating MultiAgentSystem with multiple apps."""
        crd = MultiAgentSystemCRD(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(
                name="prod-mas",
                namespace="production",
                labels={"environment": "production"},
            ),
            spec=MultiAgentSystemSpec(
                name="Production MAS",
                authorization_server="prod-realm",
                enabled_tool_checks=[
                    ToolCheckType.DETERMINISTIC_TOOL_SELECTED,
                    ToolCheckType.AI_POWERED_TOOL_MATCH,
                ],
                apps=[
                    AppSpec(
                        name="orchestrator-agent",
                        type=AppTypeK8s.AGENT,
                        base_url="http://orchestrator:8000",
                    ),
                    AppSpec(
                        name="filesystem-mcp",
                        type=AppTypeK8s.MCP_SERVER,
                        base_url="http://fs-mcp:8080",
                    ),
                ],
            ),
        )

        assert crd.metadata.name == "prod-mas"
        assert crd.metadata.namespace == "production"
        assert crd.metadata.labels == {"environment": "production"}
        assert len(crd.spec.apps) == 2
        assert crd.spec.apps[0].name == "orchestrator-agent"
        assert crd.spec.apps[0].type == AppTypeK8s.AGENT
        assert crd.spec.apps[1].type == AppTypeK8s.MCP_SERVER

    def test_mas_with_status(self):
        """Test MultiAgentSystem with status."""
        now = datetime.now(timezone.utc)
        crd = MultiAgentSystemCRD(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(name="test-mas", namespace="default"),
            spec=MultiAgentSystemSpec(
                name="Test MAS",
                authorization_server="test-realm",
                apps=[],
            ),
            status=MultiAgentSystemStatus(
                phase=MASPhase.ACTIVE,
                apps_ready=2,
                last_sync_time=now,
            ),
        )

        assert crd.status is not None
        assert crd.status.phase == MASPhase.ACTIVE
        assert crd.status.apps_ready == 2
        assert crd.status.last_sync_time == now

    def test_invalid_app_type_raises_error(self):
        """Test that invalid app type raises validation error."""
        with pytest.raises(ValidationError):
            AppSpec(
                name="bad-app",
                type="invalid_type",  # type: ignore
                base_url="http://bad:8000",
            )

    def test_mas_create_request_validation(self):
        """Test MASCreateRequest validation."""
        request = MASCreateRequest(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(name="test", namespace="default"),
            spec=MultiAgentSystemSpec(
                name="Test",
                authorization_server="test-realm",
                apps=[],
            ),
        )

        assert request.metadata.name == "test"
        assert request.spec.name == "Test"


class TestZTAPolicyCRD:
    """Tests for ZTAPolicy CRD models."""

    def test_create_minimal_policy(self):
        """Test creating a minimal ZTAPolicy."""
        policy = ZTAPolicyCRD(
            api_version="zta.io/v1alpha1",
            kind="ZTAPolicy",
            metadata=ZTAPolicyMetadata(name="agent-policy", namespace="default"),
            spec=ZTAPolicySpec(
                target_ref=TargetRef(kind="Deployment", name="agent-deployment"),
                allowed_protocols=["mcp"],
                allowed_endpoints=[],
            ),
        )

        assert policy.api_version == "zta.io/v1alpha1"
        assert policy.kind == "ZTAPolicy"
        assert policy.metadata.name == "agent-policy"
        assert policy.spec.target_ref.kind == "Deployment"
        assert policy.spec.target_ref.name == "agent-deployment"
        assert "mcp" in policy.spec.allowed_protocols

    def test_policy_with_all_features(self):
        """Test creating ZTAPolicy with all features."""
        policy = ZTAPolicyCRD(
            api_version="zta.io/v1alpha1",
            kind="ZTAPolicy",
            metadata=ZTAPolicyMetadata(
                name="full-policy",
                namespace="production",
                labels={"app": "agent"},
            ),
            spec=ZTAPolicySpec(
                target_ref=TargetRef(kind="Deployment", name="agent"),
                allowed_protocols=["mcp", "a2a"],
                allowed_endpoints=[
                    AllowedEndpoint(name="mcp-server", namespace="production", port=8080),
                    AllowedEndpoint(name="zta-auth", namespace="zta-system", port=8443),
                ],
                llm_endpoint=LLMEndpoint(fqdn="api.openai.com", port=443),
            ),
        )

        assert len(policy.spec.allowed_endpoints) == 2
        assert policy.spec.allowed_endpoints[0].name == "mcp-server"
        assert policy.spec.allowed_endpoints[0].namespace == "production"
        assert policy.spec.allowed_endpoints[0].port == 8080
        assert policy.spec.llm_endpoint is not None
        assert policy.spec.llm_endpoint.fqdn == "api.openai.com"
        assert policy.spec.llm_endpoint.port == 443

    def test_policy_with_status(self):
        """Test ZTAPolicy with status."""
        now = datetime.now(timezone.utc)
        policy = ZTAPolicyCRD(
            api_version="zta.io/v1alpha1",
            kind="ZTAPolicy",
            metadata=ZTAPolicyMetadata(name="test-policy", namespace="default"),
            spec=ZTAPolicySpec(
                target_ref=TargetRef(kind="Deployment", name="test"),
                allowed_protocols=["mcp"],
                allowed_endpoints=[],
            ),
            status=ZTAPolicyStatus(
                phase=PolicyPhase.ACTIVE,
                cilium_policy_name="cnp-test-policy",
                last_sync_time=now,
            ),
        )

        assert policy.status is not None
        assert policy.status.phase == PolicyPhase.ACTIVE
        assert policy.status.cilium_policy_name == "cnp-test-policy"
        assert policy.status.last_sync_time == now

    def test_invalid_target_ref_kind_raises_error(self):
        """Test that invalid target ref kind raises validation error."""
        with pytest.raises(ValidationError):
            TargetRef(kind="InvalidKind", name="test")  # type: ignore

    def test_policy_create_request_validation(self):
        """Test PolicyCreateRequest validation."""
        request = PolicyCreateRequest(
            api_version="zta.io/v1alpha1",
            kind="ZTAPolicy",
            metadata=ZTAPolicyMetadata(name="test", namespace="default"),
            spec=ZTAPolicySpec(
                target_ref=TargetRef(kind="Deployment", name="test"),
                allowed_protocols=["mcp"],
                allowed_endpoints=[],
            ),
        )

        assert request.metadata.name == "test"
        assert request.spec.target_ref.name == "test"


class TestToolCheckType:
    """Tests for ToolCheckType enum."""

    def test_all_tool_check_types(self):
        """Test all tool check types are defined."""
        assert ToolCheckType.DETERMINISTIC_TOOL_SELECTED == "DETERMINISTIC_TOOL_SELECTED"
        assert ToolCheckType.DETERMINISTIC_LLM_SELECTED_TOOLS == "DETERMINISTIC_LLM_SELECTED_TOOLS"
        assert ToolCheckType.AI_POWERED_TOOL_MATCH == "AI_POWERED_TOOL_MATCH"


class TestAppTypeK8s:
    """Tests for AppTypeK8s enum."""

    def test_all_app_types(self):
        """Test all app types are defined."""
        assert AppTypeK8s.AGENT == "agent"
        assert AppTypeK8s.CLIENT == "client"
        assert AppTypeK8s.MCP_SERVER == "mcp_server"


class TestMASPhase:
    """Tests for MAS phase enum."""

    def test_all_phases(self):
        """Test all MAS phases are defined."""
        assert MASPhase.PENDING == "Pending"
        assert MASPhase.ACTIVE == "Active"
        assert MASPhase.FAILED == "Failed"


class TestPolicyPhase:
    """Tests for Policy phase enum."""

    def test_all_phases(self):
        """Test all policy phases are defined."""
        assert PolicyPhase.PENDING == "Pending"
        assert PolicyPhase.ACTIVE == "Active"
        assert PolicyPhase.FAILED == "Failed"
