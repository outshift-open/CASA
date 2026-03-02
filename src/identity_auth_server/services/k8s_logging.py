"""Structured logging configuration for K8s CRD operations.

Provides JSON-structured logging for better observability in Kubernetes environments.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add common Kubernetes fields from environment
        import os
        if os.getenv("POD_NAME"):
            log_data["pod_name"] = os.getenv("POD_NAME")
        if os.getenv("POD_NAMESPACE"):
            log_data["pod_namespace"] = os.getenv("POD_NAMESPACE")
        if os.getenv("NODE_NAME"):
            log_data["node_name"] = os.getenv("NODE_NAME")
        
        return json.dumps(log_data)


class CRDOperationLogger:
    """Logger with CRD-specific context."""
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
    
    def log_crd_operation(
        self,
        operation: str,
        kind: str,
        namespace: str,
        name: str,
        level: str = "INFO",
        extra: Optional[Dict[str, Any]] = None,
    ):
        """Log a CRD operation with structured context.
        
        Args:
            operation: Operation type (create, update, delete, etc.)
            kind: CRD kind (MultiAgentSystem, ZTAPolicy)
            namespace: Resource namespace
            name: Resource name
            level: Log level
            extra: Additional fields
        """
        context = {
            "operation": operation,
            "crd_kind": kind,
            "crd_namespace": namespace,
            "crd_name": name,
        }
        
        if extra:
            context.update(extra)
        
        message = f"{operation.upper()} {kind} {namespace}/{name}"
        
        log_func = getattr(self._logger, level.lower())
        log_func(message, extra=context)
    
    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_ip: Optional[str] = None,
    ):
        """Log an API request."""
        context = {
            "http_method": method,
            "http_path": path,
            "http_status": status_code,
            "duration_ms": duration_ms,
        }
        
        if client_ip:
            context["client_ip"] = client_ip
        
        level = "INFO" if status_code < 400 else "WARNING" if status_code < 500 else "ERROR"
        
        message = f"{method} {path} - {status_code} ({duration_ms:.2f}ms)"
        
        log_func = getattr(self._logger, level.lower())
        log_func(message, extra=context)
    
    def log_watch_event(
        self,
        event_type: str,
        kind: str,
        namespace: str,
        name: str,
        resource_version: str,
    ):
        """Log a watch event."""
        context = {
            "event_type": event_type,
            "crd_kind": kind,
            "crd_namespace": namespace,
            "crd_name": name,
            "resource_version": resource_version,
        }
        
        message = f"WATCH {event_type} {kind} {namespace}/{name} (rv={resource_version})"
        self._logger.info(message, extra=context)
    
    def log_db_operation(
        self,
        operation: str,
        table: str,
        duration_ms: float,
        success: bool,
        error: Optional[str] = None,
    ):
        """Log a database operation."""
        context = {
            "db_operation": operation,
            "db_table": table,
            "duration_ms": duration_ms,
            "success": success,
        }
        
        if error:
            context["error"] = error
        
        level = "INFO" if success else "ERROR"
        message = f"DB {operation.upper()} {table} ({duration_ms:.2f}ms) - {'SUCCESS' if success else 'FAILED'}"
        
        log_func = getattr(self._logger, level.lower())
        log_func(message, extra=context)
    
    def log_keycloak_operation(
        self,
        operation: str,
        realm: str,
        duration_ms: float,
        success: bool,
        error: Optional[str] = None,
    ):
        """Log a Keycloak operation."""
        context = {
            "keycloak_operation": operation,
            "keycloak_realm": realm,
            "duration_ms": duration_ms,
            "success": success,
        }
        
        if error:
            context["error"] = error
        
        level = "INFO" if success else "ERROR"
        message = f"KEYCLOAK {operation.upper()} realm={realm} ({duration_ms:.2f}ms) - {'SUCCESS' if success else 'FAILED'}"
        
        log_func = getattr(self._logger, level.lower())
        log_func(message, extra=context)


def configure_structured_logging(level: str = "INFO", json_format: bool = True):
    """Configure structured logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting (recommended for production)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    if json_format:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
    
    root_logger.addHandler(handler)


def get_crd_logger(name: str) -> CRDOperationLogger:
    """Get a CRD operation logger.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        CRDOperationLogger instance
    """
    logger = logging.getLogger(name)
    return CRDOperationLogger(logger)
