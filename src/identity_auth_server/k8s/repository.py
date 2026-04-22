"""PostgreSQL implementation of AppRepository."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, delete, desc, select

from identity_auth_server.core.types import AppType
from identity_auth_server.k8s.types import (
    K8sAppSpec,
    K8sLlmCallMapping,
    K8sMultiAgentSystemCRD,
    K8sTokenCache,
)


class K8sMultiAgentSystemRepository(ABC):
    """Interface for K8sMultiAgentSystemRepository."""

    @abstractmethod
    def get_mas_by_app_host(self, namespace: str, app_host: str) -> Optional[K8sMultiAgentSystemCRD]:
        """get_mas_by_app_host."""

    @abstractmethod
    def get_mas_by_workload_name(self, namespace: str, workload_name: str) -> Optional[K8sMultiAgentSystemCRD]:
        """get_mas_by_workload_name."""

    @abstractmethod
    def store_token(self, token: K8sTokenCache) -> K8sTokenCache:
        """Store a token in the cache."""

    @abstractmethod
    def load_token(
        self, namespace: str, trace_id: str, app_host: str, app_type: AppType, tool: Optional[str]
    ) -> Optional[K8sTokenCache]:
        """Load a token from the cache."""

    @abstractmethod
    def create_mas(self, crd: K8sMultiAgentSystemCRD) -> K8sMultiAgentSystemCRD:
        """Persist a new K8sMultiAgentSystemCRD (and its metadata/app_specs) to the database."""

    @abstractmethod
    def get_k8s_crd_by_mas_id(self, mas_id: UUID) -> Optional[K8sMultiAgentSystemCRD]:
        """Retrieve a K8sMultiAgentSystemCRD by its linked MultiAgentSystem id."""

    @abstractmethod
    def update_app_spec(self, app_spec: K8sAppSpec) -> K8sAppSpec:
        """Update an existing K8sAppSpec record."""

    @abstractmethod
    def delete_mas(self, crd: K8sMultiAgentSystemCRD) -> None:
        """Delete a K8sMultiAgentSystemCRD along with its metadata and app specs."""

    @abstractmethod
    def store_llm_call_mapping(self, call: K8sLlmCallMapping) -> K8sLlmCallMapping:
        """Store an LLM call mapping."""

    @abstractmethod
    def load_llm_call_mapping(self, id: UUID) -> K8sLlmCallMapping:
        """Load an LLM call mapping by id."""


class K8sMultiAgentSystemPostgresRepository(K8sMultiAgentSystemRepository):
    """PostgreSQL implementation of K8sMultiAgentSystemRepository."""

    def __init__(self, session: Session):
        """Initialize the repository with a database session."""
        self._session = session

    def get_mas_by_app_host(self, namespace: str, app_host: str) -> Optional[K8sMultiAgentSystemCRD]:
        """Retrieve a MAS by app host."""
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

    def get_mas_by_workload_name(self, namespace: str, workload_name: str) -> Optional[K8sMultiAgentSystemCRD]:
        """Retrieve a MAS by app workload name."""
        try:
            crd = self._session.exec(
                select(K8sMultiAgentSystemCRD)
                .join(K8sAppSpec)
                .where(K8sAppSpec.kubernetes_workload_name == workload_name)
                .where(K8sMultiAgentSystemCRD.namespace == namespace)
            )
            return crd.first()
        except Exception as e:
            raise Exception(f"Error retrieving MAS with app Kubernetes workload name '{workload_name}': {e}") from e

    def store_token(self, token: K8sTokenCache) -> K8sTokenCache:
        """Store a token in the cache."""
        try:
            self._session.add(token)
            return token
        except Exception as e:
            raise Exception(f"Error storing token: {e}") from e

    def load_token(
        self, namespace: str, trace_id: str, app_host: str, app_type: AppType, tool: Optional[str]
    ) -> Optional[K8sTokenCache]:
        """Load a token from the cache."""
        try:
            query = (
                select(K8sTokenCache)
                .where(K8sTokenCache.namespace == namespace)
                .where(K8sTokenCache.trace_id == trace_id)
                .where(K8sTokenCache.app_host == app_host)
                .where(K8sTokenCache.app_type == app_type)
            )
            if tool and tool != "":
                query = query.where(K8sTokenCache.tool == tool)
            token = self._session.exec(query.order_by(desc(K8sTokenCache.created_at)))
            return token.first()
        except Exception as e:
            raise Exception(f"Error retrieving token: {e}") from e

    def create_mas(self, crd: K8sMultiAgentSystemCRD) -> K8sMultiAgentSystemCRD:
        """Create a new K8sMultiAgentSystemCRD (and its metadata/app_specs) in the database."""
        try:
            self._session.add(crd)
            if crd.mas_metadata:
                self._session.add(crd.mas_metadata)
            for app_spec in crd.app_specs:
                self._session.add(app_spec)
            return crd
        except IntegrityError as e:
            raise Exception(f"K8s CRD already exists: {e}") from e
        except Exception as e:
            raise Exception(f"Error creating K8s CRD: {e}") from e

    def get_k8s_crd_by_mas_id(self, mas_id: UUID) -> Optional[K8sMultiAgentSystemCRD]:
        """Retrieve a K8sMultiAgentSystemCRD by its mas_id."""
        try:
            result = self._session.exec(select(K8sMultiAgentSystemCRD).where(K8sMultiAgentSystemCRD.mas_id == mas_id))
            return result.first()
        except Exception as e:
            raise Exception(f"Error retrieving K8s CRD by mas_id '{mas_id}': {e}") from e

    def update_app_spec(self, app_spec: K8sAppSpec) -> K8sAppSpec:
        """Update an existing K8sAppSpec record."""
        try:
            self._session.add(app_spec)
            return app_spec
        except Exception as e:
            raise Exception(f"Error updating K8sAppSpec: {e}") from e

    def delete_mas(self, crd: K8sMultiAgentSystemCRD) -> None:
        """Delete a K8sMultiAgentSystemCRD along with its metadata and app specs."""
        try:
            self._session.exec(delete(K8sAppSpec).where(K8sAppSpec.mas_crd_id == crd.id))
            if crd.mas_metadata:
                self._session.delete(crd.mas_metadata)
            self._session.delete(crd)
        except Exception as e:
            raise Exception(f"Error deleting K8s CRD: {e}") from e

    def store_llm_call_mapping(self, call: K8sLlmCallMapping) -> K8sLlmCallMapping:
        """Store an LLM call mapping."""
        try:
            self._session.add(call)
            return call
        except Exception as e:
            raise Exception(f"Error storing LLM call mapping: {e}") from e

    def load_llm_call_mapping(self, id: UUID) -> K8sLlmCallMapping:
        """Load an LLM call mapping by id."""
        try:
            result = self._session.exec(select(K8sLlmCallMapping).where(K8sLlmCallMapping.id == id))
            return result.first()
        except Exception as e:
            raise Exception(f"Error fetching LLM call mapping by id '{id}': {e}") from e
