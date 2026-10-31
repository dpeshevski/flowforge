class DomainError(Exception):
    """Base exception for domain rule violations."""


class InvalidWorkflowTransition(DomainError):
    """Raised when a workflow transition is not allowed."""


class InvalidWorkflowDefinition(DomainError):
    """Raised when a workflow definition is invalid."""
