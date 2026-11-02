from uuid import uuid4

import pytest

from flowforge.application.exceptions import StepExecutionNotFound
from flowforge.application.use_cases.start_step import StartStepCommand, StartStepExecutionUseCase
from flowforge.domain.retry_policy import RetryPolicy
from flowforge.domain.step_execution import (
    InvalidStepTransition,
    StepExecution,
    StepExecutionStatus,
)
from flowforge.infrastructure.persistence.in_memory import InMemoryStepExecutionRepository


@pytest.fixture
def step_execution_repository() -> InMemoryStepExecutionRepository:
    return InMemoryStepExecutionRepository()


def test_start_step_execution_success(
    step_execution_repository: InMemoryStepExecutionRepository,
) -> None:
    execution = StepExecution(step_id=uuid4(), retry_policy=RetryPolicy())

    step_execution_repository.create_step_execution(execution)

    use_case = StartStepExecutionUseCase(step_execution_repository)

    result = use_case.execute(StartStepCommand(step_execution_id=execution.id))

    assert result.status == StepExecutionStatus.RUNNING
    assert result.attempts == 1

    persisted = step_execution_repository.get_step_execution(execution.id)

    assert persisted is not None
    assert persisted.status == StepExecutionStatus.RUNNING
    assert persisted.attempts == 1


def test_start_step_execution_not_found(
    step_execution_repository: InMemoryStepExecutionRepository,
) -> None:
    use_case = StartStepExecutionUseCase(step_execution_repository)

    with pytest.raises(StepExecutionNotFound):
        use_case.execute(StartStepCommand(step_execution_id=uuid4()))


def test_cannot_start_already_running_step_execution(
    step_execution_repository: InMemoryStepExecutionRepository,
) -> None:
    execution = StepExecution(step_id=uuid4(), retry_policy=RetryPolicy())
    execution.start()

    step_execution_repository.create_step_execution(execution)

    use_case = StartStepExecutionUseCase(step_execution_repository)

    with pytest.raises(InvalidStepTransition):
        use_case.execute(StartStepCommand(step_execution_id=execution.id))

    persisted = step_execution_repository.get_step_execution(execution.id)

    assert persisted is not None
    assert persisted.attempts == 1


def test_cannot_start_step_execution_exceeding_max_attempts(
    step_execution_repository: InMemoryStepExecutionRepository,
) -> None:
    retry_policy = RetryPolicy(max_attempts=1)
    execution = StepExecution(step_id=uuid4(), retry_policy=retry_policy)
    execution.start()

    step_execution_repository.create_step_execution(execution)

    use_case = StartStepExecutionUseCase(step_execution_repository)

    with pytest.raises(InvalidStepTransition):
        use_case.execute(StartStepCommand(step_execution_id=execution.id))

    persisted = step_execution_repository.get_step_execution(execution.id)

    assert persisted is not None
    assert persisted.attempts == 1


def test_step_execution_does_not_share_mutable_state_with_repository(
    step_execution_repository: InMemoryStepExecutionRepository,
) -> None:
    execution = StepExecution(step_id=uuid4(), retry_policy=RetryPolicy())

    step_execution_repository.create_step_execution(execution)

    loaded = step_execution_repository.get_step_execution(execution.id)
    assert loaded is not None

    loaded.start()

    persisted = step_execution_repository.get_step_execution(execution.id)
    assert persisted is not None

    assert persisted.status == StepExecutionStatus.PENDING
    assert persisted.attempts == 0
