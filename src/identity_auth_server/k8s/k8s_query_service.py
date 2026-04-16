import logging
from typing import Optional

from pydantic import BaseModel

from identity_auth_server.core.types import AppType, TokenResponse
from identity_auth_server.k8s.repository import K8sMultiAgentSystemRepository
from identity_auth_server.k8s.types import K8sTokenCache
from identity_auth_server.k8s.view_models import K8sMultiAgentSystemCRDViewModel


logger = logging.getLogger(__name__)


class CacheTokenStoreRequest(BaseModel):
    trace_id: str
    app_host: str
    app_type: AppType
    access_token: str
    tool: Optional[str] = None


class CacheTokenLoadRequest(BaseModel):
    trace_id: str
    app_host: str
    app_type: AppType
    tool: Optional[str] = None


class K8sQueryService:
    def __init__(self, k8s_mas_repository: K8sMultiAgentSystemRepository):
        self._k8s_mas_repository = k8s_mas_repository

    def get_mas_by_app_host(self, namespace: str, app_host: str) -> Optional[K8sMultiAgentSystemCRDViewModel]:
        mas = self._k8s_mas_repository.get_mas_by_app_host(namespace, app_host)
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

    def load_token(self, namespace: str, request: CacheTokenLoadRequest) -> Optional[TokenResponse]:
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
