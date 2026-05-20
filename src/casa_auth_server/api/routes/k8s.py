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

"""API routes for Kubernetes resources."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from casa_auth_server.api.dependencies import Container
from casa_auth_server.core.events import LLMCallEndedEvent
from casa_auth_server.core.types import TokenResponse
from casa_auth_server.k8s.k8s_policy_crd_service import K8sPolicyCRDService
from casa_auth_server.k8s.k8s_query_service import (
    CacheTokenLoadRequest,
    CacheTokenStoreRequest,
    K8sQueryService,
    LLMCallEndedKubernetesRequest,
    LlmCallMappingStoreRequest,
)
from casa_auth_server.k8s.k8s_types import CASAPolicyCRD
from casa_auth_server.k8s.types import K8sLlmCallMapping
from casa_auth_server.k8s.view_models import K8sMultiAgentSystemCRDViewModel

router = APIRouter(tags=["Kubernetes Resources"], prefix="/k8s")


@router.get(
    "/namespaces/{namespace}/get_mas_by_app_host",
    response_model=K8sMultiAgentSystemCRDViewModel,
    generate_unique_id_function=lambda _: "get_k8s_mas_by_app_host",
)
def get_k8s_mas_by_app_host(
    k8s_query_service: Annotated[K8sQueryService, Depends(Container.get_k8s_query_service)],
    namespace: str,
    app_host: str,
) -> K8sMultiAgentSystemCRDViewModel:
    crd = k8s_query_service.get_mas_by_app_host(namespace, app_host)
    if not crd:
        raise HTTPException(status_code=404, detail="MultiAgentSystem not found")
    return crd


@router.get(
    "/namespaces/{namespace}/get_mas_by_app_workload",
    response_model=K8sMultiAgentSystemCRDViewModel,
    generate_unique_id_function=lambda _: "get_k8s_mas_by_app_workload",
)
def get_k8s_mas_by_app_workload(
    k8s_query_service: Annotated[K8sQueryService, Depends(Container.get_k8s_query_service)],
    namespace: str,
    app_workload: str,
) -> K8sMultiAgentSystemCRDViewModel:
    crd = k8s_query_service.get_mas_by_workload_name(namespace, app_workload)
    if not crd:
        raise HTTPException(status_code=404, detail="MultiAgentSystem not found")
    return crd


@router.post("/namespaces/{namespace}/cache/store-token", generate_unique_id_function=lambda _: "cache_store_token")
def store_token(
    k8s_query_service: Annotated[K8sQueryService, Depends(Container.get_k8s_query_service)],
    namespace: str,
    request: CacheTokenStoreRequest,
):
    return k8s_query_service.store_token(namespace, request)


@router.post("/namespaces/{namespace}/cache/load-token", generate_unique_id_function=lambda _: "cache_load_token")
def load_token(
    k8s_query_service: Annotated[K8sQueryService, Depends(Container.get_k8s_query_service)],
    namespace: str,
    request: CacheTokenLoadRequest,
) -> TokenResponse:
    token = k8s_query_service.load_token(namespace, request)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return token


@router.post(
    "/namespaces/{namespace}/cache/store-llm-call-mapping",
    generate_unique_id_function=lambda _: "cache_store_llm_call_mapping",
)
def store_llm_call_mapping(
    k8s_query_service: Annotated[K8sQueryService, Depends(Container.get_k8s_query_service)],
    namespace: str,
    request: LlmCallMappingStoreRequest,
) -> K8sLlmCallMapping:
    call = k8s_query_service.store_llm_call_mapping(namespace, request)
    if not call:
        raise HTTPException(status_code=500, detail="Error storing the LLM call mapping")
    return call


@router.get(
    "/cache/load-llm-call-mapping/{call_id}", generate_unique_id_function=lambda _: "cache_load_llm_call_mapping"
)
def load_llm_call_mapping(
    k8s_query_service: Annotated[K8sQueryService, Depends(Container.get_k8s_query_service)],
    call_id: str,
) -> K8sLlmCallMapping:
    call = k8s_query_service.load_llm_call_mapping(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="LLM call mapping not found")
    return call


# @router.post("/trace/llm/call_start", generate_unique_id_function=lambda _: "trace_llm_call_start")
# def trace_llm_call_start(
#     tracer: Annotated[Tracer, Depends(Container.get_tracer)],
#     auth_server: Annotated[AuthorizationServerService, Depends(Container.get_authorization_service)],
#     jwt: Annotated[HTTPAuthorizationCredentials, Depends(jwt_security)],
#     request: LLMCallStartedRequest,
# ) -> LLMCallStartedEvent:
#     """Record the start of an LLM call for the authenticated agent."""
#     token = auth_server.introspect_token(jwt.credentials)
#     if token is None or not token.active:
#         raise credentials_exception

#     event = LLMCallStartedEvent(
#         app_id=token.app_id,
#         call_id=request.call_id,
#         token=jwt.credentials,
#         user_input_id=token.user_input_id,
#         mas_id=token.mas_id,
#         prompt=request.prompt,
#         tools=request.tools,
#     )

#     tracer.record_event(event)
#     return event


@router.post("/trace/llm/call_end", generate_unique_id_function=lambda _: "k8s_trace_llm_call_end")
def k8s_trace_llm_call_end(
    k8s_query_service: Annotated[K8sQueryService, Depends(Container.get_k8s_query_service)],
    request: LLMCallEndedKubernetesRequest,
) -> LLMCallEndedEvent:
    """Record the end of an LLM call for the authenticated agent."""
    return k8s_query_service.trace_llm_call_end(request)


@router.get(
    "/namespaces/{namespace}/policy-by-workload",
    response_model=CASAPolicyCRD,
    generate_unique_id_function=lambda _: "get_k8s_policy_by_workload",
)
def get_k8s_policy_by_workload(
    policy_service: Annotated[K8sPolicyCRDService, Depends(Container.get_k8s_policy_crd_service)],
    namespace: str,
    workload_name: str,
) -> CASAPolicyCRD:
    """Retrieve a CASAPolicy by the workload it targets.

    Used by the ext-auth sidecar to look up the policy for an inbound workload.
    """
    policy = policy_service.get_policy_by_workload_name(namespace, workload_name)
    if not policy:
        raise HTTPException(status_code=404, detail="CASAPolicy not found")
    return policy
