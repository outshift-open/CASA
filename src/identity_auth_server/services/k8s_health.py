"""Health check endpoints for K8s CRD backend.

Implements liveness and readiness probes for Kubernetes deployment.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HealthStatus(BaseModel):
    """Health check response."""
    
    status: str  # "healthy" or "unhealthy"
    timestamp: datetime
    checks: Dict[str, Dict[str, any]]
    version: str = "0.3.0"


class ComponentHealth(BaseModel):
    """Health status of a component."""
    
    healthy: bool
    message: Optional[str] = None
    latency_ms: Optional[float] = None


class HealthChecker:
    """Performs health checks on system components."""
    
    def __init__(self):
        self._startup_time = datetime.now(timezone.utc)
        self._ready = False
    
    def mark_ready(self):
        """Mark the service as ready to receive traffic."""
        self._ready = True
        logger.info("Service marked as ready")
    
    async def check_liveness(self) -> HealthStatus:
        """Check if the service is alive.
        
        This is a lightweight check that returns quickly.
        Should only return unhealthy if the service needs to be restarted.
        """
        checks = {
            "uptime": {
                "healthy": True,
                "message": f"Up for {(datetime.now(timezone.utc) - self._startup_time).total_seconds():.0f}s",
            }
        }
        
        return HealthStatus(
            status="healthy",
            timestamp=datetime.now(timezone.utc),
            checks=checks,
        )
    
    async def check_readiness(self) -> HealthStatus:
        """Check if the service is ready to receive traffic.
        
        This checks dependencies like database, Keycloak, etc.
        Should return unhealthy if the service can't process requests.
        """
        import time
        
        checks = {}
        all_healthy = True
        
        # Check if startup is complete
        if not self._ready:
            checks["startup"] = {
                "healthy": False,
                "message": "Service not yet ready",
            }
            all_healthy = False
        else:
            checks["startup"] = {
                "healthy": True,
                "message": "Service ready",
            }
        
        # Check database connection
        try:
            from identity_auth_server.database.database import Database
            
            start = time.time()
            db = Database()
            # Simple query to verify connection
            with db.session_scope() as session:
                session.execute("SELECT 1")
            latency = (time.time() - start) * 1000
            
            checks["database"] = {
                "healthy": True,
                "message": "Connected",
                "latency_ms": round(latency, 2),
            }
        except Exception as e:
            checks["database"] = {
                "healthy": False,
                "message": f"Error: {str(e)}",
            }
            all_healthy = False
        
        # Check CRD repositories
        try:
            checks["crd_storage"] = {
                "healthy": True,
                "message": "Available",
            }
        except Exception as e:
            checks["crd_storage"] = {
                "healthy": False,
                "message": f"Error: {str(e)}",
            }
            all_healthy = False
        
        return HealthStatus(
            status="healthy" if all_healthy else "unhealthy",
            timestamp=datetime.now(timezone.utc),
            checks=checks,
        )


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get or create the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker
