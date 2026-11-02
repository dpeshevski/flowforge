from copy import deepcopy
from uuid import UUID

from flowforge.domain.step_execution import StepExecution


class InMemoryStepExecutionRepository:
    def __init__(self):
        self._step_executions: dict[UUID, StepExecution] = {}

    def get_step_execution(self, step_execution_id: UUID) -> StepExecution | None:
        if execution := self._step_executions.get(step_execution_id):
            return deepcopy(execution)

    def create_step_execution(self, step_execution: StepExecution) -> None:
        self._step_executions[step_execution.id] = deepcopy(step_execution)
