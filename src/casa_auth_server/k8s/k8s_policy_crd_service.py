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

"""Service layer for managing Kubernetes CASAPolicy CRD resources."""

import json
import logging
from datetime import UTC, datetime
from uuid import uuid4

from casa_auth_server.k8s.k8s_types import (
    CASAPolicyAllowedEndpoint,
    CASAPolicyCRD,
    CASAPolicyCreateRequest,
    CASAPolicyLlmEndpoint,
    CASAPolicySpec,
    CASAPolicyStatus,
    CASAPolicyTargetRef,
    CRDPhase,
    MultiAgentSystemMetadata,
)
from casa_auth_server.k8s.repository import K8sCASAPolicyRepository
from casa_auth_server.k8s.types import K8sCASAPolicy, K8sCASAPolicyAllowedEndpoint

logger = logging.getLogger(__name__)


class K8sPolicyCRDService:
    """Service for managing Kubernetes CASAPolicy CRD resources."""

    def __init__(self, k8s_policy_repository: K8sCASAPolicyRepository):
        self._repo = k8s_policy_repository

    def _db_to_crd(self, policy: K8sCASAPolicy) -> CASAPolicyCRD:
        """Convert a K8sCASAPolicy DB record to a CASAPolicyCRD Pydantic response."""
        allowed_endpoints = [
            CASAPolicyAllowedEndpoint(name=ep.name, namespace=ep.namespace, port=ep.port)
            for ep in policy.allowed_endpoints
        ]

        llm_endpoint = None
        if policy.llm_endpoint_fqdn is not None and policy.llm_endpoint_port is not None:
            llm_endpoint = CASAPolicyLlmEndpoint(fqdn=policy.llm_endpoint_fqdn, port=policy.llm_endpoint_port)

        spec = CASAPolicySpec(
            targetRef=CASAPolicyTargetRef(kind=policy.target_ref_kind, name=policy.target_ref_name),
            allowedProtocols=json.loads(policy.allowed_protocols),
            allowedEndpoints=allowed_endpoints,
            llmEndpoint=llm_endpoint,
        )

        return CASAPolicyCRD(
            apiVersion="casa.io/v1alpha1",
            kind="CASAPolicy",
            metadata=MultiAgentSystemMetadata(name=policy.name, namespace=policy.namespace),
            spec=spec,
            status=CASAPolicyStatus(
                phase=CRDPhase.ACTIVE,
                last_sync_time=datetime.now(UTC),
                message="Policy active",
            ),
        )

    def create_policy_from_crd(self, request: CASAPolicyCreateRequest) -> CASAPolicyCRD:
        """Create or update a CASAPolicy from a CRD request (idempotent)."""
        namespace = request.metadata.namespace
        name = request.metadata.name

        existing = self._repo.get_policy_by_namespace_and_name(namespace, name)
        if existing is not None:
            logger.info(f"CASAPolicy {namespace}/{name} already exists, updating")
            existing.target_ref_kind = request.spec.target_ref.kind
            existing.target_ref_name = request.spec.target_ref.name
            existing.allowed_protocols = json.dumps(request.spec.allowed_protocols)
            existing.llm_endpoint_fqdn = request.spec.llm_endpoint.fqdn if request.spec.llm_endpoint else None
            existing.llm_endpoint_port = request.spec.llm_endpoint.port if request.spec.llm_endpoint else None
            new_endpoints = [
                K8sCASAPolicyAllowedEndpoint(
                    name=ep.name,
                    namespace=ep.namespace,
                    port=ep.port,
                    policy_id=existing.id,
                )
                for ep in request.spec.allowed_endpoints
            ]
            self._repo.update_policy(existing, new_endpoints)
            return self._db_to_crd(existing)

        logger.info(f"Creating new CASAPolicy {namespace}/{name}")
        policy_id = uuid4()
        allowed_endpoints = [
            K8sCASAPolicyAllowedEndpoint(
                name=ep.name,
                namespace=ep.namespace,
                port=ep.port,
                policy_id=policy_id,
            )
            for ep in request.spec.allowed_endpoints
        ]

        policy = K8sCASAPolicy(
            id=policy_id,
            namespace=namespace,
            name=name,
            target_ref_kind=request.spec.target_ref.kind,
            target_ref_name=request.spec.target_ref.name,
            allowed_protocols=json.dumps(request.spec.allowed_protocols),
            llm_endpoint_fqdn=request.spec.llm_endpoint.fqdn if request.spec.llm_endpoint else None,
            llm_endpoint_port=request.spec.llm_endpoint.port if request.spec.llm_endpoint else None,
        )
        policy.allowed_endpoints = allowed_endpoints

        self._repo.create_policy(policy)
        return self._db_to_crd(policy)

    def delete_policy_crd(self, namespace: str, name: str) -> None:
        """Delete a CASAPolicy by namespace and CR name."""
        policy = self._repo.get_policy_by_namespace_and_name(namespace, name)
        if policy is None:
            raise ValueError(f"CASAPolicy {namespace}/{name} not found")
        self._repo.delete_policy(policy)

    def get_policy_by_workload_name(self, namespace: str, workload_name: str) -> CASAPolicyCRD | None:
        """Retrieve a CASAPolicy by the workload it targets (for sidecar queries)."""
        policy = self._repo.get_policy_by_workload_name(namespace, workload_name)
        if policy is None:
            return None
        return self._db_to_crd(policy)
