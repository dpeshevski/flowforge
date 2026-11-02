from typing import Protocol
from uuid import UUID

from flowforge.domain.step_execution import StepExecution


class StepExecutionRepository(Protocol):
    def get_step_execution(self, step_execution_id: UUID) -> StepExecution | None:
        """Get a step execution by its ID."""
        raise NotImplementedError

    def create_step_execution(self, step_execution: StepExecution) -> None:
        """Create a new step execution."""
        raise NotImplementedError
