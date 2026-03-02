"""Service layer for managing Kubernetes CRD resources (MultiAgentSystem and ZTAPolicy)."""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from identity_auth_server.core.idp.idp_client import IdpClient
from identity_auth_server.services.k8s_exceptions import (
    CRDAlreadyExistsError,
    CRDNotFoundError,
    CRDReconciliationError,
    CRDValidationError,
    KeycloakIntegrationError,
)
from identity_auth_server.core.k8s_types import (
    AppSpec,
    AppTypeK8s,
    MASCreateRequest,
    MASPhase,
    MASStatusUpdateRequest,
    MASUpdateRequest,
    MultiAgentSystemCRD,
    MultiAgentSystemMetadata,
    MultiAgentSystemStatus,
    PolicyCreateRequest,
    PolicyStatusUpdateRequest,
    PolicyUpdateRequest,
    ToolCheckType,
    ZTAPolicyCRD,
    ZTAPolicyMetadata,
    ZTAPolicyStatus,
)
from identity_auth_server.core.repositories.app import AppRepository
from identity_auth_server.core.repositories.authorization_server import AuthorizationServerRepository
from identity_auth_server.core.repositories.k8s_crd import (
    K8sMultiAgentSystemCRDRepository,
    K8sZTAPolicyCRDRepository,
)
from identity_auth_server.core.repositories.multi_agent_system import MultiAgentSystemRepository
from identity_auth_server.core.types import App, AppType, AuthorizationServer, MultiAgentSystem, ToolCheckFlags

logger = logging.getLogger(__name__)


class K8sCRDService:
    """Service for managing Kubernetes CRD resources in the ZTA control plane."""

    def __init__(
        self,
        mas_repository: MultiAgentSystemRepository,
        app_repository: AppRepository,
        auth_srv_repository: AuthorizationServerRepository,
        k8s_mas_crd_repository: K8sMultiAgentSystemCRDRepository,
        k8s_policy_crd_repository: K8sZTAPolicyCRDRepository,
        idp_client: IdpClient,
    ):
        self._mas_repository = mas_repository
        self._app_repository = app_repository
        self._auth_srv_repository = auth_srv_repository
        self._k8s_mas_crd_repository = k8s_mas_crd_repository
        self._k8s_policy_crd_repository = k8s_policy_crd_repository
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
        apps = self._app_repository.get_mas_apps(str(mas.id))

        # Build app specs
        app_specs = [
            AppSpec(name=app.name, type=AppTypeK8s(app.type), base_url=app.base_url) for app in apps
        ]

        # Get realm name from authorization server
        realm = mas.authorization_server.realm if mas.authorization_server else f"mas-{mas.id}"

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
            spec={
                "name": mas.name,
                "authorizationServer": realm,
                "enabledToolChecks": self._convert_flags_to_tool_checks(mas.enabled_tool_checks),
                "apps": [
                    {"name": app.name, "type": app.type, "baseUrl": app.base_url}
                    for app in apps
                ],
            },
            status=status,
        )

    def create_mas_from_crd(self, request: MASCreateRequest) -> MultiAgentSystemCRD:
        """Create a new MultiAgentSystem from CRD request."""
        # Generate unique ID
        mas_id = uuid4()

        # Create authorization server
        realm_name = request.spec.authorization_server
        authorization_server = self._auth_srv_repository.create_authorization_server(
            AuthorizationServer(realm=realm_name)
        )

        # Create realm in Keycloak
        try:
            self._idp_client.create_authorization_server(authorization_server)
        except Exception as e:
            logger.error(f"Failed to create Keycloak realm: {e}")
            # Rollback
            self._auth_srv_repository.delete_authorization_server(authorization_server)
            raise

        # Convert tool checks
        tool_check_flags = self._convert_tool_checks_to_flags(request.spec.enabled_tool_checks)

        # Create MAS in database
        mas = MultiAgentSystem(
            id=mas_id,
            name=request.spec.name,
            authorization_server_id=authorization_server.id,
            enabled_tool_checks=tool_check_flags,
        )
        mas = self._mas_repository.create(mas)

        # Create apps
        created_apps = []
        for app_spec in request.spec.apps:
            try:
                # Create client credentials in Keycloak
                client_creds = self._idp_client.create_client(realm_name, app_spec.name)

                # Create app in database
                app = App(
                    id=uuid4(),
                    name=app_spec.name,
                    type=self._convert_app_type(app_spec.type),
                    base_url=app_spec.base_url,
                    mas_id=mas.id,
                )
                app = self._app_repository.create_app(app)

                # Store client credentials
                from identity_auth_server.core.types import ClientCredentials

                creds = ClientCredentials(
                    name=f"{app.name}-credentials",
                    client_id=client_creds["clientId"],
                    client_secret=client_creds.get("clientSecret"),
                    authorization_server_id=authorization_server.id,
                    app_id=app.id,
                )
                self._app_repository.create_client_credentials(creds)

                created_apps.append(app)
            except Exception as e:
                logger.error(f"Failed to create app {app_spec.name}: {e}")
                # Continue with other apps

        # Build CRD response
        crd = self._mas_to_crd(mas, namespace=request.metadata.namespace)
        crd.metadata.uid = str(mas.id)
        crd.status = MultiAgentSystemStatus(
            phase=MASPhase.ACTIVE if created_apps else MASPhase.FAILED,
            apps_ready=len(created_apps),
            last_sync_time=datetime.now(timezone.utc),
            message=f"Created {len(created_apps)}/{len(request.spec.apps)} apps successfully",
        )

        # Cache it
        cache_key = f"{request.metadata.namespace}/{request.metadata.name}"
        self._mas_cache[cache_key] = crd

        return crd

    def get_mas_crd(self, namespace: str, name: str) -> Optional[MultiAgentSystemCRD]:
        """Get a MultiAgentSystem CRD by namespace and name."""
        cache_key = f"{namespace}/{name}"
        if cache_key in self._mas_cache:
            return self._mas_cache[cache_key]

        # Find MAS by name (simplified lookup)
        all_mas = self._mas_repository.get_all()
        for mas in all_mas:
            mas_name_normalized = mas.name.lower().replace(" ", "-")
            if mas_name_normalized == name:
                crd = self._mas_to_crd(mas, namespace)
                self._mas_cache[cache_key] = crd
                return crd

        return None

    def list_mas_crds(self, namespace: Optional[str] = None) -> List[MultiAgentSystemCRD]:
        """List all MultiAgentSystem CRDs, optionally filtered by namespace."""
        all_mas = self._mas_repository.get_all()
        crds = []

        for mas in all_mas:
            # Use default namespace if not specified
            ns = namespace or "default"
            crd = self._mas_to_crd(mas, ns)
            crds.append(crd)

        return crds

    def update_mas_crd(self, namespace: str, name: str, request: MASUpdateRequest) -> MultiAgentSystemCRD:
        """Update a MultiAgentSystem CRD spec."""
        # Find existing MAS
        existing_crd = self.get_mas_crd(namespace, name)
        if not existing_crd:
            raise ValueError(f"MultiAgentSystem {namespace}/{name} not found")

        mas_id = UUID(existing_crd.metadata.uid)
        mas = self._mas_repository.get_by_id(str(mas_id))

        # Update MAS fields
        mas.name = request.spec.name
        mas.enabled_tool_checks = self._convert_tool_checks_to_flags(request.spec.enabled_tool_checks)

        # Update realm if changed
        if request.spec.authorization_server != existing_crd.spec.authorization_server:
            # This is complex - would require realm migration
            logger.warning("Authorization server realm change not yet supported")

        # Update apps - simplified: delete all and recreate
        existing_apps = self._app_repository.get_mas_apps(str(mas_id))
        for app in existing_apps:
            self._app_repository.delete_app(app)

        # Create new apps
        realm_name = mas.authorization_server.realm
        for app_spec in request.spec.apps:
            try:
                client_creds = self._idp_client.create_client(realm_name, app_spec.name)

                app = App(
                    id=uuid4(),
                    name=app_spec.name,
                    type=self._convert_app_type(app_spec.type),
                    base_url=app_spec.base_url,
                    mas_id=mas.id,
                )
                app = self._app_repository.create_app(app)

                from identity_auth_server.core.types import ClientCredentials

                creds = ClientCredentials(
                    name=f"{app.name}-credentials",
                    client_id=client_creds["clientId"],
                    client_secret=client_creds.get("clientSecret"),
                    authorization_server_id=mas.authorization_server_id,
                    app_id=app.id,
                )
                self._app_repository.create_client_credentials(creds)
            except Exception as e:
                logger.error(f"Failed to create app {app_spec.name}: {e}")

        # Update MAS
        mas = self._mas_repository.update(mas)

        # Build updated CRD
        crd = self._mas_to_crd(mas, namespace)

        # Update cache
        cache_key = f"{namespace}/{name}"
        self._mas_cache[cache_key] = crd

        return crd

    def update_mas_status(
        self, namespace: str, name: str, request: MASStatusUpdateRequest
    ) -> MultiAgentSystemCRD:
        """Update the status of a MultiAgentSystem CRD (typically called by operator)."""
        existing_crd = self.get_mas_crd(namespace, name)
        if not existing_crd:
            raise ValueError(f"MultiAgentSystem {namespace}/{name} not found")

        # Update status
        existing_crd.status = request.status

        # Update cache
        cache_key = f"{namespace}/{name}"
        self._mas_cache[cache_key] = existing_crd

        return existing_crd

    def delete_mas_crd(self, namespace: str, name: str) -> None:
        """Delete a MultiAgentSystem CRD."""
        existing_crd = self.get_mas_crd(namespace, name)
        if not existing_crd:
            raise ValueError(f"MultiAgentSystem {namespace}/{name} not found")

        mas_id = UUID(existing_crd.metadata.uid)
        mas = self._mas_repository.get_by_id(str(mas_id))

        # Delete apps
        for app in mas.apps:
            self._app_repository.delete_app(app)

        # Delete authorization server
        if mas.authorization_server:
            self._auth_srv_repository.delete_authorization_server(mas.authorization_server)
            self._idp_client.delete_authorization_server(mas.authorization_server)

        # Delete MAS
        self._mas_repository.delete(mas)

        # Remove from cache
        cache_key = f"{namespace}/{name}"
        self._mas_cache.pop(cache_key, None)

    # ZTAPolicy methods (simplified implementation - policies are stored in cache only)

    def create_policy_crd(self, request: PolicyCreateRequest) -> ZTAPolicyCRD:
        """Create a new ZTAPolicy CRD."""
        policy = ZTAPolicyCRD(
            api_version="zta.io/v1alpha1",
            kind="ZTAPolicy",
            metadata=request.metadata,
            spec=request.spec,
            status=ZTAPolicyStatus(
                phase=MASPhase.PENDING,
                network_policy_applied=False,
                last_sync_time=datetime.now(timezone.utc),
            ),
        )

        # Assign UID if not present
        if not policy.metadata.uid:
            policy.metadata.uid = str(uuid4())

        # Store in cache
        cache_key = f"{request.metadata.namespace}/{request.metadata.name}"
        self._policy_cache[cache_key] = policy

        return policy

    def get_policy_crd(self, namespace: str, name: str) -> Optional[ZTAPolicyCRD]:
        """Get a ZTAPolicy CRD by namespace and name."""
        cache_key = f"{namespace}/{name}"
        return self._policy_cache.get(cache_key)

    def list_policy_crds(self, namespace: Optional[str] = None) -> List[ZTAPolicyCRD]:
        """List all ZTAPolicy CRDs, optionally filtered by namespace."""
        if namespace:
            return [
                policy
                for key, policy in self._policy_cache.items()
                if key.startswith(f"{namespace}/")
            ]
        return list(self._policy_cache.values())

    def update_policy_crd(self, namespace: str, name: str, request: PolicyUpdateRequest) -> ZTAPolicyCRD:
        """Update a ZTAPolicy CRD spec."""
        cache_key = f"{namespace}/{name}"
        existing_policy = self._policy_cache.get(cache_key)

        if not existing_policy:
            raise ValueError(f"ZTAPolicy {namespace}/{name} not found")

        # Update spec
        existing_policy.spec = request.spec

        # Update status
        if existing_policy.status:
            existing_policy.status.last_sync_time = datetime.now(timezone.utc)
            existing_policy.status.phase = MASPhase.PENDING
            existing_policy.status.network_policy_applied = False

        return existing_policy

    def update_policy_status(
        self, namespace: str, name: str, request: PolicyStatusUpdateRequest
    ) -> ZTAPolicyCRD:
        """Update the status of a ZTAPolicy CRD (typically called by operator)."""
        cache_key = f"{namespace}/{name}"
        existing_policy = self._policy_cache.get(cache_key)

        if not existing_policy:
            raise ValueError(f"ZTAPolicy {namespace}/{name} not found")

        # Update status
        existing_policy.status = request.status

        return existing_policy

    def delete_policy_crd(self, namespace: str, name: str) -> None:
        """Delete a ZTAPolicy CRD."""
        cache_key = f"{namespace}/{name}"
        if cache_key not in self._policy_cache:
            raise ValueError(f"ZTAPolicy {namespace}/{name} not found")

        del self._policy_cache[cache_key]
