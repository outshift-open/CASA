# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Service layer for managing Kubernetes CRD resources (MultiAgentSystem)."""

import json
import logging
from datetime import UTC, datetime
from urllib.parse import urlparse
from uuid import uuid4

from casa_auth_server.core.idp.idp_client import IdpClient
from casa_auth_server.core.types import App, AppType, MultiAgentSystem, ToolCheckFlags
from casa_auth_server.k8s.k8s_types import (
    AppCredentials,
    AppSpec,
    AppSpecBaseUrl,
    MASCreateRequest,
    MASPhase,
    MultiAgentSystemCRD,
    MultiAgentSystemMetadata,
    MultiAgentSystemSpec,
    MultiAgentSystemStatus,
    ToolCheckType,
)
from casa_auth_server.k8s.repository import K8sMultiAgentSystemRepository
from casa_auth_server.k8s.types import K8sAppSpec, K8sMultiAgentSystemCRD, K8sMultiAgentSystemMetadata
from casa_auth_server.services.app_service import AppRequest, AppService, ToolRequest
from casa_auth_server.services.mas_service import (
    MultiAgentSystemCreateRequest,
    MultiAgentSystemService,
)
from casa_auth_server.services.mcp_discover import McpDiscoverService

logger = logging.getLogger(__name__)


class K8sCRDService:
    """Service for managing Kubernetes CRD resources in the CASA runtime."""

    def __init__(
        self,
        mas_service: MultiAgentSystemService,
        app_service: AppService,
        idp_client: IdpClient,
        k8s_mas_repository: K8sMultiAgentSystemRepository,
        mcp_discover: McpDiscoverService,
    ):
        self._mas_service = mas_service
        self._app_service = app_service
        self._idp_client = idp_client
        self._k8s_mas_repository = k8s_mas_repository
        self._mcp_discover = mcp_discover

    def _convert_tool_checks_to_flags(self, checks: list[ToolCheckType]) -> ToolCheckFlags:
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

    def _convert_flags_to_tool_checks(self, flags: ToolCheckFlags) -> list[ToolCheckType]:
        """Convert ToolCheckFlags to list of tool check types."""
        checks = []
        if flags & ToolCheckFlags.DETERMINISTIC_TOOL_SELECTED:
            checks.append(ToolCheckType.DETERMINISTIC_TOOL_SELECTED)
        if flags & ToolCheckFlags.DETERMINISTIC_LLM_SELECTED_TOOLS:
            checks.append(ToolCheckType.DETERMINISTIC_LLM_SELECTED_TOOLS)
        if flags & ToolCheckFlags.AI_POWERED_TOOL_MATCH:
            checks.append(ToolCheckType.AI_POWERED_TOOL_MATCH)
        return checks

    def _convert_app_type(self, app_type: AppType) -> str:
        """Convert K8s app type to internal app type."""
        return app_type.value

    def _mas_to_crd(self, mas: MultiAgentSystem, namespace: str = "default") -> MultiAgentSystemCRD:
        """Convert internal MAS model to CRD representation."""
        # Get apps for this MAS
        apps = self._app_service.get_mas_apps(str(mas.id))

        # Build app specs
        app_specs = [
            AppSpec(
                name=app.name,
                type=AppType(app.type),
                base_url=AppSpecBaseUrl(host=urlparse(app.base_url).netloc, scheme=urlparse(app.base_url).scheme),
            )
            for app in apps
        ]

        # Build status
        status = MultiAgentSystemStatus(
            phase=MASPhase.ACTIVE,
            apps_ready=len(apps),
            last_sync_time=datetime.now(UTC),
        )

        return MultiAgentSystemCRD(
            api_version="casa.io/v1alpha1",
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

    def _build_k8s_crd_record(
        self,
        mas: MultiAgentSystem,
        k8s_name: str,
        namespace: str,
        workload_names: dict | None = None,
        prompt_field_json_paths: dict | None = None,
        llm_host: str | None = None,
    ) -> K8sMultiAgentSystemCRD:
        """Build K8sMultiAgentSystemCRD SQLModel record linked to an existing MAS."""
        apps = self._app_service.get_mas_apps(str(mas.id))

        crd_id = uuid4()

        metadata = K8sMultiAgentSystemMetadata(
            name=k8s_name,
            uid=str(mas.id),
            mas_crd_id=crd_id,
        )

        app_specs = []
        for app in apps:
            parsed = urlparse(app.base_url)
            app_specs.append(
                K8sAppSpec(
                    name=app.name,
                    type=AppType(app.type),
                    url_host=parsed.netloc,
                    url_scheme=parsed.scheme,
                    app_id=app.id,
                    mas_crd_id=crd_id,
                    kubernetes_workload_name=(workload_names or {}).get(app.name),
                    prompt_field_json_path=(prompt_field_json_paths or {}).get(app.name),
                )
            )

        crd = K8sMultiAgentSystemCRD(
            id=crd_id,
            namespace=namespace,
            name=mas.name,
            enabled_tool_checks=mas.enabled_tool_checks,
            mas_id=mas.id,
            llm_host=llm_host,
        )
        crd.mas_metadata = metadata
        crd.app_specs = app_specs
        return crd

    def _discover_and_register_tools(self, app: App) -> None:
        """Discover tools from an MCP server and persist them. Best-effort: logs and returns on any failure."""
        try:
            mcp_server = self._mcp_discover.discover_mcp_tools(app.base_url)
        except Exception as e:
            logger.warning(f"Tool discovery failed for MCP server {app.base_url}: {e}")
            return

        tool_requests = [
            ToolRequest(
                name=tool.name,
                description=tool.description or "",
                input_schema=json.dumps(tool.inputSchema),
                output_schema=json.dumps(tool.outputSchema) if tool.outputSchema else "{}",
            )
            for tool in mcp_server.tools
        ]

        try:
            self._app_service.update_app(
                str(app.id),
                AppRequest(
                    name=app.name,
                    type=app.type,
                    base_url=app.base_url,
                    mas_id=str(app.mas_id),
                    tools=tool_requests,
                ),
            )
            logger.info(f"Registered {len(tool_requests)} tools for MCP server {app.name}")
        except Exception as e:
            logger.error(f"Failed to persist discovered tools for app {app.id}: {e}")

    def create_mas_from_crd(self, request: MASCreateRequest) -> MultiAgentSystemCRD:
        """Create a new MultiAgentSystem from CRD request (idempotent)."""
        # Check if MAS already exists (by k8s_name and namespace)
        try:
            existing_mas = self._mas_service._mas_repository.get_by_name_and_namespace(
                request.metadata.name, request.metadata.namespace
            )
            logger.info(f"MAS {request.metadata.name} already exists in namespace {request.metadata.namespace}")
            mas = existing_mas

            # Get existing apps
            existing_apps = self._app_service.get_mas_apps(str(mas.id))
            credentials = []

            # Return credentials for existing apps
            for app in existing_apps:
                if app.client_credentials:
                    credentials.append(
                        AppCredentials(
                            app_name=app.name,
                            app_id=str(app.id),
                            client_id=app.client_credentials.client_id,
                            client_secret=app.client_credentials.client_secret or "",
                            secret_name=f"{app.id}-oauth2-credentials",
                        )
                    )

            # Ensure the K8sMultiAgentSystemCRD row exists in DB
            k8s_crd = self._k8s_mas_repository.get_k8s_crd_by_mas_id(mas.id) if mas.id is not None else None
            prompt_field_json_paths = {
                a.name: a.http_request_schema.prompt_field_json_path for a in request.spec.apps if a.http_request_schema
            }
            if k8s_crd is None:
                workload_names = {
                    a.name: a.kubernetes_workload_name for a in request.spec.apps if a.kubernetes_workload_name
                }
                k8s_crd = self._build_k8s_crd_record(
                    mas,
                    request.metadata.name,
                    request.metadata.namespace,
                    workload_names,
                    prompt_field_json_paths,
                    request.spec.llm_host,
                )
                self._k8s_mas_repository.create_mas(k8s_crd)
            else:
                # Update prompt_field_json_path on existing app specs
                for app_spec in k8s_crd.app_specs:
                    if app_spec.name in prompt_field_json_paths:
                        app_spec.prompt_field_json_path = prompt_field_json_paths[app_spec.name]
                        self._k8s_mas_repository.update_app_spec(app_spec)
                # Update llm_host if changed
                if k8s_crd.llm_host != request.spec.llm_host:
                    k8s_crd.llm_host = request.spec.llm_host

            # Build CRD response with existing data
            crd = self._mas_to_crd(mas, namespace=request.metadata.namespace)
            crd.metadata.uid = str(mas.id)
            crd.status = MultiAgentSystemStatus(
                phase=MASPhase.ACTIVE,
                apps_ready=len(existing_apps),
                last_sync_time=datetime.now(UTC),
                message=f"MAS already exists with {len(existing_apps)} apps",
                credentials=credentials if credentials else None,
            )
            return crd

        except Exception:
            # MAS doesn't exist, create it
            logger.info(f"Creating new MAS {request.metadata.name} in namespace {request.metadata.namespace}")
            pass

        # Create new MAS
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
                        base_url=app_spec.base_url.to_url(),
                        mas_id=str(mas.id),
                        type=self._convert_app_type(app_spec.type),
                    )
                )

                created_apps.append(app)

                if app.type == AppType.MCP_SERVER:
                    self._discover_and_register_tools(app)

                # Collect credentials for operator to create K8s secrets
                if app.client_credentials:
                    credentials.append(
                        AppCredentials(
                            app_name=app.name,
                            app_id=str(app.id),
                            client_id=app.client_credentials.client_id,
                            client_secret=app.client_credentials.client_secret or "",
                            secret_name=f"{app.id}-oauth2-credentials",
                        )
                    )
            except Exception as e:
                logger.error(f"Failed to create app {app_spec.name}: {e}")

        # Persist the K8sMultiAgentSystemCRD record (used by k8s_query_service for host-based lookups)
        workload_names = {a.name: a.kubernetes_workload_name for a in request.spec.apps if a.kubernetes_workload_name}
        prompt_field_json_paths = {
            a.name: a.http_request_schema.prompt_field_json_path for a in request.spec.apps if a.http_request_schema
        }
        k8s_crd = self._build_k8s_crd_record(
            mas,
            request.metadata.name,
            request.metadata.namespace,
            workload_names,
            prompt_field_json_paths,
            request.spec.llm_host,
        )
        self._k8s_mas_repository.create_mas(k8s_crd)

        # Build CRD response
        crd = self._mas_to_crd(mas, namespace=request.metadata.namespace)
        crd.metadata.uid = str(mas.id)
        crd.status = MultiAgentSystemStatus(
            phase=MASPhase.ACTIVE if created_apps else MASPhase.FAILED,
            apps_ready=len(created_apps),
            last_sync_time=datetime.now(UTC),
            message=f"Created {len(created_apps)}/{len(request.spec.apps)} apps successfully",
            credentials=credentials if credentials else None,
        )

        return crd

    def delete_mas_crd(self, namespace: str, name: str) -> None:
        """Delete a MultiAgentSystem CRD by namespace and name."""
        mas = self._mas_service.get_mas_by_name(name, namespace)
        if not mas or not mas.id:
            raise ValueError(f"MultiAgentSystem {namespace}/{name} not found")

        mas_crd = self._k8s_mas_repository.get_k8s_crd_by_mas_id(mas.id)
        if mas_crd:
            self._k8s_mas_repository.delete_mas(mas_crd)

        self._mas_service.delete_mas(str(mas.id))
