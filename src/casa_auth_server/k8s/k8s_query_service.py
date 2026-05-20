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

import json
import logging
from uuid import UUID

from pydantic import BaseModel

from casa_auth_server.core.events import LLMCallEndedEvent, LLMCallStartedEvent
from casa_auth_server.core.types import AppType, TokenResponse
from casa_auth_server.k8s.repository import K8sMultiAgentSystemRepository
from casa_auth_server.k8s.types import K8sLlmCallMapping, K8sTokenCache
from casa_auth_server.k8s.view_models import K8sMultiAgentSystemCRDViewModel
from casa_auth_server.services.authorization_server import AuthorizationServerService
from casa_auth_server.telemetry.tracer import Tracer

logger = logging.getLogger(__name__)


class CacheTokenStoreRequest(BaseModel):
    trace_id: str
    app_host: str
    app_type: AppType
    access_token: str
    tool: str | None = None


class CacheTokenLoadRequest(BaseModel):
    trace_id: str
    app_host: str
    app_type: AppType
    tool: str | None = None


class LlmCallMappingStoreRequest(BaseModel):
    id: str
    trace_id: str
    token: str
    request: str | None = None


class LLMCallEndedKubernetesRequest(BaseModel):
    """Request body for recording the end of an LLM call."""

    call_id: str
    response: str


class K8sQueryService:
    def __init__(
        self,
        k8s_mas_repository: K8sMultiAgentSystemRepository,
        auth_service: AuthorizationServerService,
        tracer: Tracer,
    ):
        self._k8s_mas_repository = k8s_mas_repository
        self._auth_service = auth_service
        self._tracer = tracer

    def get_mas_by_app_host(self, namespace: str, app_host: str) -> K8sMultiAgentSystemCRDViewModel | None:
        mas = self._k8s_mas_repository.get_mas_by_app_host(namespace, app_host)
        if mas is None:
            return None
        return K8sMultiAgentSystemCRDViewModel.model_validate(mas)

    def get_mas_by_workload_name(self, namespace: str, workload_name: str) -> K8sMultiAgentSystemCRDViewModel | None:
        mas = self._k8s_mas_repository.get_mas_by_workload_name(namespace, workload_name)
        if mas is None:
            return None
        return K8sMultiAgentSystemCRDViewModel.model_validate(mas)

    def store_token(self, namespace: str, request: CacheTokenStoreRequest) -> K8sTokenCache:
        token = K8sTokenCache(
            namespace=namespace,
            trace_id=request.trace_id,
            app_host=request.app_host,
            app_type=request.app_type,
            access_token=request.access_token,
            tool=request.tool,
        )
        return self._k8s_mas_repository.store_token(token)

    def load_token(self, namespace: str, request: CacheTokenLoadRequest) -> TokenResponse | None:
        token = self._k8s_mas_repository.load_token(
            namespace=namespace,
            trace_id=request.trace_id,
            app_host=request.app_host,
            app_type=request.app_type,
            tool=request.tool,
        )
        if token is not None:
            return TokenResponse(access_token=token.access_token)
        return None

    def store_llm_call_mapping(self, namespace: str, request: LlmCallMappingStoreRequest) -> K8sLlmCallMapping:
        token = self._auth_service.introspect_token(request.token, None)
        if token is None or not token.active:
            raise Exception("Invalid token.")

        # don't store the whole token, store a reference instead (ID for example)
        call = K8sLlmCallMapping(
            id=UUID(request.id),
            app_id=token.app_id,
            mas_id=token.mas_id,
            namespace=namespace,
            trace_id=request.trace_id,
            user_input_id=token.user_input_id,
            token=request.token,
        )
        mapping = self._k8s_mas_repository.store_llm_call_mapping(call)

        prompt = ""
        tools: str | None = None

        if request.request is not None and request.request != "":
            raw_req = json.loads(request.request)
            prompt = self._get_content_from_litellm_request(raw_req)
            tools = self._get_tools_from_litellm_request(raw_req)

        event = LLMCallStartedEvent(
            app_id=token.app_id,
            call_id=request.id,
            token=request.token,
            user_input_id=token.user_input_id,
            mas_id=token.mas_id,
            prompt=prompt,
            tools=tools,
        )
        self._tracer.record_event(event)

        return mapping

    def load_llm_call_mapping(self, call_id: str) -> K8sLlmCallMapping:
        return self._k8s_mas_repository.load_llm_call_mapping(UUID(call_id))

    def trace_llm_call_end(self, request: LLMCallEndedKubernetesRequest) -> LLMCallEndedEvent:
        """Record the end of an LLM call for the authenticated agent."""
        mapping = self._k8s_mas_repository.load_llm_call_mapping(UUID(request.call_id))
        if mapping is None:
            raise Exception("Invalid call ID")

        tools: str | None = None
        content: str = ""

        if request.response != "":
            resp = json.loads(request.response)
            tools = self._get_tools_from_litellm_response(resp)
            content = self._get_content_from_litellm_response(resp)

        event = LLMCallEndedEvent(
            app_id=str(mapping.app_id),
            call_id=request.call_id,
            token=mapping.token,
            user_input_id=str(mapping.user_input_id),
            mas_id=str(mapping.mas_id),
            response=content,
            tools=tools,
        )

        self._tracer.record_event(event)
        return event

    def _get_content_from_litellm_request(self, request: dict) -> str:
        if "messages" in request and len(request["messages"]) > 0:
            message: dict = request["messages"][0]
            if message.get("content"):
                return message["content"]
        return ""

    def _get_tools_from_litellm_request(self, request: dict) -> str | None:
        if "tools" in request and len(request["tools"]) > 0:
            tools = [f"name='{tool['function']['name']}'" for tool in request["tools"]]
            return json.dumps(tools)
        return None

    def _get_tools_from_litellm_response(self, response: dict) -> str | None:
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice and "tool_calls" in choice["message"]:
                tools = [f"name='{tool['function']['name']}'" for tool in choice["message"]["tool_calls"]]
                return json.dumps(tools)
        return None

    def _get_content_from_litellm_response(self, response: dict) -> str:
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                if content:
                    return content
        return ""
