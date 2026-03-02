"""Repositories for Kubernetes CRD metadata storage and retrieval."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from identity_auth_server.core.k8s_db_types import K8sMultiAgentSystemCRD, K8sZTAPolicyCRD


class K8sMultiAgentSystemCRDRepository(ABC):
    """Abstract repository for K8s MultiAgentSystem CRD metadata."""

    @abstractmethod
    def create(self, crd: K8sMultiAgentSystemCRD) -> K8sMultiAgentSystemCRD:
        """Create a new CRD metadata record."""
        pass

    @abstractmethod
    def get_by_name_and_namespace(self, name: str, namespace: str) -> Optional[K8sMultiAgentSystemCRD]:
        """Get CRD metadata by name and namespace."""
        pass

    @abstractmethod
    def get_by_uid(self, uid: str) -> Optional[K8sMultiAgentSystemCRD]:
        """Get CRD metadata by Kubernetes UID."""
        pass

    @abstractmethod
    def get_by_mas_id(self, mas_id: UUID) -> Optional[K8sMultiAgentSystemCRD]:
        """Get CRD metadata by internal MAS ID."""
        pass

    @abstractmethod
    def list_all(self) -> List[K8sMultiAgentSystemCRD]:
        """List all CRD metadata records."""
        pass

    @abstractmethod
    def list_by_namespace(self, namespace: str) -> List[K8sMultiAgentSystemCRD]:
        """List CRD metadata records in a specific namespace."""
        pass

    @abstractmethod
    def update(self, crd: K8sMultiAgentSystemCRD) -> K8sMultiAgentSystemCRD:
        """Update CRD metadata."""
        pass

    @abstractmethod
    def delete(self, crd: K8sMultiAgentSystemCRD) -> None:
        """Delete CRD metadata."""
        pass


class K8sMultiAgentSystemCRDPostgresRepository(K8sMultiAgentSystemCRDRepository):
    """PostgreSQL implementation of K8s MultiAgentSystem CRD repository."""

    def __init__(self, session: Session):
        self._session = session

    def create(self, crd: K8sMultiAgentSystemCRD) -> K8sMultiAgentSystemCRD:
        """Create a new CRD metadata record."""
        try:
            self._session.add(crd)
            self._session.flush()
            self._session.refresh(crd)
            return crd
        except Exception as e:
            raise Exception(f"Error creating K8s MAS CRD metadata: {e}") from e

    def get_by_name_and_namespace(self, name: str, namespace: str) -> Optional[K8sMultiAgentSystemCRD]:
        """Get CRD metadata by name and namespace."""
        try:
            statement = select(K8sMultiAgentSystemCRD).where(
                K8sMultiAgentSystemCRD.name == name, K8sMultiAgentSystemCRD.namespace == namespace
            )
            result = self._session.exec(statement)
            return result.first()
        except Exception as e:
            raise Exception(f"Error retrieving K8s MAS CRD metadata: {e}") from e

    def get_by_uid(self, uid: str) -> Optional[K8sMultiAgentSystemCRD]:
        """Get CRD metadata by Kubernetes UID."""
        try:
            statement = select(K8sMultiAgentSystemCRD).where(K8sMultiAgentSystemCRD.uid == uid)
            result = self._session.exec(statement)
            return result.first()
        except Exception as e:
            raise Exception(f"Error retrieving K8s MAS CRD metadata by UID: {e}") from e

    def get_by_mas_id(self, mas_id: UUID) -> Optional[K8sMultiAgentSystemCRD]:
        """Get CRD metadata by internal MAS ID."""
        try:
            statement = select(K8sMultiAgentSystemCRD).where(K8sMultiAgentSystemCRD.mas_id == mas_id)
            result = self._session.exec(statement)
            return result.first()
        except Exception as e:
            raise Exception(f"Error retrieving K8s MAS CRD metadata by MAS ID: {e}") from e

    def list_all(self) -> List[K8sMultiAgentSystemCRD]:
        """List all CRD metadata records."""
        try:
            statement = select(K8sMultiAgentSystemCRD)
            result = self._session.exec(statement)
            return list(result.all())
        except Exception as e:
            raise Exception(f"Error listing K8s MAS CRD metadata: {e}") from e

    def list_by_namespace(self, namespace: str) -> List[K8sMultiAgentSystemCRD]:
        """List CRD metadata records in a specific namespace."""
        try:
            statement = select(K8sMultiAgentSystemCRD).where(K8sMultiAgentSystemCRD.namespace == namespace)
            result = self._session.exec(statement)
            return list(result.all())
        except Exception as e:
            raise Exception(f"Error listing K8s MAS CRD metadata by namespace: {e}") from e

    def update(self, crd: K8sMultiAgentSystemCRD) -> K8sMultiAgentSystemCRD:
        """Update CRD metadata."""
        try:
            self._session.add(crd)
            self._session.flush()
            self._session.refresh(crd)
            return crd
        except Exception as e:
            raise Exception(f"Error updating K8s MAS CRD metadata: {e}") from e

    def delete(self, crd: K8sMultiAgentSystemCRD) -> None:
        """Delete CRD metadata."""
        try:
            self._session.delete(crd)
            self._session.flush()
        except Exception as e:
            raise Exception(f"Error deleting K8s MAS CRD metadata: {e}") from e


class K8sZTAPolicyCRDRepository(ABC):
    """Abstract repository for K8s ZTAPolicy CRD metadata."""

    @abstractmethod
    def create(self, crd: K8sZTAPolicyCRD) -> K8sZTAPolicyCRD:
        """Create a new CRD metadata record."""
        pass

    @abstractmethod
    def get_by_name_and_namespace(self, name: str, namespace: str) -> Optional[K8sZTAPolicyCRD]:
        """Get CRD metadata by name and namespace."""
        pass

    @abstractmethod
    def get_by_uid(self, uid: str) -> Optional[K8sZTAPolicyCRD]:
        """Get CRD metadata by Kubernetes UID."""
        pass

    @abstractmethod
    def list_all(self) -> List[K8sZTAPolicyCRD]:
        """List all CRD metadata records."""
        pass

    @abstractmethod
    def list_by_namespace(self, namespace: str) -> List[K8sZTAPolicyCRD]:
        """List CRD metadata records in a specific namespace."""
        pass

    @abstractmethod
    def update(self, crd: K8sZTAPolicyCRD) -> K8sZTAPolicyCRD:
        """Update CRD metadata."""
        pass

    @abstractmethod
    def delete(self, crd: K8sZTAPolicyCRD) -> None:
        """Delete CRD metadata."""
        pass


class K8sZTAPolicyCRDPostgresRepository(K8sZTAPolicyCRDRepository):
    """PostgreSQL implementation of K8s ZTAPolicy CRD repository."""

    def __init__(self, session: Session):
        self._session = session

    def create(self, crd: K8sZTAPolicyCRD) -> K8sZTAPolicyCRD:
        """Create a new CRD metadata record."""
        try:
            self._session.add(crd)
            self._session.flush()
            self._session.refresh(crd)
            return crd
        except Exception as e:
            raise Exception(f"Error creating K8s ZTAPolicy CRD metadata: {e}") from e

    def get_by_name_and_namespace(self, name: str, namespace: str) -> Optional[K8sZTAPolicyCRD]:
        """Get CRD metadata by name and namespace."""
        try:
            statement = select(K8sZTAPolicyCRD).where(
                K8sZTAPolicyCRD.name == name, K8sZTAPolicyCRD.namespace == namespace
            )
            result = self._session.exec(statement)
            return result.first()
        except Exception as e:
            raise Exception(f"Error retrieving K8s ZTAPolicy CRD metadata: {e}") from e

    def get_by_uid(self, uid: str) -> Optional[K8sZTAPolicyCRD]:
        """Get CRD metadata by Kubernetes UID."""
        try:
            statement = select(K8sZTAPolicyCRD).where(K8sZTAPolicyCRD.uid == uid)
            result = self._session.exec(statement)
            return result.first()
        except Exception as e:
            raise Exception(f"Error retrieving K8s ZTAPolicy CRD metadata by UID: {e}") from e

    def list_all(self) -> List[K8sZTAPolicyCRD]:
        """List all CRD metadata records."""
        try:
            statement = select(K8sZTAPolicyCRD)
            result = self._session.exec(statement)
            return list(result.all())
        except Exception as e:
            raise Exception(f"Error listing K8s ZTAPolicy CRD metadata: {e}") from e

    def list_by_namespace(self, namespace: str) -> List[K8sZTAPolicyCRD]:
        """List CRD metadata records in a specific namespace."""
        try:
            statement = select(K8sZTAPolicyCRD).where(K8sZTAPolicyCRD.namespace == namespace)
            result = self._session.exec(statement)
            return list(result.all())
        except Exception as e:
            raise Exception(f"Error listing K8s ZTAPolicy CRD metadata by namespace: {e}") from e

    def update(self, crd: K8sZTAPolicyCRD) -> K8sZTAPolicyCRD:
        """Update CRD metadata."""
        try:
            self._session.add(crd)
            self._session.flush()
            self._session.refresh(crd)
            return crd
        except Exception as e:
            raise Exception(f"Error updating K8s ZTAPolicy CRD metadata: {e}") from e

    def delete(self, crd: K8sZTAPolicyCRD) -> None:
        """Delete CRD metadata."""
        try:
            self._session.delete(crd)
            self._session.flush()
        except Exception as e:
            raise Exception(f"Error deleting K8s ZTAPolicy CRD metadata: {e}") from e
