"""API routes for Kubernetes CRD resources (MultiAgentSystem and ZTAPolicy)."""

import json
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from identity_auth_server.api.dependencies import Container
from identity_auth_server.services.k8s_watch import WatchEvent, get_watcher
from identity_auth_server.services.k8s_metrics import get_metrics
from identity_auth_server.services.k8s_health import get_health_checker
from identity_auth_server.core.k8s_types import (
    MASCreateRequest,
    MASListResponse,
    MASStatusUpdateRequest,
    MASUpdateRequest,
    MultiAgentSystemCRD,
    PolicyCreateRequest,
    PolicyListResponse,
    PolicyStatusUpdateRequest,
    PolicyUpdateRequest,
    ZTAPolicyCRD,
)
from identity_auth_server.services.k8s_crd_service import K8sCRDService

router = APIRouter(tags=["Kubernetes CRDs"], prefix="/k8s")


# MultiAgentSystem CRD endpoints


@router.post("/namespaces/{namespace}/multiagentsystems", response_model=MultiAgentSystemCRD)
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


@router.get("/namespaces/{namespace}/multiagentsystems/{name}", response_model=MultiAgentSystemCRD)
def get_mas_crd(
    namespace: str,
    name: str,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> MultiAgentSystemCRD:
    """Get a MultiAgentSystem CRD by namespace and name."""
    crd = crd_service.get_mas_crd(namespace, name)
    if not crd:
        raise HTTPException(status_code=404, detail=f"MultiAgentSystem {namespace}/{name} not found")
    return crd


@router.get("/namespaces/{namespace}/multiagentsystems", response_model=MASListResponse)
def list_mas_crds_in_namespace(
    namespace: str,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> MASListResponse:
    """List all MultiAgentSystem CRDs in a specific namespace."""
    items = crd_service.list_mas_crds(namespace=namespace)
    return MASListResponse(api_version="zta.io/v1alpha1", kind="MultiAgentSystemList", items=items)


@router.get("/multiagentsystems", response_model=MASListResponse)
def list_all_mas_crds(
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
    namespace: Optional[str] = Query(None, description="Filter by namespace"),
) -> MASListResponse:
    """List all MultiAgentSystem CRDs across all namespaces or filtered by namespace."""
    items = crd_service.list_mas_crds(namespace=namespace)
    return MASListResponse(api_version="zta.io/v1alpha1", kind="MultiAgentSystemList", items=items)


@router.put("/namespaces/{namespace}/multiagentsystems/{name}", response_model=MultiAgentSystemCRD)
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


@router.patch("/namespaces/{namespace}/multiagentsystems/{name}/status", response_model=MultiAgentSystemCRD)
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


@router.delete("/namespaces/{namespace}/multiagentsystems/{name}", status_code=204)
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


# ZTAPolicy CRD endpoints


@router.post("/namespaces/{namespace}/ztapolicies", response_model=ZTAPolicyCRD)
def create_policy_crd(
    namespace: str,
    request: PolicyCreateRequest,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> ZTAPolicyCRD:
    """Create a new ZTAPolicy CRD.

    This endpoint is used by kubectl or Kubernetes operators to create a new
    Zero Trust policy through the CRD API.
    """
    try:
        # Override namespace in metadata if provided in path
        request.metadata.namespace = namespace
        return crd_service.create_policy_crd(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/namespaces/{namespace}/ztapolicies/{name}", response_model=ZTAPolicyCRD)
def get_policy_crd(
    namespace: str,
    name: str,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> ZTAPolicyCRD:
    """Get a ZTAPolicy CRD by namespace and name."""
    crd = crd_service.get_policy_crd(namespace, name)
    if not crd:
        raise HTTPException(status_code=404, detail=f"ZTAPolicy {namespace}/{name} not found")
    return crd


@router.get("/namespaces/{namespace}/ztapolicies", response_model=PolicyListResponse)
def list_policy_crds_in_namespace(
    namespace: str,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> PolicyListResponse:
    """List all ZTAPolicy CRDs in a specific namespace."""
    items = crd_service.list_policy_crds(namespace=namespace)
    return PolicyListResponse(api_version="zta.io/v1alpha1", kind="ZTAPolicyList", items=items)


@router.get("/ztapolicies", response_model=PolicyListResponse)
def list_all_policy_crds(
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
    namespace: Optional[str] = Query(None, description="Filter by namespace"),
) -> PolicyListResponse:
    """List all ZTAPolicy CRDs across all namespaces or filtered by namespace."""
    items = crd_service.list_policy_crds(namespace=namespace)
    return PolicyListResponse(api_version="zta.io/v1alpha1", kind="ZTAPolicyList", items=items)


@router.put("/namespaces/{namespace}/ztapolicies/{name}", response_model=ZTAPolicyCRD)
def update_policy_crd(
    namespace: str,
    name: str,
    request: PolicyUpdateRequest,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> ZTAPolicyCRD:
    """Update a ZTAPolicy CRD spec."""
    try:
        return crd_service.update_policy_crd(namespace, name, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/namespaces/{namespace}/ztapolicies/{name}/status", response_model=ZTAPolicyCRD)
def update_policy_status(
    namespace: str,
    name: str,
    request: PolicyStatusUpdateRequest,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> ZTAPolicyCRD:
    """Update a ZTAPolicy CRD status (typically called by operator)."""
    try:
        return crd_service.update_policy_status(namespace, name, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/namespaces/{namespace}/ztapolicies/{name}", status_code=204)
def delete_policy_crd(
    namespace: str,
    name: str,
    crd_service: Annotated[K8sCRDService, Depends(Container.get_k8s_crd_service)],
) -> None:
    """Delete a ZTAPolicy CRD."""
    try:
        crd_service.delete_policy_crd(namespace, name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# Watch endpoints for real-time updates


@router.get("/watch/namespaces/{namespace}/multiagentsystems")
async def watch_mas_in_namespace(
    namespace: str,
    resource_version: Optional[str] = Query(None, description="Start watching from this version"),
):
    """Watch MultiAgentSystem CRDs in a specific namespace.
    
    This endpoint streams Server-Sent Events (SSE) for real-time updates.
    Operators can use this to react to CRD changes immediately.
    
    Example:
        curl -N http://localhost:3000/k8s/watch/namespaces/default/multiagentsystems
    """
    watcher = get_watcher()
    
    async def event_stream():
        async for event in watcher.subscribe_mas(namespace=namespace, resource_version=resource_version):
            # Format as SSE
            yield f"data: {event.model_dump_json()}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/watch/multiagentsystems")
async def watch_all_mas(
    resource_version: Optional[str] = Query(None, description="Start watching from this version"),
):
    """Watch all MultiAgentSystem CRDs across all namespaces.
    
    Example:
        curl -N http://localhost:3000/k8s/watch/multiagentsystems
    """
    watcher = get_watcher()
    
    async def event_stream():
        async for event in watcher.subscribe_mas(namespace=None, resource_version=resource_version):
            yield f"data: {event.model_dump_json()}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/watch/namespaces/{namespace}/ztapolicies")
async def watch_policies_in_namespace(
    namespace: str,
    resource_version: Optional[str] = Query(None, description="Start watching from this version"),
):
    """Watch ZTAPolicy CRDs in a specific namespace.
    
    Example:
        curl -N http://localhost:3000/k8s/watch/namespaces/production-mas/ztapolicies
    """
    watcher = get_watcher()
    
    async def event_stream():
        async for event in watcher.subscribe_policy(namespace=namespace, resource_version=resource_version):
            yield f"data: {event.model_dump_json()}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/watch/ztapolicies")
async def watch_all_policies(
    resource_version: Optional[str] = Query(None, description="Start watching from this version"),
):
    """Watch all ZTAPolicy CRDs across all namespaces.
    
    Example:
        curl -N http://localhost:3000/k8s/watch/ztapolicies
    """
    watcher = get_watcher()
    
    async def event_stream():
        async for event in watcher.subscribe_policy(namespace=None, resource_version=resource_version):
            yield f"data: {event.model_dump_json()}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# Health check endpoints


@router.get("/healthz")
async def liveness_probe():
    """Liveness probe endpoint.
    
    Returns 200 if the service is alive and should not be restarted.
    This is a lightweight check.
    
    Example:
        curl http://localhost:3000/k8s/healthz
    """
    health_checker = get_health_checker()
    health_status = await health_checker.check_liveness()
    
    return health_status


@router.get("/readyz")
async def readiness_probe():
    """Readiness probe endpoint.
    
    Returns 200 if the service is ready to receive traffic.
    Checks database connectivity and other dependencies.
    
    Example:
        curl http://localhost:3000/k8s/readyz
    """
    health_checker = get_health_checker()
    health_status = await health_checker.check_readiness()
    
    if health_status.status == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status.model_dump())
    
    return health_status


@router.get("/metrics")
def prometheus_metrics():
    """Prometheus metrics endpoint.
    
    Returns metrics in Prometheus text format for scraping.
    
    Example:
        curl http://localhost:3000/k8s/metrics
    """
    metrics_data, content_type = get_metrics()
    return Response(content=metrics_data, media_type=content_type)
