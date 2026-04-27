"""Exception classes for pipelines."""


class PipelineValidationError(Exception):
    """Exception raised when input validation fails in pipelines."""

    def __init__(self, message: str):
        """Initialize the validation error.

        Args:
            message: Human-readable error message describing the validation failure
        """
        self.message = message
        super().__init__(self.message)
