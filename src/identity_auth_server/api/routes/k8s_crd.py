"""API routes for Kubernetes CRD resources (MultiAgentSystem and ZTAPolicy)."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from identity_auth_server.api.dependencies import Container
from identity_auth_server.k8s.k8s_crd_service import K8sCRDService
from identity_auth_server.k8s.k8s_types import (
    MASCreateRequest,
    MASListResponse,
    MASStatusUpdateRequest,
    MASUpdateRequest,
    MultiAgentSystemCRD,
)

router = APIRouter(tags=["Kubernetes CRDs"], prefix="/k8s")


# MultiAgentSystem CRD endpoints


@router.post("/namespaces/{namespace}/mas", response_model=MultiAgentSystemCRD)
def create_mas_crd(
    namespace: str,
    request: MASCreateRequest,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> MultiAgentSystemCRD:
    """Create a new MultiAgentSystem CRD.

    This endpoint is used by kubectl or Kubernetes operators to create a new
    Multi-Agent System through the CRD API.
    """
    try:
        # Override namespace in metadata if provided in path
        request.metadata.namespace = namespace
        return crd_service.create_mas_from_crd(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/namespaces/{namespace}/mas/{mas_id}", response_model=MultiAgentSystemCRD)
def get_mas_crd(
    namespace: str,
    mas_id: str,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> MultiAgentSystemCRD:
    """Get a MultiAgentSystem CRD by namespace and name."""
    crd = crd_service.get_mas_crd(namespace, mas_id)
    if not crd:
        raise HTTPException(status_code=404, detail=f"MultiAgentSystem {namespace}/{mas_id} not found")
    return crd


@router.get("/namespaces/{namespace}/mas", response_model=MASListResponse)
def list_mas_crds_in_namespace(
    namespace: str,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> MASListResponse:
    """List all MultiAgentSystem CRDs in a specific namespace."""
    items = crd_service.list_mas_crds(namespace=namespace)
    return MASListResponse(api_version="zta.io/v1alpha1", kind="MultiAgentSystemList", items=items)


@router.get("/mas", response_model=MASListResponse)
def list_all_mas_crds(
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
    namespace: Optional[str] = Query(None, description="Filter by namespace"),
) -> MASListResponse:
    """List all MultiAgentSystem CRDs across all namespaces or filtered by namespace."""
    items = crd_service.list_mas_crds(namespace=namespace)
    return MASListResponse(api_version="zta.io/v1alpha1", kind="MultiAgentSystemList", items=items)


@router.put("/namespaces/{namespace}/mas/{name}", response_model=MultiAgentSystemCRD)
def update_mas_crd(
    namespace: str,
    name: str,
    request: MASUpdateRequest,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> MultiAgentSystemCRD:
    """Update a MultiAgentSystem CRD spec."""
    try:
        return crd_service.update_mas_crd(namespace, name, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/namespaces/{namespace}/mas/{name}/status", response_model=MultiAgentSystemCRD)
def update_mas_status(
    namespace: str,
    name: str,
    request: MASStatusUpdateRequest,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> MultiAgentSystemCRD:
    """Update a MultiAgentSystem CRD status (typically called by operator)."""
    try:
        return crd_service.update_mas_status(namespace, name, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/namespaces/{namespace}/mas/{name}", status_code=204)
def delete_mas_crd(
    namespace: str,
    name: str,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> None:
    """Delete a MultiAgentSystem CRD."""
    try:
        crd_service.delete_mas_crd(namespace, name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
