"""PostgreSQL implementation of AppRepository."""

from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, desc, select

from identity_auth_server.core.types import AppType
from identity_auth_server.k8s.types import K8sAppSpec, K8sMultiAgentSystemCRD, K8sTokenCache


class K8sMultiAgentSystemRepository(ABC):
    """Interface for K8sMultiAgentSystemRepository."""

    @abstractmethod
    def get_mas_by_app_host(self, namespace: str, app_host: str) -> Optional[K8sMultiAgentSystemCRD]:
        """get_mas_by_app_host."""

    @abstractmethod
    def store_token(self, token: K8sTokenCache) -> K8sTokenCache:
        """Store a token in the cache"""

    @abstractmethod
    def load_token(self, namespace: str, trace_id: str, app_host: str, app_type: AppType) -> Optional[K8sTokenCache]:
        """Load a token from the cache"""


class K8sMultiAgentSystemPostgresRepository(K8sMultiAgentSystemRepository):
    """PostgreSQL implementation of K8sMultiAgentSystemRepository."""

    def __init__(self, session: Session):
        """Initialize the repository with a database session."""
        self._session = session

    def get_mas_by_app_host(self, namespace: str, app_host: str) -> Optional[K8sMultiAgentSystemCRD]:
        """Retrieve an app by its ID."""
        try:
            crd = self._session.exec(
                select(K8sMultiAgentSystemCRD)
                .join(K8sAppSpec)
                .where(K8sAppSpec.url_host == app_host)
                .where(K8sMultiAgentSystemCRD.namespace == namespace)
            )
            return crd.first()
        except Exception as e:
            raise Exception(f"Error retrieving MAS with app url '{app_host}': {e}") from e

    def store_token(self, token: K8sTokenCache) -> K8sTokenCache:
        """Store a token in the cache"""
        try:
            self._session.add(token)
            return token
        except Exception as e:
            raise Exception(f"Error storing token: {e}") from e

    def load_token(self, namespace: str, trace_id: str, app_host: str, app_type: AppType) -> Optional[K8sTokenCache]:
        """Load a token from the cache"""
        try:
            token = self._session.exec(
                select(K8sTokenCache)
                .where(K8sTokenCache.namespace == namespace)
                .where(K8sTokenCache.trace_id == trace_id)
                .where(K8sTokenCache.app_host == app_host)
                .where(K8sTokenCache.app_type == app_type)
                .order_by(desc(K8sTokenCache.created_at))
            )
            return token.first()
        except Exception as e:
            raise Exception(f"Error retrieving token: {e}") from e
