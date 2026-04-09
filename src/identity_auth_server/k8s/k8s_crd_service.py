"""Service layer for managing Kubernetes CRD resources (MultiAgentSystem and ZTAPolicy)."""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from identity_auth_server.core.idp.idp_client import IdpClient
from identity_auth_server.core.types import MultiAgentSystem, ToolCheckFlags
from identity_auth_server.k8s.k8s_types import (
    AppCredentials,
    AppSpec,
    AppTypeK8s,
    MASCreateRequest,
    MASPhase,
    MASStatusUpdateRequest,
    MASUpdateRequest,
    MultiAgentSystemCRD,
    MultiAgentSystemMetadata,
    MultiAgentSystemSpec,
    MultiAgentSystemStatus,
    ToolCheckType,
)
from identity_auth_server.services.app_service import AppRequest, AppService
from identity_auth_server.services.mas_service import (
    MultiAgentSystemCreateRequest,
    MultiAgentSystemService,
    MultiAgentSystemUpdateRequest,
)

logger = logging.getLogger(__name__)


class K8sCRDService:
    """Service for managing Kubernetes CRD resources in the ZTA control plane."""

    def __init__(  # noqa: D107
        self,
        mas_service: MultiAgentSystemService,
        app_service: AppService,
        idp_client: IdpClient,
    ):
        self._mas_service = mas_service
        self._app_service = app_service
        self._idp_client = idp_client

    def _convert_tool_checks_to_flags(self, checks: List[ToolCheckType]) -> ToolCheckFlags:
        """Convert list of tool check types to ToolCheckFlags."""
        flags = ToolCheckFlags.NONE
        for check in checks:
            if check == ToolCheckType.DETERMINISTIC_TOOL_SELECTED:
                flags |= ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED
            elif check == ToolCheckType.DETERMINISTIC_LLM_SELECTED_TOOLS:
                flags |= ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS
            elif check == ToolCheckType.AI_POWERED_TOOL_MATCH:
                flags |= ToolCheckFlags.AI_POWERED_TOOL_MATCH
        return flags

    def _convert_flags_to_tool_checks(self, flags: ToolCheckFlags) -> List[ToolCheckType]:
        """Convert ToolCheckFlags to list of tool check types."""
        checks = []
        if flags & ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED:
            checks.append(ToolCheckType.DETERMINISTIC_TOOL_SELECTED)
        if flags & ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS:
            checks.append(ToolCheckType.DETERMINISTIC_LLM_SELECTED_TOOLS)
        if flags & ToolCheckFlags.AI_POWERED_TOOL_MATCH:
            checks.append(ToolCheckType.AI_POWERED_TOOL_MATCH)
        return checks

    def _convert_app_type(self, app_type: AppTypeK8s) -> str:
        """Convert K8s app type to internal app type."""
        return app_type.value

    def _mas_to_crd(self, mas: MultiAgentSystem, namespace: str = "default") -> MultiAgentSystemCRD:
        """Convert internal MAS model to CRD representation."""
        # Get apps for this MAS
        apps = self._app_service.get_mas_apps(str(mas.id))

        # Build app specs
        app_specs = [AppSpec(name=app.name, type=AppTypeK8s(app.type), base_url=app.base_url) for app in apps]

        # Build status
        status = MultiAgentSystemStatus(
            phase=MASPhase.ACTIVE,
            apps_ready=len(apps),
            last_sync_time=datetime.now(timezone.utc),
        )

        return MultiAgentSystemCRD(
            api_version="zta.io/v1alpha1",
            kind="MultiAgentSystem",
            metadata=MultiAgentSystemMetadata(
                name=mas.name.lower().replace(" ", "-"),
                namespace=namespace,
                uid=str(mas.id),
            ),
            spec=MultiAgentSystemSpec(
                name=mas.name,
                enabled_tool_checks=self._convert_flags_to_tool_checks(mas.enabled_tool_checks or ToolCheckFlags.NONE),
                apps=app_specs,
            ),
            status=status,
        )

    def create_mas_from_crd(self, request: MASCreateRequest) -> MultiAgentSystemCRD:
        """Create a new MultiAgentSystem from CRD request."""
        mas = self._mas_service.create_mas(
            MultiAgentSystemCreateRequest(
                name=request.spec.name,
                namespace=request.metadata.namespace,
                enabled_tool_checks=self._convert_tool_checks_to_flags(request.spec.enabled_tool_checks),
                k8s_name=request.metadata.name,
            )
        )

        # Create apps and collect credentials
        created_apps = []
        credentials = []
        for app_spec in request.spec.apps:
            try:
                app = self._app_service.create_app(
                    AppRequest(
                        name=app_spec.name,
                        base_url=app_spec.base_url,
                        mas_id=str(mas.id),
                        type=self._convert_app_type(app_spec.type),
                    )
                )

                created_apps.append(app)

                # Collect credentials for operator to create K8s secrets
                if app.client_credentials:
                    credentials.append(
                        AppCredentials(
                            app_name=app.name,
                            client_id=app.client_credentials.client_id,
                            client_secret=app.client_credentials.client_secret or "",
                            secret_name=f"{app.name}-oauth2-credentials",
                        )
                    )
            except Exception as e:
                logger.error(f"Failed to create app {app_spec.name}: {e}")

        # Build CRD response
        crd = self._mas_to_crd(mas, namespace=request.metadata.namespace)
        crd.metadata.uid = str(mas.id)
        crd.status = MultiAgentSystemStatus(
            phase=MASPhase.ACTIVE if created_apps else MASPhase.FAILED,
            apps_ready=len(created_apps),
            last_sync_time=datetime.now(timezone.utc),
            message=f"Created {len(created_apps)}/{len(request.spec.apps)} apps successfully",
            credentials=credentials if credentials else None,
        )

        return crd

    def get_mas_crd(self, namespace: str, mas_id: str) -> Optional[MultiAgentSystemCRD]:
        """Get a MultiAgentSystem CRD by namespace and name."""
        mas = self._mas_service.get_mas_by_id(mas_id)
        crd = self._mas_to_crd(mas, namespace)
        return crd

    def list_mas_crds(self, namespace: Optional[str] = None) -> List[MultiAgentSystemCRD]:
        """List all MultiAgentSystem CRDs, optionally filtered by namespace."""
        all_mas = self._mas_service.get_all_mas()
        crds = []

        for mas in all_mas:
            ns = namespace or "default"
            if mas.namespace == ns:
                crd = self._mas_to_crd(mas, ns)
                crds.append(crd)

        return crds

    def update_mas_crd(self, namespace: str, name: str, request: MASUpdateRequest) -> MultiAgentSystemCRD:
        """Update a MultiAgentSystem CRD spec."""
        # Convert name to UUID
        mas_id = self._mas_service.get_id_by_name(name, namespace)

        mas = self._mas_service.update_mas(mas_id, MultiAgentSystemUpdateRequest(name=request.spec.name))

        # # Update realm if changed
        # if request.spec.authorization_server != existing_crd.spec.authorization_server:
        #     # This is complex - would require realm migration
        #     logger.warning("Authorization server realm change not yet supported")

        existing_apps = self._app_service.get_mas_apps(mas_id)
        for app in existing_apps:
            self._app_service.delete_app(str(app.id))

        for app_spec in request.spec.apps:
            try:
                app = self._app_service.create_app(
                    AppRequest(
                        name=app_spec.name,
                        base_url=app_spec.base_url,
                        mas_id=str(mas.id),
                        type=self._convert_app_type(app_spec.type),
                    )
                )
            except Exception as e:
                logger.error(f"Failed to create app {app_spec.name}: {e}")

        crd = self._mas_to_crd(mas, namespace)

        return crd

    def update_mas_status(self, namespace: str, name: str, request: MASStatusUpdateRequest) -> MultiAgentSystemCRD:
        """Update the status of a MultiAgentSystem CRD (typically called by operator)."""
        existing_crd = self.get_mas_crd(namespace, name)
        if not existing_crd:
            raise ValueError(f"MultiAgentSystem {namespace}/{name} not found")

        # Update status
        existing_crd.status = request.status

        return existing_crd

    def delete_mas_crd(self, namespace: str, name: str) -> None:
        """Delete a MultiAgentSystem CRD by namespace and name."""
        # Convert name to UUID
        mas_id = self._mas_service.get_id_by_name(name, namespace)

        # Look up the MAS CRD
        mas_crd = self.get_mas_crd(namespace, mas_id)
        if not mas_crd or not mas_crd.metadata.uid:
            raise ValueError(f"MultiAgentSystem {namespace}/{name} not found")

        # Delete by UUID
        self._mas_service.delete_mas(mas_crd.metadata.uid)
