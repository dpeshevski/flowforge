from uuid import uuid4

import pytest

from flowforge.domain.retry_policy import RetryPolicy
from flowforge.domain.step_execution import (
    InvalidStepTransition,
    StepExecution,
    StepExecutionStatus,
)


@pytest.fixture
def execution() -> StepExecution:
    return StepExecution(
        step_id=uuid4(), retry_policy=RetryPolicy(max_attempts=3, initial_delay_seconds=2)
    )


def test_step_starts_pending(execution: StepExecution) -> None:
    assert execution.status == StepExecutionStatus.PENDING
    assert execution.attempts == 0


def test_start_increments_attempts(execution: StepExecution) -> None:
    execution.start()

    assert execution.status == StepExecutionStatus.RUNNING
    assert execution.attempts == 1


def test_successful_step(execution: StepExecution) -> None:
    execution.start()
    execution.succeed()

    assert execution.status == StepExecutionStatus.SUCCEEDED


def test_transient_failure_schedules_retry(execution: StepExecution) -> None:
    execution.start()
    execution.fail("HTTP 503", retryable=True)

    assert execution.status == StepExecutionStatus.RETRYING
    assert execution.attempts == 1
    assert execution.retry_delay_seconds == 2


def test_retry_increments_attempts(execution: StepExecution) -> None:
    execution.start()
    execution.fail("HTTP 503", retryable=True)
    execution.start()

    assert execution.attempts == 2
    assert execution.status == StepExecutionStatus.RUNNING


def test_permanent_failure_does_not_retry(execution: StepExecution) -> None:
    execution.start()
    execution.fail("Invalid payload", retryable=False)

    assert execution.status == StepExecutionStatus.FAILED
    assert execution.retry_delay_seconds is None


def test_retry_exhaustion_fails_step(execution: StepExecution) -> None:
    for _ in range(2):
        execution.start()
        execution.fail("HTTP 503", retryable=True)

    execution.start()
    execution.fail("HTTP 503", retryable=True)

    assert execution.attempts == 3
    assert execution.status == StepExecutionStatus.FAILED


def test_completed_step_cannot_restart(execution: StepExecution) -> None:
    execution.start()
    execution.succeed()

    with pytest.raises(InvalidStepTransition):
        execution.start()


def test_cannot_succeed_pending_step(execution: StepExecution) -> None:
    with pytest.raises(InvalidStepTransition):
        execution.succeed()
