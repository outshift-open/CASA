"""Common exception types for the identity auth server domain."""


class ResourceNotFoundError(Exception):
    """Raised when a requested entity cannot be found in the backing store."""


class ResourceAlreadyExistsError(Exception):
    """Raised when attempting to create an entity that violates a uniqueness constraint."""
