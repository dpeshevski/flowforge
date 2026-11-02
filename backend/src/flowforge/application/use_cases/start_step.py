from dataclasses import dataclass
from uuid import UUID

from flowforge.application.exceptions import StepExecutionNotFound
from flowforge.application.ports.repositories import StepExecutionRepository
from flowforge.domain.step_execution import StepExecution


@dataclass(frozen=True, kw_only=True)
class StartStepCommand:
    step_execution_id: UUID


class StartStepExecutionUseCase:
    def __init__(self, step_execution_repository: StepExecutionRepository) -> None:
        self.step_execution_repository = step_execution_repository

    def execute(self, command: StartStepCommand) -> StepExecution:
        execution = self.step_execution_repository.get_step_execution(command.step_execution_id)

        if execution is None:
            raise StepExecutionNotFound(
                f"Step execution with ID {command.step_execution_id} not found."
            )

        execution.start()

        self.step_execution_repository.create_step_execution(execution)

        return execution
