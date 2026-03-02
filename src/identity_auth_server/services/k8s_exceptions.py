"""Custom exceptions for K8s CRD service layer."""


class CRDServiceError(Exception):
    """Base exception for K8s CRD service errors."""

    pass


class CRDNotFoundError(CRDServiceError):
    """Raised when a CRD resource is not found."""

    def __init__(self, kind: str, namespace: str, name: str):
        self.kind = kind
        self.namespace = namespace
        self.name = name
        super().__init__(f"{kind} {namespace}/{name} not found")


class CRDAlreadyExistsError(CRDServiceError):
    """Raised when attempting to create a CRD that already exists."""

    def __init__(self, kind: str, namespace: str, name: str):
        self.kind = kind
        self.namespace = namespace
        self.name = name
        super().__init__(f"{kind} {namespace}/{name} already exists")


class CRDValidationError(CRDServiceError):
    """Raised when CRD validation fails."""

    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(f"Validation error{f' on field {field}' if field else ''}: {message}")


class CRDReconciliationError(CRDServiceError):
    """Raised when CRD reconciliation fails."""

    def __init__(self, kind: str, namespace: str, name: str, reason: str):
        self.kind = kind
        self.namespace = namespace
        self.name = name
        self.reason = reason
        super().__init__(f"Failed to reconcile {kind} {namespace}/{name}: {reason}")


class KeycloakIntegrationError(CRDServiceError):
    """Raised when Keycloak integration fails."""

    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        super().__init__(f"Keycloak {operation} failed: {reason}")
