"""Prometheus metrics for K8s CRD operations.

Exposes metrics for monitoring CRD API performance, resource counts,
and operation success/failure rates.
"""

from prometheus_client import Counter, Gauge, Histogram, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST


# Request metrics
crd_api_requests_total = Counter(
    'zta_crd_api_requests_total',
    'Total number of CRD API requests',
    ['method', 'endpoint', 'status'],
)

crd_api_request_duration_seconds = Histogram(
    'zta_crd_api_request_duration_seconds',
    'Duration of CRD API requests in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# Resource count metrics
multiagentsystem_total = Gauge(
    'zta_multiagentsystems_total',
    'Total number of MultiAgentSystem CRDs',
    ['namespace'],
)

ztapolicy_total = Gauge(
    'zta_ztapolicies_total',
    'Total number of ZTAPolicy CRDs',
    ['namespace'],
)

# Resource status metrics
multiagentsystem_by_phase = Gauge(
    'zta_multiagentsystems_by_phase',
    'Number of MultiAgentSystem CRDs by phase',
    ['namespace', 'phase'],
)

# Watch metrics
watch_subscribers_total = Gauge(
    'zta_watch_subscribers_total',
    'Number of active watch subscribers',
    ['resource_type', 'namespace'],
)

watch_events_sent_total = Counter(
    'zta_watch_events_sent_total',
    'Total number of watch events sent',
    ['resource_type', 'event_type'],
)

# Database operation metrics
db_operations_total = Counter(
    'zta_db_operations_total',
    'Total number of database operations',
    ['operation', 'table', 'status'],
)

db_operation_duration_seconds = Histogram(
    'zta_db_operation_duration_seconds',
    'Duration of database operations in seconds',
    ['operation', 'table'],
    buckets=(0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
)

# Keycloak integration metrics
keycloak_operations_total = Counter(
    'zta_keycloak_operations_total',
    'Total number of Keycloak operations',
    ['operation', 'status'],
)

keycloak_operation_duration_seconds = Histogram(
    'zta_keycloak_operation_duration_seconds',
    'Duration of Keycloak operations in seconds',
    ['operation'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# Error metrics
crd_errors_total = Counter(
    'zta_crd_errors_total',
    'Total number of CRD operation errors',
    ['error_type', 'operation'],
)


class MetricsCollector:
    """Helper class for collecting metrics."""
    
    @staticmethod
    def record_api_request(method: str, endpoint: str, status: int, duration: float):
        """Record an API request."""
        crd_api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status),
        ).inc()
        
        crd_api_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)
    
    @staticmethod
    def update_resource_count(namespace: str, mas_count: int, policy_count: int):
        """Update resource count metrics."""
        multiagentsystem_total.labels(namespace=namespace).set(mas_count)
        ztapolicy_total.labels(namespace=namespace).set(policy_count)
    
    @staticmethod
    def update_mas_phase_count(namespace: str, phase: str, count: int):
        """Update MAS phase count."""
        multiagentsystem_by_phase.labels(
            namespace=namespace,
            phase=phase,
        ).set(count)
    
    @staticmethod
    def update_watch_subscribers(resource_type: str, namespace: str, count: int):
        """Update watch subscriber count."""
        watch_subscribers_total.labels(
            resource_type=resource_type,
            namespace=namespace or "all",
        ).set(count)
    
    @staticmethod
    def record_watch_event(resource_type: str, event_type: str):
        """Record a watch event being sent."""
        watch_events_sent_total.labels(
            resource_type=resource_type,
            event_type=event_type,
        ).inc()
    
    @staticmethod
    def record_db_operation(operation: str, table: str, status: str, duration: float):
        """Record a database operation."""
        db_operations_total.labels(
            operation=operation,
            table=table,
            status=status,
        ).inc()
        
        db_operation_duration_seconds.labels(
            operation=operation,
            table=table,
        ).observe(duration)
    
    @staticmethod
    def record_keycloak_operation(operation: str, status: str, duration: float):
        """Record a Keycloak operation."""
        keycloak_operations_total.labels(
            operation=operation,
            status=status,
        ).inc()
        
        keycloak_operation_duration_seconds.labels(
            operation=operation,
        ).observe(duration)
    
    @staticmethod
    def record_error(error_type: str, operation: str):
        """Record an error."""
        crd_errors_total.labels(
            error_type=error_type,
            operation=operation,
        ).inc()


def get_metrics() -> tuple[bytes, str]:
    """Get Prometheus metrics in text format.
    
    Returns:
        Tuple of (metrics_bytes, content_type)
    """
    return generate_latest(), CONTENT_TYPE_LATEST
