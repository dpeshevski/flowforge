class ApplicationError(Exception):
    """Base class for all application errors."""

    pass


class StepExecutionNotFound(ApplicationError):
    """Raised when a step execution is not found."""

    pass
