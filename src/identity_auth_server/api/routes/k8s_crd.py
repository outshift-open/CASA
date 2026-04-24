"""API routes for Kubernetes CRD resources (MultiAgentSystem)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from identity_auth_server.api.dependencies import Container
from identity_auth_server.k8s.k8s_crd_service import K8sCRDService
from identity_auth_server.k8s.k8s_types import (
    MASCreateRequest,
    MultiAgentSystemCRD,
)

router = APIRouter(tags=["Kubernetes CRDs"], prefix="/k8s")


# MultiAgentSystem CRD endpoints


@router.post(
    "/namespaces/{namespace}/mas",
    response_model=MultiAgentSystemCRD,
    generate_unique_id_function=lambda _: "create_mas_crd",
)
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


@router.delete(
    "/namespaces/{namespace}/mas/{name}", status_code=204, generate_unique_id_function=lambda _: "delete_mas_crd"
)
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
